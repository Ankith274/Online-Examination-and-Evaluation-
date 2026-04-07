from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'Admin', 'Teacher', 'Student'
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False) 
    
    # Student specific
    roll_no = db.Column(db.String(50), unique=True, nullable=True)
    course = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(20), nullable=True)
    
    # Faculty specific
    department = db.Column(db.String(100), nullable=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    duration = db.Column(db.Integer, nullable=False) # In minutes
    total_marks = db.Column(db.Integer, nullable=False, default=0)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref=db.backref('exams', lazy=True))
    teacher = db.relationship('User', backref=db.backref('exams_created', lazy=True))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'MCQ', 'TF', 'Descriptive'
    content = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True) # Stored as JSON string
    correct_answer = db.Column(db.Text, nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=1)
    difficulty = db.Column(db.String(50), default='Medium') # 'Easy', 'Medium', 'Hard'

    exam = db.relationship('Exam', backref=db.backref('questions', lazy=True, cascade='all, delete-orphan'))

class Answer(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    submitted_answer = db.Column(db.Text, nullable=True)
    marks_awarded = db.Column(db.Float, default=0.0)

    student = db.relationship('User', backref=db.backref('answers', lazy=True))
    exam = db.relationship('Exam', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Completed')
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ML Prediction fields
    predicted_at_risk = db.Column(db.Boolean, default=False)
    risk_confidence = db.Column(db.Float, default=0.0)

    student = db.relationship('User', backref=db.backref('results', lazy=True))
    exam = db.relationship('Exam', backref=db.backref('results', lazy=True))

class StudentResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    ml_score = db.Column(db.Float, default=None) # Used for smart evaluation of descriptive answers

    result = db.relationship('Result', backref=db.backref('responses', lazy=True, cascade='all, delete-orphan'))
    question = db.relationship('Question', backref=db.backref('responses', lazy=True))

class ProctoringLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False) # 'Face Lost', 'Suspicious Behavior', 'Tab Switch'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confidence = db.Column(db.Float, default=1.0)
    details = db.Column(db.Text, nullable=True)
    result = db.relationship('Result', backref=db.backref('proctoring_logs', lazy=True, cascade='all, delete-orphan'))

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(250), nullable=False) # e.g., 'Login', 'Exam Created'
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))


class TheoryPaper(db.Model):
    """Uploaded theory question paper with ML analysis results."""
    id              = db.Column(db.Integer, primary_key=True)
    filename        = db.Column(db.String(300), nullable=False)          # original filename
    filepath        = db.Column(db.String(500), nullable=False)          # server path
    subject_id      = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    uploaded_by     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at     = db.Column(db.DateTime, default=datetime.utcnow)
    exam_type       = db.Column(db.String(50), default='General')        # Internal/External/Midterm/Final
    semester        = db.Column(db.String(50), nullable=True)            # e.g. 'Sem 3'

    # ML Output fields (stored as JSON strings)
    ocr_text        = db.Column(db.Text, nullable=True)                  # Model 1 – extracted text
    ocr_method      = db.Column(db.String(100), nullable=True)           # PyMuPDF / Tesseract
    classification  = db.Column(db.Text, nullable=True)                  # Model 2 – JSON
    is_duplicate    = db.Column(db.Boolean, default=False)               # Model 3
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey('theory_paper.id'), nullable=True)  # Model 3
    similarity_data = db.Column(db.Text, nullable=True)                  # Model 3+4 – JSON
    difficulty_data = db.Column(db.Text, nullable=True)                  # Model 5 – JSON
    error_flags     = db.Column(db.Text, nullable=True)                  # Model 6 – JSON
    keywords        = db.Column(db.Text, nullable=True)                  # Model 7 – JSON
    ml_status       = db.Column(db.String(20), default='Pending')        # Pending/Processed/Error

    # Relationships
    subject   = db.relationship('Subject', backref=db.backref('theory_papers', lazy=True))
    uploader  = db.relationship('User',    backref=db.backref('uploaded_papers', lazy=True))
    duplicate_original = db.relationship('TheoryPaper', remote_side=[id], foreign_keys=[duplicate_of_id])
