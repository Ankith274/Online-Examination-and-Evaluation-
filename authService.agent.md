// src/services/authService.js
import axios from 'axios';
import jwtDecode from 'jwt-decode'; // npm i jwt-decode

class AuthService {
  constructor() {
    this.API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
    this.tokenKey = 'auth_access_token';
    this.refreshKey = 'auth_refresh_token';
    this.roleKey = 'auth_user_role';
    this.userIdKey = 'auth_user_id';
    this.sessionIdKey = 'auth_session_id';
    this.expiryKey = 'auth_token_expiry';
    
    // Axios instance with interceptors
    this.api = axios.create({
      baseURL: this.API_BASE,
      timeout: 15000,
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    });

    // Initialize interceptors
    this.initInterceptors();
    this.initSession();
  }

  // Initialize axios interceptors (token injection + refresh)
  initInterceptors() {
    // Request interceptor: Auto-add token
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token && this.isTokenValid()) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        config.headers['X-Session-ID'] = this.getSessionId();
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor: Handle 401 refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry && this.getRefreshToken()) {
          originalRequest._retry = true;

          try {
            const refreshResponse = await axios.post(`${this.API_BASE}/auth/refresh`, {
              refreshToken: this.getRefreshToken()
            }, { withCredentials: true });

            const { accessToken, refreshToken: newRefreshToken } = refreshResponse.data;
            this.storeTokens(accessToken, newRefreshToken);

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${accessToken}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            this.logout(true);
            window.location.href = '/login?sessionExpired=true';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Session initialization
  initSession() {
    const sessionId = this.getSessionId();
    if (!sessionId) {
      const newSessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem(this.sessionIdKey, newSessionId);
    }
  }

  // ===== CORE AUTH METHODS =====
  async login(credentials) {
    try {
      // Handle OTP flow if required
      if (credentials.otp) {
        const otpResponse = await axios.post(`${this.API_BASE}/auth/otp-verify`, {
          username: credentials.username,
          otp: credentials.otp
        });

        if (!otpResponse.data.valid) {
          throw new Error('Invalid OTP. Please try again.');
        }
      }

      // Main login
      const response = await axios.post(`${this.API_BASE}/auth/login`, {
        username: credentials.username,
        password: credentials.password,
        role: credentials.role || 'student'
      });

      const { accessToken, refreshToken, user } = response.data;
      
      if (!accessToken || !user) {
        throw new Error('Invalid login response');
      }

      this.storeTokens(accessToken, refreshToken);
      this.storeUserData(user);
      
      return { 
        success: true, 
        user,
        token: accessToken,
        expiresIn: this.getTokenExpiry(accessToken)
      };
    } catch (error) {
      const errorMsg = error.response?.data?.message || 
                      (error.message === 'Network Error' ? 'Connection failed' : 'Login failed');
      throw new Error(errorMsg);
    }
  }

  async register(userData, files = {}) {
    const formData = new FormData();
    
    // Append user data
    Object.entries(userData).forEach(([key, value]) => {
      formData.append(key, value);
    });

    // Append files
    Object.entries(files).forEach(([key, file]) => {
      if (file) formData.append(key, file);
    });

    try {
      const response = await axios.post(`${this.API_BASE}/auth/register`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000
      });

      return { 
        success: true, 
        message: response.data.message,
        tempToken: response.data.tempToken 
      };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  }

  async sendOtp(credentials) {
    try {
      const response = await axios.post(`${this.API_BASE}/auth/otp-send`, {
        username: credentials.username,
        email: credentials.email,
        phone: credentials.phone
      });

      return { success: true, message: response.data.message };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'OTP send failed');
    }
  }

  async verifyOtp(credentials) {
    try {
      const response = await axios.post(`${this.API_BASE}/auth/otp-verify`, {
        username: credentials.username,
        otp: credentials.otp
      });

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'OTP verification failed');
    }
  }

  // ===== TOKEN MANAGEMENT =====
  storeTokens(accessToken, refreshToken) {
    localStorage.setItem(this.tokenKey, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.refreshKey, refreshToken);
    }
    
    const decoded = jwtDecode(accessToken);
    localStorage.setItem(this.expiryKey, decoded.exp.toString());
  }

  storeUserData(user) {
    localStorage.setItem(this.roleKey, user.role || 'student');
    localStorage.setItem(this.userIdKey, user.id || user._id);
  }

  getAccessToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshKey);
  }

  getRole() {
    return localStorage.getItem(this.roleKey);
  }

  getUserId() {
    return localStorage.getItem(this.userIdKey);
  }

  getSessionId() {
    return localStorage.getItem(this.sessionIdKey);
  }

  getTokenExpiry(token) {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 - Date.now();
    } catch {
      return 0;
    }
  }

  // ===== VALIDATION =====
  isAuthenticated() {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const decoded = jwtDecode(token);
      const now = Date.now() / 1000;
      return decoded.exp > now + 60; // 1min buffer
    } catch {
      this.clearTokens();
      return false;
    }
  }

  isTokenValid() {
    return this.isAuthenticated();
  }

  // ===== AUTHORIZATION =====
  hasRole(...requiredRoles) {
    if (!this.isAuthenticated()) return false;
    
    const userRole = this.getRole();
    const roleOrder = { admin: 3, teacher: 2, moderator: 2, student: 1 };
    
    const userLevel = roleOrder[userRole] || 0;
    return requiredRoles.some(role => {
      const requiredLevel = roleOrder[role] || 0;
      return userLevel >= requiredLevel;
    });
  }

  hasPermission(permission) {
    try {
      const token = this.getAccessToken();
      const decoded = jwtDecode(token);
      return decoded.permissions?.includes(permission) || false;
    } catch {
      return false;
    }
  }

  // ===== LOGOUT & CLEANUP =====
  logout(force = false) {
    const refreshToken = this.getRefreshToken();
    
    // Revoke session (fire & forget)
    if (refreshToken && !force) {
      axios.post(`${this.API_BASE}/auth/logout`, { 
        refreshToken,
        sessionId: this.getSessionId()
      }).catch(() => {}); // Ignore errors
    }

    // Clear all auth data
    this.clearTokens();
    
    // Clear exam state
    localStorage.removeItem('currentExamId');
    localStorage.removeItem('examAnswers');
    
    // Redirect
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  clearTokens() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshKey);
    localStorage.removeItem(this.roleKey);
    localStorage.removeItem(this.userIdKey);
    localStorage.removeItem(this.sessionIdKey);
    localStorage.removeItem(this.expiryKey);
    
    // Clear axios auth header
    delete this.api.defaults.headers.common['Authorization'];
  }

  // ===== PROTECTED API =====
  async protectedCall(config) {
    if (!this.isAuthenticated()) {
      throw new Error('Authentication required');
    }

    if (!this.hasPermission(config.meta?.permission)) {
      throw new Error('Insufficient permissions');
    }

    try {
      const response = await this.api(config);
      return response.data;
    } catch (error) {
      if (error.response?.status === 403) {
        throw new Error('Access denied');
      }
      if (error.response?.status >= 500) {
        throw new Error('Server error. Please try again.');
      }
      throw error;
    }
  }

  // ===== EXAM-SPECIFIC AUTH =====
  async getProctorToken(examId) {
    if (!this.hasRole('teacher', 'admin')) {
      throw new Error('Proctoring permission required');
    }

    return this.protectedCall({
      method: 'post',
      url: `/exams/${examId}/proctor-token`,
      meta: { permission: 'proctor:access' }
    });
  }

  async validateExamAccess(examId) {
    return this.protectedCall({
      method: 'get',
      url: `/exams/${examId}/access`
    });
  }

  // ===== USER PROFILE =====
  async getProfile() {
    return this.protectedCall({
      method: 'get',
      url: '/profile'
    });
  }

  async updateProfile(updates) {
    return this.protectedCall({
      method: 'put',
      url: '/profile',
      data: updates
    });
  }

  // ===== TOKEN REFRESH =====
  async refreshAccessToken() {
    if (!this.getRefreshToken()) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${this.API_BASE}/auth/refresh`, {
        refreshToken: this.getRefreshToken()
      });

      const { accessToken, refreshToken: newRefresh } = response.data;
      this.storeTokens(accessToken, newRefresh);
      
      return true;
    } catch (error) {
      this.logout(true);
      return false;
    }
  }

  // ===== UTILITIES =====
  getCurrentUser() {
    try {
      const token = this.getAccessToken();
      return token ? jwtDecode(token) : null;
    } catch {
      return null;
    }
  }

  clearAuthCache() {
    this.clearTokens();
  }
}

// Singleton instance (global access)
export const authService = new AuthService();
export default authService;
