const express = require('express');
const session = require('express-session');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const db = new sqlite3.Database('./exam_sys.db');

// Setup App
app.set('view engine', 'ejs');
app.use(express.static('static'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: 'evaluation_secret_key',
    resave: false,
    saveUninitialized: true
}));

// Setup Database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        is_approved BOOLEAN DEFAULT 0,
        registered_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_by INTEGER
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        duration INTEGER,
        subject_id INTEGER,
        teacher_id INTEGER,
        created_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        content TEXT,
        type TEXT,
        options_json TEXT,
        correct_answer TEXT,
        marks INTEGER,
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exam_id INTEGER,
        score INTEGER,
        total_marks INTEGER,
        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Create default admin
    const defaultPassword = bcrypt.hashSync('password', 10);
    db.run(`INSERT OR IGNORE INTO users (username, password, role, is_approved) 
            VALUES ('admin', ?, 'Admin', 1)`, [defaultPassword]);
});

// Middleware for authentication
const requireAuth = (req, res, next) => {
    if (!req.session.userId) return res.redirect('/');
    next();
};

const requireRole = (roles) => (req, res, next) => {
    if (!req.session.userId) return res.redirect('/');
    if (!roles.includes(req.session.role)) return res.redirect('/');
    next();
};

const getCommonLocals = (req) => ({
    username: req.session.username,
    role: req.session.role,
    error: req.session.error,
    success: req.session.success
});

const clearMessages = (req) => {
    req.session.error = null;
    req.session.success = null;
};

// Routes - Authentication
app.get('/', (req, res) => {
    if (req.session.userId) {
        if (req.session.role === 'Admin') return res.redirect('/admin');
        if (req.session.role === 'Teacher') return res.redirect('/teacher');
        if (req.session.role === 'Student') return res.redirect('/student');
    }
    const locals = getCommonLocals(req);
    clearMessages(req);
    res.render('index', locals);
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
        if (!user || !bcrypt.compareSync(password, user.password)) {
            req.session.error = 'Invalid credentials';
            return res.redirect('/');
        }
        if (!user.is_approved) {
            req.session.error = 'Account pending admin approval.';
            return res.redirect('/');
        }
        req.session.userId = user.id;
        req.session.username = user.username;
        req.session.role = user.role;
        res.redirect('/');
    });
});

app.post('/register', (req, res) => {
    const { username, password, role } = req.body;
    const hash = bcrypt.hashSync(password, 10);
    const is_approved = role === 'Admin' ? 1 : 0;

    db.run('INSERT INTO users (username, password, role, is_approved) VALUES (?, ?, ?, ?)',
        [username, hash, role, is_approved], function (err) {
            if (err) {
                req.session.error = 'Username already exists.';
            } else {
                req.session.success = 'Registration successful! Wait for admin approval.';
            }
            res.redirect('/');
        });
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});


// Admin Routes
app.get('/admin', requireRole(['Admin']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    db.serialize(() => {
        db.all('SELECT * FROM users', [], (err, allUsers) => {
            locals.studentCount = allUsers.filter(u => u.role === 'Student').length;
            locals.teacherCount = allUsers.filter(u => u.role === 'Teacher').length;
            locals.pendingUsers = allUsers.filter(u => !u.is_approved);

            db.all('SELECT * FROM subjects', [], (err, subjects) => {
                locals.subjects = subjects;
                locals.subjectCount = subjects.length;
                res.render('admin', locals);
            });
        });
    });
});

app.post('/admin/approve/:id', requireRole(['Admin']), (req, res) => {
    db.run('UPDATE users SET is_approved = 1 WHERE id = ?', [req.params.id], () => {
        req.session.success = 'User approved.';
        res.redirect('/admin');
    });
});

app.post('/admin/reject/:id', requireRole(['Admin']), (req, res) => {
    db.run('DELETE FROM users WHERE id = ?', [req.params.id], () => {
        req.session.success = 'User rejected/deleted.';
        res.redirect('/admin');
    });
});

app.post('/admin/subject', requireRole(['Admin']), (req, res) => {
    db.run('INSERT INTO subjects (name, created_by) VALUES (?, ?)', [req.body.name, req.session.userId], function (err) {
        if (err) req.session.error = 'Subject already exists.';
        else req.session.success = 'Subject added successfully.';
        res.redirect('/admin');
    });
});

app.post('/admin/subject/delete/:id', requireRole(['Admin']), (req, res) => {
    db.run('DELETE FROM subjects WHERE id = ?', [req.params.id], () => {
        req.session.success = 'Subject deleted.';
        res.redirect('/admin');
    });
});

// Teacher Routes
app.get('/teacher', requireRole(['Teacher']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    db.serialize(() => {
        db.all('SELECT * FROM subjects', [], (err, subjects) => {
            db.all(`
                SELECT e.*, s.name as subject_name 
                FROM exams e 
                JOIN subjects s ON e.subject_id = s.id 
                WHERE e.teacher_id = ?
            `, [req.session.userId], (err, exams) => {
                locals.subjects = subjects;
                locals.exams = exams;
                res.render('teacher', locals);
            });
        });
    });
});

app.post('/teacher/exam', requireRole(['Teacher']), (req, res) => {
    const { title, subject_id, duration } = req.body;
    db.run(`INSERT INTO exams (title, duration, subject_id, teacher_id, total_marks) 
            VALUES (?, ?, ?, ?, 0)`,
        [title, duration, subject_id, req.session.userId], () => {
            req.session.success = 'Exam created successfully.';
            res.redirect('/teacher');
        });
});

app.post('/teacher/exam/delete/:id', requireRole(['Teacher']), (req, res) => {
    db.run('DELETE FROM exams WHERE id = ? AND teacher_id = ?', [req.params.id, req.session.userId], () => {
        req.session.success = 'Exam deleted.';
        res.redirect('/teacher');
    });
});

app.get('/teacher/manage_questions/:id', requireRole(['Teacher']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    db.get(`
        SELECT e.*, s.name as subject_name 
        FROM exams e JOIN subjects s ON e.subject_id = s.id 
        WHERE e.id = ? AND e.teacher_id = ?
    `, [req.params.id, req.session.userId], (err, exam) => {
        if (!exam) return res.redirect('/teacher');

        db.all('SELECT * FROM questions WHERE exam_id = ?', [exam.id], (err, questions) => {
            locals.exam = exam;
            locals.questions = questions.map(q => {
                if (q.options_json) q.options = JSON.parse(q.options_json);
                return q;
            });
            res.render('manage_questions', locals);
        });
    });
});

app.post('/teacher/question/:exam_id', requireRole(['Teacher']), (req, res) => {
    const { type, content, marks } = req.body;
    let options_json = null;
    let correct_answer = null;

    if (type === 'MCQ') {
        options_json = JSON.stringify({
            A: req.body.opt_A, B: req.body.opt_B, C: req.body.opt_C, D: req.body.opt_D
        });
        correct_answer = req.body.correct_mcq;
    } else {
        correct_answer = req.body.correct_tf;
    }

    db.run(`INSERT INTO questions (exam_id, content, type, options_json, correct_answer, marks) 
            VALUES (?, ?, ?, ?, ?, ?)`,
        [req.params.exam_id, content, type, options_json, correct_answer, marks], () => {

            // Update exam total marks
            db.run('UPDATE exams SET total_marks = (SELECT SUM(marks) FROM questions WHERE exam_id = ?) WHERE id = ?',
                [req.params.exam_id, req.params.exam_id]);

            req.session.success = 'Question added.';
            res.redirect(`/teacher/manage_questions/${req.params.exam_id}`);
        });
});

app.post('/teacher/question/delete/:exam_id/:id', requireRole(['Teacher']), (req, res) => {
    db.run('DELETE FROM questions WHERE id = ? AND exam_id = ?', [req.params.id, req.params.exam_id], () => {
        // Update exam total marks
        db.run('UPDATE exams SET total_marks = (SELECT SUM(marks) FROM questions WHERE exam_id = ?) WHERE id = ?',
            [req.params.exam_id, req.params.exam_id]);

        req.session.success = 'Question deleted.';
        res.redirect(`/teacher/manage_questions/${req.params.exam_id}`);
    });
});

app.get('/teacher/results/:id', requireRole(['Teacher']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    db.get(`
        SELECT e.*, s.name as subject_name 
        FROM exams e JOIN subjects s ON e.subject_id = s.id 
        WHERE e.id = ? AND e.teacher_id = ?
    `, [req.params.id, req.session.userId], (err, exam) => {
        if (!exam) return res.redirect('/teacher');

        db.get('SELECT COUNT(*) as qCount FROM questions WHERE exam_id = ?', [exam.id], (err, countRow) => {
            exam.qCount = countRow.qCount;
            locals.exam = exam;

            db.all(`
                SELECT r.*, u.username as student_username 
                FROM results r JOIN users u ON r.student_id = u.id 
                WHERE r.exam_id = ?
            `, [exam.id], (err, results) => {
                locals.results = results;
                res.render('results', locals);
            });
        });
    });
});

// Student Routes
app.get('/student', requireRole(['Student']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    db.all(`
        SELECT r.*, e.title as exam_title, s.name as subject_name
        FROM results r 
        JOIN exams e ON r.exam_id = e.id 
        JOIN subjects s ON e.subject_id = s.id 
        WHERE r.student_id = ?
    `, [req.session.userId], (err, results) => {
        locals.results = results;

        // Find exams not yet taken
        const takenIds = results.map(r => r.exam_id);
        const placeholders = takenIds.map(() => '?').join(',');
        const query = takenIds.length > 0
            ? `SELECT e.*, s.name as subject_name, (SELECT COUNT(*) FROM questions q WHERE q.exam_id = e.id) as qCount 
               FROM exams e JOIN subjects s ON e.subject_id = s.id WHERE e.id NOT IN (${placeholders})`
            : `SELECT e.*, s.name as subject_name, (SELECT COUNT(*) FROM questions q WHERE q.exam_id = e.id) as qCount 
               FROM exams e JOIN subjects s ON e.subject_id = s.id`;

        db.all(query, takenIds, (err, availableExams) => {
            locals.availableExams = availableExams;
            res.render('student', locals);
        });
    });
});

app.get('/student/take_exam/:id', requireRole(['Student']), (req, res) => {
    const locals = getCommonLocals(req);
    clearMessages(req);

    // Check if already taken
    db.get('SELECT * FROM results WHERE student_id = ? AND exam_id = ?', [req.session.userId, req.params.id], (err, row) => {
        if (row) {
            req.session.error = 'You have already taken this exam.';
            return res.redirect('/student');
        }

        db.get(`
            SELECT e.*, s.name as subject_name 
            FROM exams e JOIN subjects s ON e.subject_id = s.id 
            WHERE e.id = ?
        `, [req.params.id], (err, exam) => {
            if (!exam) return res.redirect('/student');

            db.all('SELECT * FROM questions WHERE exam_id = ?', [exam.id], (err, questions) => {
                if (questions.length === 0) {
                    req.session.error = 'Exam has no questions yet.';
                    return res.redirect('/student');
                }

                locals.exam = exam;
                locals.questions = questions.map(q => {
                    if (q.options_json) q.options = JSON.parse(q.options_json);
                    return q;
                });
                res.render('take_exam', locals);
            });
        });
    });
});

app.post('/student/submit_exam/:id', requireRole(['Student']), (req, res) => {
    db.get('SELECT * FROM results WHERE student_id = ? AND exam_id = ?', [req.session.userId, req.params.id], (err, row) => {
        if (row) return res.redirect('/student'); // Already taken

        db.all('SELECT * FROM questions WHERE exam_id = ?', [req.params.id], (err, questions) => {
            let score = 0;
            let total_marks = 0;

            questions.forEach(q => {
                total_marks += q.marks;
                const studentAnswer = req.body[`q_${q.id}`];
                if (studentAnswer && studentAnswer === q.correct_answer) {
                    score += q.marks;
                }
            });

            db.run(`INSERT INTO results (student_id, exam_id, score, total_marks) 
                    VALUES (?, ?, ?, ?)`,
                [req.session.userId, req.params.id, score, total_marks], () => {

                    req.session.success = `Exam submitted automatically! You scored ${score} out of ${total_marks}.`;
                    res.redirect('/student');
                });
        });
    });
});


const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Node Server running on http://127.0.0.1:${PORT}`);
});
