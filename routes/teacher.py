from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Course, Material, Assignment, Submission, Attendance, User
import os
from werkzeug.utils import secure_filename
from datetime import datetime

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(func):
    """Decorator to ensure user is a teacher."""
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != 'teacher':
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

@teacher.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/dashboard.html', courses=courses)

@teacher.route('/course/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash('Course title is required.', 'error')
            return redirect(url_for('teacher.create_course'))

        new_course = Course(
            title=title,
            description=description,
            teacher_id=current_user.id
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('teacher.dashboard'))
    return render_template('teacher/create_course.html')

@teacher.route('/course/<int:course_id>')
@login_required
@teacher_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))
    
    materials = Material.query.filter_by(course_id=course_id).all()
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    return render_template('teacher/view_course.html', course=course, materials=materials, assignments=assignments)

@teacher.route('/course/<int:course_id>/material/upload', methods=['GET', 'POST'])
@login_required
@teacher_required
def upload_material(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url') # For simplicity, saving URL links instead of files
        
        new_material = Material(
            title=title,
            file_path=url, 
            course_id=course.id
        )
        db.session.add(new_material)
        db.session.commit()
        flash('Material uploaded successfully!', 'success')
        return redirect(url_for('teacher.view_course', course_id=course.id))

    return render_template('teacher/upload_material.html', course=course)

@teacher.route('/course/<int:course_id>/assignment/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('teacher.create_assignment', course_id=course.id))

        new_assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            course_id=course.id
        )
        db.session.add(new_assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('teacher.view_course', course_id=course.id))

    return render_template('teacher/create_assignment.html', course=course)

@teacher.route('/assignment/<int:assignment_id>/submissions')
@login_required
@teacher_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))
        
    submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
    return render_template('teacher/view_submissions.html', assignment=assignment, submissions=submissions)

@teacher.route('/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
@teacher_required
def grade_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))

    grade = request.form.get('grade')
    feedback = request.form.get('feedback')
    
    submission.grade = grade
    submission.feedback = feedback
    db.session.commit()
    
    flash('Submission graded successfully!', 'success')
    return redirect(url_for('teacher.view_submissions', assignment_id=submission.assignment_id))

@teacher.route('/course/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark_attendance(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.dashboard'))

    # Get all students enrolled in this course
    enrolled_students = User.query.join(User.enrollments).filter_by(course_id=course.id).all()

    if request.method == 'POST':
        date_str = request.form.get('date')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('teacher.mark_attendance', course_id=course.id))

        for student in enrolled_students:
            status = request.form.get(f'status_{student.id}')
            if status:
                # Check if record already exists
                existing = Attendance.query.filter_by(course_id=course.id, student_id=student.id, date=date_obj).first()
                if existing:
                    existing.status = status
                else:
                    new_attendance = Attendance(
                        course_id=course.id,
                        student_id=student.id,
                        date=date_obj,
                        status=status
                    )
                    db.session.add(new_attendance)
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('teacher.view_course', course_id=course.id))

    return render_template('teacher/mark_attendance.html', course=course, students=enrolled_students, today=datetime.today().strftime('%Y-%m-%d'))
