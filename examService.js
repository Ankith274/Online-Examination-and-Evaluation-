// src/services/examService.js - COMPLETE PRODUCTION VERSION
import authService from './authService.js';
import proctorService from './proctorService.js';
import io from 'socket.io-client'; // npm i socket.io-client

class ExamService {
  constructor() {
    this.API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
    this.socket = null;
    this.currentExam = null;
    this.currentExamId = null;
    this.sessionId = null;
    this.answers = new Map(); // examId -> [{questionId, answer, timestamp}]
    this.timerSyncInterval = null;
    this.offlineSyncQueue = []; // Pending API calls
    
    // Protected API (inherits authService.api)
    this.api = authService.api;
    
    // Event callbacks
    this.callbacks = {
      onJoin: [],
      onTimeUpdate: [],
      onViolation: [],
      onQuestionUpdate: [],
      onExamEnd: []
    };
  }

  // ===== EVENT LISTENERS =====
  on(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event].push(callback);
    }
  }

  emit(event, data) {
    this.callbacks[event]?.forEach(cb => cb(data));
  }

  // ===== EXAM CRUD (TEACHER/ADMIN) =====
  async createExam(examData) {
    if (!authService.hasRole('teacher', 'admin')) {
      throw new Error('Only teachers/admins can create exams');
    }

    try {
      const response = await authService.protectedCall({
        method: 'POST',
        url: '/exams',
        data: {
          title: examData.title,
          description: examData.description || '',
          duration: examData.duration, // seconds
          totalQuestions: examData.questions?.length || 0,
          startDate: examData.startDate,
          endDate: examData.endDate,
          maxAttempts: examData.maxAttempts || 1,
          proctoringRequired: examData.proctoringRequired || false,
          questions: examData.questions || [],
          settings: examData.settings || {}
        }
      });

      return response.exam;
    } catch (error) {
      throw new Error(error.message || 'Failed to create exam');
    }
  }

  async getExams(filters = {}) {
    return authService.protectedCall({
      method: 'GET',
      url: '/exams',
      params: {
        role: authService.getRole(),
        status: filters.status, // 'draft', 'published', 'active', 'completed'
        search: filters.search,
        limit: filters.limit || 50,
        page: filters.page || 1,
        category: filters.category
      }
    });
  }

  async getExam(examId) {
    const response = await authService.protectedCall({
      method: 'GET',
      url: `/exams/${examId}?include=questions,results`
    });

    // Cache for offline
    this.currentExam = response;
    this.currentExamId = examId;
    
    // Store locally
    localStorage.setItem(`exam_cache_${examId}`, JSON.stringify(response));
    
    return response;
  }

  async updateExam(examId, updates) {
    if (!authService.hasRole('teacher', 'admin')) {
      throw new Error('Permission denied');
    }

    return authService.protectedCall({
      method: 'PUT',
      url: `/exams/${examId}`,
      data: updates
    });
  }

  async publishExam(examId) {
    return authService.protectedCall({
      method: 'POST',
      url: `/exams/${examId}/publish`
    });
  }

  async deleteExam(examId) {
    return authService.protectedCall({
      method: 'DELETE',
      url: `/exams/${examId}`
    });
  }

  // ===== STUDENT EXAM FLOW =====
  async joinExam(examId, options = {}) {
    if (!authService.isAuthenticated()) {
      throw new Error('Must login to join exam');
    }

    try {
      // Validate access first
      await authService.validateExamAccess(examId);

      const response = await authService.protectedCall({
        method: 'POST',
        url: `/exams/${examId}/join`,
        data: {
          proctoringConsent: options.proctoringConsent !== false,
          deviceInfo: this.getDeviceInfo(),
          userAgent: navigator.userAgent
        }
      });

      this.currentExamId = examId;
      this.sessionId = response.sessionId;
      
      // Init WebSocket
      await this.initWebSocket(examId, response.sessionId);
      
      // Load exam data
      await this.getExam(examId);
      
      // Initialize local answers
      this.answers.set(examId, []);
      localStorage.setItem(`exam_answers_${examId}_${authService.getUserId()}`, '[]');
      
      // Start proctoring if required
      if (response.proctoringRequired && options.proctoringConsent !== false) {
        await proctorService.start(examId);
      }

      this.emit('onJoin', response);
      return response;
    } catch (error) {
      console.error('Join exam failed:', error);
      if (error.response?.status === 409) {
        throw new Error('Exam already started, expired, or max attempts reached');
      }
      if (error.response?.status === 403) {
        throw new Error('No access to this exam');
      }
      throw new Error(error.message || 'Failed to join exam');
    }
  }

  async submitAnswer(examId, questionId, answer) {
    if (this.currentExamId !== examId) {
      throw new Error('Not in active exam session');
    }

    const timestamp = new Date().toISOString();
    
    // Store locally FIRST (offline-first)
    const answers = this.getCurrentAnswers(examId);
    const existingIndex = answers.findIndex(a => a.questionId === questionId);
    
    const answerData = {
      questionId,
      answer: Array.isArray(answer) ? answer : [answer],
      timestamp,
      questionIndex: existingIndex
    };

    if (existingIndex >= 0) {
      answers[existingIndex] = answerData;
    } else {
      answers.push(answerData);
    }

    this.answers.set(examId, answers);
    localStorage.setItem(`exam_answers_${examId}_${authService.getUserId()}`, 
                       JSON.stringify(answers));

    // Queue API call (optimistic update)
    this.queueApiCall('POST', `/exams/${examId}/answers`, answerData);

    return answerData;
  }

  async submitExam(examId) {
    if (this.currentExamId !== examId) {
      throw new Error('Not in active exam');
    }

    const answers = this.getCurrentAnswers(examId);
    if (answers.length === 0) {
      throw new Error('No answers to submit');
    }

    try {
      const response = await authService.protectedCall({
        method: 'POST',
        url: `/exams/${examId}/submit`,
        data: {
          answers,
          sessionId: this.sessionId,
          submitTime: new Date().toISOString()
        }
      });

      // Cleanup
      this.leaveExam();
      
      this.emit('onExamEnd', response);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Submission failed');
    }
  }

  // ===== QUESTIONS MANAGEMENT =====
  async addQuestion(examId, questionData) {
    return authService.protectedCall({
      method: 'POST',
      url: `/exams/${examId}/questions`,
      data: questionData
    });
  }

  async updateQuestion(examId, questionId, updates) {
    return authService.protectedCall({
      method: 'PUT',
      url: `/exams/${examId}/questions/${questionId}`,
      data: updates
    });
  }

  // ===== RESULTS & ANALYTICS =====
  async getResults(examId, filters = {}) {
    return authService.protectedCall({
      method: 'GET',
      url: `/exams/${examId}/results`,
      params: {
        studentId: filters.studentId,
        status: filters.status,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        limit: filters.limit || 100
      }
    });
  }

  async getExamAnalytics(examId) {
    return authService.protectedCall({
      method: 'GET',
      url: `/exams/${examId}/analytics`
    });
  }

  computeScore(answers, questions) {
    let score = 0;
    let total = 0;

    answers.forEach(answer => {
      const question = questions.find(q => q.id === answer.questionId);
      if (!question) return;

      const isCorrect = Array.isArray(answer.answer[0])
        ? answer.answer[0].every(idx => question.correctAnswer.includes(idx))
        : question.correctAnswer.includes(answer.answer[0]);

      total += question.points || 1;
      if (isCorrect) score += question.points || 1;
    });

    return {
      score,
      total,
      percentage: total > 0 ? (score / total) * 100 : 0,
      correct: answers.filter(answer => {
        const question = questions.find(q => q.id === answer.questionId);
        return question && Array.isArray(answer.answer[0])
          ? answer.answer[0].every(idx => question.correctAnswer.includes(idx))
          : question.correctAnswer.includes(answer.answer[0]);
      }).length
    };
  }

  // ===== WEBSOCKET REAL-TIME =====
  async initWebSocket(examId, sessionId) {
    if (this.socket) {
      this.socket.disconnect();
    }

    try {
      this.socket = io(`${this.API_BASE.replace('/api', '')}/exams`, {
        auth: {
          token: authService.getAccessToken(),
          sessionId,
          examId,
          userId: authService.getUserId()
        },
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        timeout: 20000
      });

      this.socket.on('connect', () => {
        console.log('Exam WebSocket connected:', this.socket.id);
      });

      // Server time sync
      this.socket.on('server-time', (serverTime) => {
        this.syncClientTimer(serverTime);
        this.emit('onTimeUpdate', serverTime);
      });

      // Violations from proctoring
      this.socket.on('violation', (violation) => {
        proctorService.flagViolation(violation.type, violation.message);
        this.emit('onViolation', violation);
      });

      // Live question updates (teacher edits)
      this.socket.on('question-update', (question) => {
        this.emit('onQuestionUpdate', question);
      });

      // Exam ending
      this.socket.on('exam-end', (data) => {
        this.leaveExam();
        this.emit('onExamEnd', data);
      });

      // Connection loss warning
      this.socket.on('disconnect', (reason) => {
        console.warn('Exam WebSocket disconnected:', reason);
      });

      // Reconnect
      this.socket.on('reconnect', () => {
        console.log('Exam WebSocket reconnected');
      });

    } catch (error) {
      console.error('WebSocket init failed:', error);
    }
  }

  leaveExam() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }

    if (proctorService.stop) {
      proctorService.stop();
    }

    if (this.timerSyncInterval) {
      clearInterval(this.timerSyncInterval);
    }

    this.currentExamId = null;
    this.sessionId = null;
    this.answers.clear();
    
    // Cleanup localStorage
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('exam_') || key.startsWith('exam_answers_')) {
        localStorage.removeItem(key);
      }
    });
  }

  // ===== TIMER SYNCHRONIZATION =====
  syncClientTimer(serverTime) {
    if (this.timerSyncInterval) {
      clearInterval(this.timerSyncInterval);
    }

    // Adjust client clock
    const offset = Date.now() - serverTime;
    localStorage.setItem('serverTimeOffset', offset.toString());

    // Periodic sync
    this.timerSyncInterval = setInterval(async () => {
      if (this.socket?.connected) {
        this.socket.emit('time-sync-request');
      }
    }, 30000); // 30s
  }

  getServerTime() {
    const offset = parseInt(localStorage.getItem('serverTimeOffset') || '0');
    return Date.now() - offset;
  }

  // ===== OFFLINE SUPPORT =====
  queueApiCall(method, url, data, retries = 3) {
    const call = { method, url, data, retries, timestamp: Date.now() };
    this.offlineSyncQueue.push(call);

    // Try immediately
    this.executeApiCall(call);

    // Retry mechanism
    const retryInterval = setInterval(() => {
      const pending = this.offlineSyncQueue.find(c => c.url === call.url);
      if (pending && navigator.onLine) {
        this.executeApiCall(pending);
      } else if (!navigator.onLine) {
        clearInterval(retryInterval);
      }
    }, 5000);
  }

  async executeApiCall(call) {
    try {
      const response = await this.api({ method: call.method, url: call.url, data: call.data });
      // Remove from queue on success
      const index = this.offlineSyncQueue.indexOf(call);
      if (index > -1) {
        this.offlineSyncQueue.splice(index, 1);
      }
    } catch (error) {
      call.retries--;
      if (call.retries <= 0) {
        console.error('API call failed permanently:', call);
      }
    }
  }

  // ===== UTILITY METHODS =====
  getCurrentAnswers(examId) {
    return this.answers.get(examId) || [];
  }

  getAnsweredCount(examId) {
    return this.getCurrentAnswers(examId).length;
  }

  getDeviceInfo() {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      screen: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      online: navigator.onLine,
      cookieEnabled: navigator.cookieEnabled,
      localStorage: !!window.localStorage
    };
  }

  // ===== PROCTORING INTEGRATION =====
  async startProctoring(examId) {
    if (!authService.hasPermission('proctor:monitor')) {
      throw new Error('Proctoring permission required');
    }

    return authService.protectedCall({
      method: 'POST',
      url: `/proctoring/${examId}/start`
    });
  }

  // ===== EXPORT/IMPORT =====
  exportAnswers(examId) {
    const answers = this.getCurrentAnswers(examId);
    const dataStr = JSON.stringify(answers, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `exam-${examId}-answers.json`;
    link.click();
  }

  // ===== CLEANUP =====
  destroy() {
    this.leaveExam();
    this.answers.clear();
    this.offlineSyncQueue = [];
    this.callbacks = {};
  }
}

// GLOBAL SINGLETON INSTANCE
export const examService = new ExamService();
export default examService;
