import os
import json
from app import app
from models import db, User, Subject, Exam, Question

def seed_data():
    with app.app_context():
        # Create subjects
        subjects_data = ["Operating System (OS)", "Machine Learning (ML)", "DATABASE (DBMS)", "DATA SCIENCE"]
        subject_objs = {}
        
        # Get admin user for 'created_by'
        admin = User.query.filter_by(role='Admin').first()
        if not admin:
            print("No admin user found. Please run app.py first to create the default admin.")
            return

        for name in subjects_data:
            subj = Subject.query.filter_by(name=name).first()
            if not subj:
                subj = Subject(name=name, created_by=admin.id)
                db.session.add(subj)
                db.session.commit()
                print(f"Created subject: {name}")
            subject_objs[name] = subj

        # MCQ Data from user
        mcqs = {
            "Operating System (OS)": [
                ("What is the brain of the computer?", ["RAM", "CPU", "Hard Disk", "OS"], "B"),
                ("Which is not an OS?", ["Windows", "Linux", "Oracle", "macOS"], "C"),
                ("Process is:", ["Program in execution", "File", "Data", "Memory"], "A"),
                ("Which scheduling is non-preemptive?", ["Round Robin", "FCFS", "Priority", "Multilevel"], "B"),
                ("Deadlock occurs when:", ["Resources are free", "Circular wait exists", "CPU idle", "No process"], "B"),
                ("Paging is used for:", ["Security", "Memory management", "I/O", "File"], "B"),
                ("Context switching means:", ["Restart system", "Switching CPU between processes", "Delete process", "None"], "B"),
                ("Virtual memory uses:", ["RAM", "Cache", "Hard disk", "Register"], "C"),
                ("Thread is:", ["Heavy process", "Lightweight process", "File", "CPU"], "B"),
                ("Which is system call?", ["printf", "fork()", "main()", "return"], "B"),
                ("Kernel is:", ["Hardware", "OS core", "Software app", "Virus"], "B"),
                ("Which is not scheduling?", ["FCFS", "SJF", "FIFO", "HTTP"], "D"),
                ("Semaphore is used for:", ["Storage", "Synchronization", "Security", "File"], "B"),
                ("Starvation means:", ["CPU failure", "Process waits indefinitely", "Memory full", "Disk error"], "B"),
                ("Thrashing occurs due to:", ["Low CPU", "Excess paging", "High disk", "Virus"], "B")
            ],
            "Machine Learning (ML)": [
                ("ML stands for:", ["Machine Logic", "Machine Learning", "Memory Learning", "Model Learning"], "B"),
                ("Supervised learning uses:", ["No labels", "Labeled data", "Random data", "Images only"], "B"),
                ("Unsupervised learning is used for:", ["Classification", "Clustering", "Regression", "Testing"], "B"),
                ("Overfitting means:", ["Poor model", "Fits training too well", "No training", "Random"], "B"),
                ("Regression predicts:", ["Class", "Number", "Image", "Label"], "B"),
                ("Classification predicts:", ["Continuous", "Categories", "Noise", "Size"], "B"),
                ("K-Means is:", ["Regression", "Clustering", "Classification", "Sorting"], "B"),
                ("Accuracy means:", ["Error", "Correct predictions ratio", "Data size", "Speed"], "B"),
                ("Precision is:", ["Correct positives", "Total data", "Errors", "Labels"], "A"),
                ("Recall is:", ["Memory", "True positive rate", "Accuracy", "Output"], "B"),
                ("Confusion matrix shows:", ["Graph", "Model performance", "Data", "Input"], "B"),
                ("Neural network inspired by:", ["Brain", "CPU", "RAM", "Disk"], "A"),
                ("Feature is:", ["Output", "Input variable", "Model", "Result"], "B"),
                ("Training data is used to:", ["Test", "Train model", "Delete", "Store"], "B"),
                ("Cross-validation improves:", ["Speed", "Accuracy", "Size", "Storage"], "B")
            ],
            "DATABASE (DBMS)": [
                ("DBMS stands for:", ["Data Base Management System", "Data Backup", "Disk Manager", "Data Model"], "A"),
                ("Primary key is:", ["Duplicate", "Unique identifier", "Null", "Random"], "B"),
                ("Foreign key is:", ["Primary key", "Reference key", "Duplicate", "Index"], "B"),
                ("SQL is used for:", ["Programming", "Query database", "OS", "Network"], "B"),
                ("DDL includes:", ["SELECT", "INSERT", "CREATE", "DELETE"], "C"),
                ("DML includes:", ["CREATE", "INSERT", "DROP", "ALTER"], "B"),
                ("Normalization reduces:", ["Speed", "Redundancy", "Data", "Memory"], "B"),
                ("1NF removes:", ["Tables", "Repeating groups", "Keys", "Rows"], "B"),
                ("Join is used to:", ["Delete", "Combine tables", "Insert", "Update"], "B"),
                ("Index improves:", ["Storage", "Speed", "Size", "Security"], "B"),
                ("ACID stands for:", ["Accuracy", "Atomicity etc.", "Access", "Action"], "B"),
                ("Transaction is:", ["Query", "Logical unit of work", "Table", "Row"], "B"),
                ("View is:", ["Real table", "Virtual table", "Column", "Row"], "B"),
                ("Stored procedure is:", ["Query", "Precompiled SQL", "Table", "File"], "B"),
                ("RDBMS uses:", ["Files", "Tables", "Images", "Graph"], "B")
            ],
            "DATA SCIENCE": [
                ("Data Science is:", ["Cooking", "Data analysis", "Gaming", "Hardware"], "B"),
                ("EDA stands for:", ["Explore Data Analysis", "Exploratory Data Analysis", "Extra Data", "Error Data"], "B"),
                ("Data cleaning removes:", ["Good data", "Noise", "Tables", "Code"], "B"),
                ("Mean is:", ["Average", "Middle", "Mode", "Range"], "A"),
                ("Median is:", ["Average", "Middle value", "Maximum", "Minimum"], "B"),
                ("Mode is:", ["Rare value", "Most frequent", "Average", "Sum"], "B"),
                ("Standard deviation measures:", ["Mean", "Spread", "Size", "Count"], "B"),
                ("Correlation shows:", ["Size", "Relationship", "Mean", "Mode"], "B"),
                ("Big data means:", ["Small data", "Large complex data", "Simple", "Text"], "B"),
                ("Structured data is:", ["Tables", "Images", "Video", "Audio"], "A"),
                ("Unstructured data is:", ["Tables", "Images/videos", "Rows", "Columns"], "B"),
                ("Visualization uses:", ["Code", "Charts", "Text", "Tables"], "B"),
                ("Hypothesis testing checks:", ["Guess validity", "Data size", "Speed", "Error"], "A"),
                ("Regression analysis finds:", ["Clusters", "Relationship", "Noise", "Labels"], "B"),
                ("Data pipeline is:", ["Storage", "Data flow process", "Table", "Graph size"], "B")
            ]
        }

        # For each subject, create an "Introductory Exam" and add these questions
        for subj_name, questions in mcqs.items():
            subj = subject_objs[subj_name]
            
            # Create an exam if it doesn't exist
            exam_title = f"Fundamental {subj_name} Challenge"
            exam = Exam.query.filter_by(title=exam_title).first()
            if not exam:
                exam = Exam(title=exam_title, duration=30, subject_id=subj.id, teacher_id=admin.id, total_marks=0)
                db.session.add(exam)
                db.session.commit()
                print(f"Created exam: {exam_title}")
            
            # Add questions
            for content, options_list, correct_key in questions:
                # Check if question exists in this exam
                existing_q = Question.query.filter_by(exam_id=exam.id, content=content).first()
                if not existing_q:
                    # Convert options list to dict format
                    options_dict = {
                        "A": options_list[0],
                        "B": options_list[1],
                        "C": options_list[2],
                        "D": options_list[3]
                    }
                    
                    q = Question(
                        exam_id=exam.id,
                        type='MCQ',
                        content=content,
                        options=json.dumps(options_dict),
                        correct_answer=correct_key,
                        marks=1
                    )
                    db.session.add(q)
                    exam.total_marks += 1
                    print(f"Added question: {content[:30]}...")
            
            db.session.commit()

    print("Success: 60 questions seeded into the database!")

if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists('instance/exam_sys.db'):
        print("Database not found. Initializing database first...")
        with app.app_context():
            db.create_all()
    seed_data()
