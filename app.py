from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy=True, order_by='Lesson.order')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(20), default='content')  # 'content', 'exercise', 'exam'
    passing_percentage = db.Column(db.Integer, default=70)  # Required percentage to unlock next
    
    # Relationships
    questions = db.relationship('Question', backref='lesson', lazy=True, order_by='Question.order')
    progress = db.relationship('Progress', backref='lesson', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'multiple_choice', 'open_ended'
    options = db.Column(db.Text)  # JSON string for multiple choice options
    correct_answer = db.Column(db.Text)  # For multiple choice
    order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='question', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('Progress', backref='enrollment', lazy=True)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)  # Percentage score
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean)
    graded = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_feedback = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Teacher Routes
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/dashboard.html', courses=courses)

@app.route('/teacher/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        course = Course(
            title=title,
            description=description,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/create_course.html')

@app.route('/teacher/course/<int:course_id>')
@login_required
def view_course(course_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    return render_template('teacher/view_course.html', course=course, enrollments=enrollments)

@app.route('/teacher/lesson/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        lesson_type = request.form.get('lesson_type')
        passing_percentage = request.form.get('passing_percentage', 70)
        order = request.form.get('order', 1)
        
        lesson = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            lesson_type=lesson_type,
            passing_percentage=int(passing_percentage),
            order=int(order)
        )
        db.session.add(lesson)
        db.session.commit()
        
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    
    max_order = db.session.query(db.func.max(Lesson.order)).filter_by(course_id=course_id).scalar() or 0
    return render_template('teacher/create_lesson.html', course=course, next_order=max_order + 1)

@app.route('/teacher/question/create/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def create_question(lesson_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get(lesson.course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        order = request.form.get('order', 1)
        
        question = Question(
            lesson_id=lesson_id,
            question_text=question_text,
            question_type=question_type,
            order=int(order)
        )
        
        if question_type == 'multiple_choice':
            options = request.form.get('options')
            correct_answer = request.form.get('correct_answer')
            question.options = options
            question.correct_answer = correct_answer
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question created successfully!', 'success')
        return redirect(url_for('view_course', course_id=course.course_id))
    
    max_order = db.session.query(db.func.max(Question.order)).filter_by(lesson_id=lesson_id).scalar() or 0
    return render_template('teacher/create_question.html', lesson=lesson, next_order=max_order + 1)

@app.route('/teacher/submissions')
@login_required
def view_submissions():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get all open-ended submissions that need grading
    submissions = Submission.query.join(Question).join(Lesson).join(Course)\
        .filter(Question.question_type == 'open_ended', Submission.graded == False)\
        .filter(Course.teacher_id == current_user.id)\
        .all()
    
    return render_template('teacher/submissions.html', submissions=submissions)

@app.route('/teacher/grade/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def grade_submission(submission_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    submission = Submission.query.get_or_404(submission_id)
    question = Question.query.get(submission.question_id)
    lesson = Lesson.query.get(question.lesson_id)
    course = Course.query.get(lesson.course_id)
    
    if course.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('view_submissions'))
    
    if request.method == 'POST':
        is_correct = request.form.get('is_correct') == 'on'
        teacher_feedback = request.form.get('teacher_feedback')
        
        submission.is_correct = is_correct
        submission.graded = True
        submission.teacher_feedback = teacher_feedback
        db.session.commit()
        
        flash('Submission graded successfully!', 'success')
        return redirect(url_for('view_submissions'))
    
    return render_template('teacher/grade_submission.html', submission=submission, question=question)

# Student Routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    available_courses = Course.query.all()
    
    enrolled_course_ids = [e.course_id for e in enrollments]
    available_courses = [c for c in available_courses if c.id not in enrolled_course_ids]
    
    return render_template('student/dashboard.html', enrollments=enrollments, available_courses=available_courses)

@app.route('/student/enroll/<int:course_id>')
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('Already enrolled in this course', 'info')
        return redirect(url_for('student_dashboard'))
    
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash('Successfully enrolled in course!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/course/<int:course_id>')
@login_required
def student_view_course(course_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        flash('Not enrolled in this course', 'error')
        return redirect(url_for('student_dashboard'))
    
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    
    # Calculate overall completion percentage
    total_lessons = len(lessons)
    completed_lessons = 0
    lesson_progress = {}
    
    for lesson in lessons:
        progress = Progress.query.filter_by(enrollment_id=enrollment.id, lesson_id=lesson.id).first()
        if progress and progress.completed:
            completed_lessons += 1
            lesson_progress[lesson.id] = {'completed': True, 'score': progress.score}
        elif progress:
            lesson_progress[lesson.id] = {'completed': False, 'score': progress.score}
        else:
            lesson_progress[lesson.id] = {'completed': False, 'score': 0}
    
    overall_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    return render_template('student/view_course.html', 
                         course=course, 
                         lessons=lessons, 
                         lesson_progress=lesson_progress,
                         overall_percentage=overall_percentage,
                         enrollment=enrollment)

@app.route('/student/lesson/<int:lesson_id>')
@login_required
def student_view_lesson(lesson_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=lesson.course_id).first()
    
    if not enrollment:
        flash('Not enrolled in this course', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Check if previous lessons are completed with required percentage
    previous_lessons = Lesson.query.filter(
        Lesson.course_id == lesson.course_id,
        Lesson.order < lesson.order
    ).order_by(Lesson.order).all()
    
    can_access = True
    for prev_lesson in previous_lessons:
        progress = Progress.query.filter_by(enrollment_id=enrollment.id, lesson_id=prev_lesson.id).first()
        if not progress or not progress.completed or progress.score < prev_lesson.passing_percentage:
            can_access = False
            break
    
    if not can_access:
        flash('Complete previous lessons with required score to access this lesson', 'warning')
        return redirect(url_for('student_view_course', course_id=lesson.course_id))
    
    questions = Question.query.filter_by(lesson_id=lesson_id).order_by(Question.order).all()
    progress = Progress.query.filter_by(enrollment_id=enrollment.id, lesson_id=lesson_id).first()
    
    return render_template('student/view_lesson.html', 
                         lesson=lesson, 
                         questions=questions, 
                         progress=progress,
                         enrollment=enrollment)

@app.route('/student/submit/<int:question_id>', methods=['POST'])
@login_required
def submit_answer(question_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    question = Question.query.get_or_404(question_id)
    lesson = Lesson.query.get(question.lesson_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=lesson.course_id).first()
    
    if not enrollment:
        flash('Not enrolled in this course', 'error')
        return redirect(url_for('student_dashboard'))
    
    answer = request.form.get('answer')
    
    # Check if submission already exists
    existing_submission = Submission.query.filter_by(
        student_id=current_user.id,
        question_id=question_id
    ).first()
    
    if existing_submission:
        flash('Already submitted answer for this question', 'info')
        return redirect(url_for('student_view_lesson', lesson_id=lesson.id))
    
    is_correct = None
    if question.question_type == 'multiple_choice':
        is_correct = (answer == question.correct_answer)
    
    submission = Submission(
        student_id=current_user.id,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct,
        graded=(question.question_type == 'multiple_choice')
    )
    db.session.add(submission)
    
    # Update or create progress
    progress = Progress.query.filter_by(enrollment_id=enrollment.id, lesson_id=lesson.id).first()
    if not progress:
        progress = Progress(enrollment_id=enrollment.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    # Calculate score for the lesson
    all_questions = Question.query.filter_by(lesson_id=lesson.id).all()
    total_questions = len(all_questions)
    correct_answers = 0
    
    for q in all_questions:
        sub = Submission.query.filter_by(student_id=current_user.id, question_id=q.id).first()
        if sub and sub.graded and sub.is_correct:
            correct_answers += 1
    
    if total_questions > 0:
        score = int((correct_answers / total_questions) * 100)
        progress.score = score
        
        if score >= lesson.passing_percentage:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Answer submitted successfully!', 'success')
    return redirect(url_for('student_view_lesson', lesson_id=lesson.id))

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
