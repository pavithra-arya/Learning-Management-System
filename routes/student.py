from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Course, Enrollment, Material, Assignment, Submission, Attendance
from datetime import datetime

student = Blueprint('student', __name__, url_prefix='/student')

def student_required(func):
    """Decorator to ensure user is a student."""
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied. Student privileges required.', 'error')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Courses student is enrolled in
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template('student/dashboard.html', enrollments=enrollments)

@student.route('/courses/available')
@login_required
@student_required
def available_courses():
    # Only show courses the student is NOT enrolled in
    enrolled_course_ids = [e.course_id for e in current_user.enrollments]
    available = Course.query.filter(Course.id.notin_(enrolled_course_ids)).all()
    return render_template('student/available_courses.html', courses=available)

@student.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
@student_required
def enroll(course_id):
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'error')
        return redirect(url_for('student.dashboard'))
        
    new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()
    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('student.dashboard'))

@student.route('/course/<int:course_id>')
@login_required
@student_required
def view_course(course_id):
    # Verify enrollment
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        flash('You must enroll in this course to view its contents.', 'error')
        return redirect(url_for('student.available_courses'))
        
    course = Course.query.get_or_404(course_id)
    materials = Material.query.filter_by(course_id=course.id).all()
    assignments = Assignment.query.filter_by(course_id=course.id).all()
    
    # Get student's submissions for these assignments
    submissions = {s.assignment_id: s for s in Submission.query.filter_by(student_id=current_user.id).all()}
    
    return render_template('student/view_course.html', course=course, materials=materials, assignments=assignments, submissions=submissions)

@student.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify enrollment in course
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=assignment.course_id).first()
    if not enrollment:
        flash('You must enroll in this course to submit assignments.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check for existing submission
    existing = Submission.query.filter_by(student_id=current_user.id, assignment_id=assignment.id).first()
    
    if request.method == 'POST':
        # Simple URL submission for now
        file_url = request.form.get('url')
        
        if existing:
            existing.file_path = file_url
            existing.submitted_at = datetime.utcnow()
            flash('Submission updated successfully!', 'success')
        else:
            new_submission = Submission(
                assignment_id=assignment.id,
                student_id=current_user.id,
                file_path=file_url
            )
            db.session.add(new_submission)
            flash('Assignment submitted successfully!', 'success')
            
        db.session.commit()
        return redirect(url_for('student.view_course', course_id=assignment.course_id))
        
    return render_template('student/submit_assignment.html', assignment=assignment, existing=existing)

@student.route('/progress')
@login_required
@student_required
def progress():
    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    attendances = Attendance.query.filter_by(student_id=current_user.id).all()
    
    return render_template('student/progress.html', submissions=submissions, attendances=attendances)
