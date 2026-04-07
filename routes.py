from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Exam, Question, Result, StudentResponse, AuditLog
from datetime import datetime
import json

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/take_exam/<int:exam_id>', methods=['GET'])
@login_required
def take_exam(exam_id):
    if current_user.role != 'Student':
        return redirect(url_for('index'))
    
    existing_result = Result.query.filter_by(student_id=current_user.id, exam_id=exam_id).first()
    if existing_result and existing_result.status == 'Completed':
        flash('You have already taken this exam.', 'warning')
        return redirect(url_for('student.student_dashboard'))
    
    if not existing_result:
        exam = Exam.query.get_or_404(exam_id)
        existing_result = Result(student_id=current_user.id, exam_id=exam_id, score=0, total_marks=exam.total_marks, status='In Progress')
        db.session.add(existing_result)
        db.session.commit()
    
    exam = Exam.query.get_or_404(exam_id)
    for q in exam.questions:
        if q.options:
            q.parsed_options = json.loads(q.options)
    return render_template('take_exam.html', exam=exam, result_id=existing_result.id)

@exam_bp.route('/submit_exam/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    if current_user.role != 'Student':
        return redirect(url_for('index'))
        
    result = Result.query.filter_by(student_id=current_user.id, exam_id=exam_id, status='In Progress').first()
    if not result:
        flash('Exam session not found or already submitted.', 'warning')
        return redirect(url_for('student.student_dashboard'))
        
    exam = Exam.query.get_or_404(exam_id)
    score = 0
    
    for q in exam.questions:
        student_answer = request.form.get(f'q_{q.id}')
        is_correct = False
        if student_answer and student_answer == q.correct_answer:
            score += q.marks
            is_correct = True
        
        # Save individual response
        resp = StudentResponse(result_id=result.id, question_id=q.id, 
                               selected_answer=student_answer, is_correct=is_correct)
        db.session.add(resp)
            
    result.score = score
    result.status = 'Completed'
    result.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Exam submitted successfully! You scored {score} out of {result.total_marks}.', 'success')
    return redirect(url_for('student.student_dashboard'))

@exam_bp.route('/api/get_questions/<int:exam_id>')
@login_required
def get_questions(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    questions_list = []
    for q in exam.questions:
        questions_list.append({
            'id': q.id,
            'content': q.content,
            'type': q.type,
            'marks': q.marks,
            'difficulty': q.difficulty
        })
    return jsonify(questions_list)
