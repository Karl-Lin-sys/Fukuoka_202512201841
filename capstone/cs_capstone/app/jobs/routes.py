from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Job, Company, Application, Skill
from app.jobs import bp
from app.jobs.forms import JobForm, ApplicationForm
from app.auth.email import send_application_confirmation, send_application_notification

@bp.route('/post', methods=['GET', 'POST'])
@login_required
def post_job():
    if not current_user.is_employer:
        flash('Only employers can post jobs.')
        return redirect(url_for('main.index'))
    
    form = JobForm()
    if form.validate_on_submit():
        # Get or create company for the current user
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            company = Company(
                name=f"{current_user.username}'s Company",
                user_id=current_user.id
            )
            db.session.add(company)
            db.session.commit()
        
        # Create the job
        job = Job(
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            location=form.location.data,
            salary_range=form.salary_range.data,
            job_type=form.job_type.data,
            is_remote=form.is_remote.data,
            company_id=company.id,
            user_id=current_user.id
        )
        
        # Add skills if any
        if form.skills.data:
            skill_names = [s.strip() for s in form.skills.data.split(',') if s.strip()]
            for skill_name in skill_names:
                skill = Skill.query.filter_by(name=skill_name.lower()).first()
                if not skill:
                    skill = Skill(name=skill_name.lower())
                    db.session.add(skill)
                job.skills.append(skill)
        
        db.session.add(job)
        db.session.commit()
        
        flash('Your job has been posted!', 'success')
        return redirect(url_for('jobs.job_detail', id=job.id))
    
    return render_template('jobs/post_job.html', title='Post a Job', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    job = Job.query.get_or_404(id)
    
    # Check if current user is the owner or admin
    if current_user.id != job.user_id and not current_user.is_admin:
        flash('You do not have permission to edit this job.')
        return redirect(url_for('jobs.job_detail', id=id))
    
    form = JobForm()
    
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        job.requirements = form.requirements.data
        job.location = form.location.data
        job.salary_range = form.salary_range.data
        job.job_type = form.job_type.data
        job.is_remote = form.is_remote.data
        
        # Update skills
        if form.skills.data:
            job.skills = []
            skill_names = [s.strip() for s in form.skills.data.split(',') if s.strip()]
            for skill_name in skill_names:
                skill = Skill.query.filter_by(name=skill_name.lower()).first()
                if not skill:
                    skill = Skill(name=skill_name.lower())
                    db.session.add(skill)
                job.skills.append(skill)
        
        db.session.commit()
        flash('Your job has been updated!', 'success')
        return redirect(url_for('jobs.job_detail', id=job.id))
    elif request.method == 'GET':
        form.title.data = job.title
        form.description.data = job.description
        form.requirements.data = job.requirements
        form.location.data = job.location
        form.salary_range.data = job.salary_range
        form.job_type.data = job.job_type
        form.is_remote.data = job.is_remote
        if job.skills:
            form.skills.data = ', '.join([s.name for s in job.skills])
    
    return render_template('jobs/edit_job.html', title='Edit Job', form=form, job=job)

@bp.route('/<int:id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(id):
    job = Job.query.get_or_404(id)
    
    # Check if job is active
    if not job.is_active:
        flash('This job is no longer accepting applications.', 'warning')
        return redirect(url_for('jobs.job_detail', id=id))
    
    # Check if user has already applied
    existing_application = Application.query.filter_by(
        user_id=current_user.id, job_id=id).first()
    if existing_application:
        flash('You have already applied to this job.', 'warning')
        return redirect(url_for('jobs.job_detail', id=id))
    
    form = ApplicationForm()
    if form.validate_on_submit():
        # Save the uploaded resume
        if form.resume.data:
            # In a production app, you would save the file to a storage service
            # and save the path to the application
            resume_filename = f"resume_{current_user.id}_{job.id}.{form.resume.data.filename.split('.')[-1]}"
            # Save file logic would go here
        
        # Create the application
        application = Application(
            cover_letter=form.cover_letter.data,
            user_id=current_user.id,
            job_id=job.id,
            # resume_path=resume_filename  # Save the path to the resume
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Send confirmation email to applicant
        send_application_confirmation(application)
        
        # Send notification to employer
        send_application_notification(application)
        
        flash('Your application has been submitted!', 'success')
        return redirect(url_for('jobs.job_detail', id=id))
    
    return render_template('jobs/apply.html', title=f'Apply for {job.title}', 
                         form=form, job=job)

@bp.route('/<int:id>/applications')
@login_required
def job_applications(id):
    job = Job.query.get_or_404(id)
    
    # Check if current user is the job poster or admin
    if current_user.id != job.user_id and not current_user.is_admin:
        flash('You do not have permission to view these applications.', 'danger')
        return redirect(url_for('jobs.job_detail', id=id))
    
    applications = job.applications.order_by(Application.created_at.desc()).all()
    
    return render_template('jobs/applications.html', title=f'Applications for {job.title}',
                         job=job, applications=applications)

@bp.route('/<int:id>/close')
@login_required
def close_job(id):
    job = Job.query.get_or_404(id)
    
    # Check if current user is the job poster or admin
    if current_user.id != job.user_id and not current_user.is_admin:
        flash('You do not have permission to close this job.', 'danger')
        return redirect(url_for('jobs.job_detail', id=id))
    
    job.is_active = False
    db.session.commit()
    
    flash('The job has been closed and will no longer accept applications.', 'success')
    return redirect(url_for('jobs.job_detail', id=id))
