import os
import re

url_map = {
    "'login'": "'auth.login'",
    '"login"': '"auth.login"',
    "'register'": "'auth.register'",
    '"register"': '"auth.register"',
    "'logout'": "'auth.logout'",
    '"logout"': '"auth.logout"',
    "'admin_dashboard'": "'admin.admin_dashboard'",
    '"admin_dashboard"': '"admin.admin_dashboard"',
    "'approve_user'": "'admin.approve_user'",
    '"approve_user"': '"admin.approve_user"',
    "'delete_user'": "'admin.delete_user'",
    '"delete_user"': '"admin.delete_user"',
    "'create_subject'": "'admin.create_subject'",
    '"create_subject"': '"admin.create_subject"',
    "'delete_subject'": "'admin.delete_subject'",
    '"delete_subject"': '"admin.delete_subject"',
    "'teacher_dashboard'": "'faculty.teacher_dashboard'",
    '"teacher_dashboard"': '"faculty.teacher_dashboard"',
    "'create_exam'": "'faculty.create_exam'",
    '"create_exam"': '"faculty.create_exam"',
    "'delete_exam'": "'faculty.delete_exam'",
    '"delete_exam"': '"faculty.delete_exam"',
    "'manage_questions'": "'faculty.manage_questions'",
    '"manage_questions"': '"faculty.manage_questions"',
    "'add_question'": "'faculty.add_question'",
    '"add_question"': '"faculty.add_question"',
    "'delete_question'": "'faculty.delete_question'",
    '"delete_question"': '"faculty.delete_question"',
    "'take_exam'": "'exam.take_exam'",
    '"take_exam"': '"exam.take_exam"',
    "'submit_exam'": "'exam.submit_exam'",
    '"submit_exam"': '"exam.submit_exam"',
    "'student_dashboard'": "'student.student_dashboard'",
    '"student_dashboard"': '"student.student_dashboard"',
    "'exam_results'": "'evaluation.exam_results'",
    '"exam_results"': '"evaluation.exam_results"',
    "'view_report'": "'evaluation.view_report'",
    '"view_report"': '"evaluation.view_report"',
    "'download_scorecard'": "'evaluation.download_scorecard'",
    '"download_scorecard"': '"evaluation.download_scorecard"',
    "'export_results_csv'": "'evaluation.export_results_csv'",
    '"export_results_csv"': '"evaluation.export_results_csv"',
    "'log_proctoring'": "'ml.log_proctoring'",
    '"log_proctoring"': '"ml.log_proctoring"',
    "'analyze_frame'": "'ml.analyze_frame'",
    '"analyze_frame"': '"ml.analyze_frame"',
    "'upload_paper'": "'ml.upload_paper'",
    '"upload_paper"': '"ml.upload_paper"',
    "'theory_papers'": "'ml.theory_papers'",
    '"theory_papers"': '"ml.theory_papers"',
    "'view_paper_analysis'": "'ml.view_paper_analysis'",
    '"view_paper_analysis"': '"ml.view_paper_analysis"',
    "'delete_paper'": "'ml.delete_paper'",
    '"delete_paper"': '"ml.delete_paper"'
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old, new in url_map.items():
        if f"url_for({old}" in content or f"url_for( {old}" in content:
            content = content.replace(f"url_for({old}", f"url_for({new}")
            content = content.replace(f"url_for( {old}", f"url_for({new}")
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

if __name__ == '__main__':
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    process_file(os.path.join(root, file))
    
    # Also update the python files we just authored just to be completely sure.
    py_dirs = ['auth', 'admin', 'student', 'faculty', 'exam', 'evaluation', 'ml']
    for d in py_dirs:
        dpath = os.path.join(os.path.dirname(__file__), d)
        if os.path.exists(dpath):
            for root, dirs, files in os.walk(dpath):
                for file in files:
                    if file.endswith('.py'):
                        process_file(os.path.join(root, file))
