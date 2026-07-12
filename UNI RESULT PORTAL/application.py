from flask import Flask, render_template, request, redirect, url_for, session, send_file
import mysql.connector
from mysql.connector import Error
import random
import logging
import os
from datetime import datetime
from fpdf import FPDF  
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

# ==================== MySQL Configuration ====================
db_config = {
    'host': 'localhost',          # Change if needed
    'user': 'root',               # Your MySQL username
    'password': 'khushboo123@955',  # Your MySQL password
    'database': 'university_portal'  # Will be created if not exists
}
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS university_portal")
    cursor.execute("USE university_portal")
    
    # Students Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        rollno VARCHAR(20) PRIMARY KEY,
                        name VARCHAR(100),
                        program VARCHAR(50),
                        batch VARCHAR(20),
                        password VARCHAR(50)
                    )''')
    
    # Marks Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS marks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rollno VARCHAR(20),
                        semester INT,
                        subject VARCHAR(100),
                        internal INT,
                        external INT,
                        total INT,
                        grade VARCHAR(5),
                        FOREIGN KEY(rollno) REFERENCES students(rollno)
                    )''')
    
    # Sample Students (only insert if table is empty)
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students_data = [
            ('24DIT001', 'Rahul Sharma', 'B.Sc. ITM', '2024-27', 'rahul123'),
            ('24DIT002', 'Priya Patel', 'B.Sc. ITM', '2024-27', 'pass123'),
            # ... (add more or keep the original 20 from database.py)
        ]
        for student in students_data:
            cursor.execute("INSERT IGNORE INTO students VALUES (%s, %s, %s, %s, %s)", student)
        
        # Generate marks (same logic as before)
        subjects_per_sem = {
            1: ['C Programming', 'Mathematics-I', 'Digital Electronics'],
            2: ['Data Structures', 'Mathematics-II', 'Business Communication'],
            # ... (copy full dict from original database.py)
        }
        
        for rollno in [s[0] for s in students_data]:
            for sem, subs in subjects_per_sem.items():
                for subj in subs:
                    internal = random.randint(20, 35)
                    external = random.randint(50, 80)
                    total = internal + external
                    if total >= 90: grade = 'O'
                    elif total >= 80: grade = 'A+'
                    elif total >= 70: grade = 'A'
                    elif total >= 60: grade = 'B+'
                    else: grade = 'B'
                    
                    cursor.execute("""INSERT IGNORE INTO marks 
                                   (rollno, semester, subject, internal, external, total, grade) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                   (rollno, sem, subj, internal, external, total, grade))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ MySQL Database initialized successfully!")

# ==================== Database Functions ====================
def verify_login(rollno, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE rollno = %s AND password = %s", (rollno, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user[0] if user else None

def get_student_results(rollno):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    
    # Updated SELECT to match new table columns
    cursor.execute('''SELECT semester, subject, internal, practical, theory, total, grade 
                      FROM marks 
                      WHERE rollno = %s 
                      ORDER BY semester, subject''', (rollno,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
def calculate_cgpa(results_data):
    if not results_data:
        return 0.0
    total_points = 0
    total_credits = 0
    grade_points = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6}
    
    for row in results_data:
        credits = 4  # Assume fixed credits per subject (customize as needed)
        grade = row[6] if len(row) > 6 else 'B'
        gp = grade_points.get(grade, 6)
        total_points += gp * credits
        total_credits += credits
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Ravenshaw University - ITM Results', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')

def generate_pdf_results(rollno, name, semesters, cgpa):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Student Name: {name}          Roll No: {rollno}", 0, 1)
    pdf.cell(0, 10, f"Overall CGPA: {cgpa} / 10.0", 0, 1, 'C')
    pdf.ln(15)
    
    for sem, subjects in semesters.items():
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, f"Semester {sem}", 0, 1)
        pdf.set_font('Arial', '', 10)
        
        # Table
        col_widths = [80, 20, 20, 20, 20, 20]
        headers = ['Subject', 'Internal', 'Practical', 'Theory', 'Total', 'Grade']
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
        pdf.ln()
        
        for sub in subjects:
            pdf.cell(col_widths[0], 8, sub['subject'][:65], 1)
            pdf.cell(col_widths[1], 8, str(sub['internal']), 1, 0, 'C')
            pdf.cell(col_widths[2], 8, str(sub.get('practical', 0)), 1, 0, 'C')
            pdf.cell(col_widths[3], 8, str(sub.get('theory', 0)), 1, 0, 'C')
            pdf.cell(col_widths[4], 8, str(sub['total']), 1, 0, 'C')
            pdf.cell(col_widths[5], 8, sub['grade'], 1, 0, 'C')
            pdf.ln()
        pdf.ln(8)
    
    filename = f"results_{rollno}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

# ==================== Routes (Unchanged) ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rollno = request.form.get('rollno')
        password = request.form.get('password')
        
        name = verify_login(rollno, password)   # Your existing function
        
        if name:
            session['rollno'] = rollno
            session['name'] = name
            return redirect(url_for('results'))
        else:
            # Stay on same page + show error
            return redirect(url_for('login') + '?error=1')
    
    return render_template('login.html')

@app.route('/results')
def results():
    if 'rollno' not in session:
        return redirect(url_for('login'))
    
    rollno = session['rollno']
    results_data = get_student_results(rollno)
    
    semesters = {}
    for row in results_data:
        sem = row[0]
        if sem not in semesters:
            semesters[sem] = []
        
        semesters[sem].append({
            'subject': row[1],
            'internal': row[2],
            'practical': row[3],      # New
            'theory': row[4],         # New
            'total': row[5],
            'grade': row[6]
        })
    
    return render_template('results.html', 
                         semesters=semesters, 
                         rollno=rollno, 
                         name=session.get('name'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/notices')
def notices():
    return render_template('notices.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/download_results')
def download_results():
    if 'rollno' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in
    
    rollno = session['rollno']
    name = session.get('name', 'Student')
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed. Please try again later.", 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT semester, subject, internal, practical, theory, total, grade 
                          FROM marks 
                          WHERE rollno = %s 
                          ORDER BY semester, subject''', (rollno,))
        results_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results_data:
            return "No results found for your account.", 404
        
        # Build semesters dict for PDF
        semesters = {}
        for row in results_data:
            sem = row[0]
            if sem not in semesters:
                semesters[sem] = []
            semesters[sem].append({
                'subject': row[1],
                'internal': row[2],
                'practical': row[3],
                'theory': row[4],
                'total': row[5],
                'grade': row[6]
            })
        
        cgpa = calculate_cgpa(results_data)
        
        # Generate PDF
        pdf_file = generate_pdf_results(rollno, name, semesters, cgpa)
        
        if os.path.exists(pdf_file):
            return send_file(pdf_file, as_attachment=True, download_name=f"results_{rollno}.pdf")
        else:
            return "Failed to generate PDF file.", 500
            
    except Exception as e:
        print(f"Download error: {e}")  # For debugging
        return f"An error occurred while generating your results: {str(e)}", 500
    

if __name__ == '__main__':
    init_db()  # Initialize on first run
    print("🚀 ITM Portal (MySQL) running at http://localhost:5000")
    app.run(debug=True, port=5000)