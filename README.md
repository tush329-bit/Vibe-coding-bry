# EduPlatform - Online Learning Management System

A fully functioning online learning platform where learners can take exams, access lessons with completion tracking, and teachers can manage courses and grade student work.

## Features

### For Students:
- **User Registration & Login**: Create accounts as students or teachers
- **Course Enrollment**: Browse and enroll in available courses
- **Progress Tracking**: View completion percentage for each course
- **Sequential Learning**: Access lessons in order; must pass previous lessons to unlock next ones
- **Mixed Content**: Lessons can include content, exercises, and exams
- **Question Types**: Answer multiple-choice (auto-graded) and open-ended questions (teacher-graded)
- **Score Monitoring**: View scores and feedback from teachers

### For Teachers:
- **Course Creation**: Create and manage courses
- **Lesson Management**: Add lessons with customizable passing percentages
- **Question Creation**: Create multiple-choice and open-ended questions
- **Student Monitoring**: View enrolled students
- **Grading System**: Grade open-ended question submissions with feedback
- **Submission Queue**: See all pending submissions that need grading

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login for user sessions
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Password hashing with Werkzeug

## Installation

1. Ensure you have Python 3.8+ installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### First-Time Setup

1. **Register a Teacher Account**: Go to registration, select "Teacher" role
2. **Create a Course**: Login as teacher, click "Create New Course"
3. **Add Lessons**: Navigate to course, add lessons with passing percentages
4. **Add Questions**: For each lesson, add multiple-choice or open-ended questions

### Student Workflow

1. Register as Student
2. Browse and enroll in courses
3. Complete lessons sequentially (must pass each to unlock next)
4. Answer questions (auto-graded or teacher-graded)
5. Track progress and view feedback

### Teacher Workflow

1. Create and manage courses
2. Add lessons and questions
3. Grade open-ended submissions
4. Monitor student progress

## Key Features

- **Sequential Learning**: Lessons locked until previous ones passed
- **Percentage Requirements**: Set minimum scores to advance
- **Mixed Content**: Content, exercises, and exam lesson types
- **Auto & Manual Grading**: Multiple-choice auto-graded, open-ended by teachers
- **Progress Tracking**: Visual progress bars and completion percentages

## File Structure

```
/workspace
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── platform.db                 # SQLite database
├── static/css/style.css        # Stylesheet
└── templates/                  # HTML templates
    ├── index.html
    ├── login.html
    ├── register.html
    ├── teacher/                # Teacher templates
    └── student/                # Student templates
```

## Running the Application

The server is currently running at http://localhost:5000

To restart: `python app.py`

For production: Change SECRET_KEY and set DEBUG=False
