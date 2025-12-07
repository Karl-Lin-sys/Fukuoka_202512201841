from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Job, Company, Application, Skill
from app.main.forms import JobSearchForm

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).paginate(
        page, current_app.config['JOBS_PER_PAGE'], False)
    next_url = url_for('main.index', page=jobs.next_num) if jobs.has_next else None
    prev_url = url_for('main.index', page=jobs.prev_num) if jobs.has_prev else None
    return render_template('index.html', title='Home', 
                         jobs=jobs.items, next_url=next_url, prev_url=prev_url)

@bp.route('/search')
def search():
    form = JobSearchForm()
    query = request.args.get('q', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    
    # Start building the query
    job_query = Job.query.filter_by(is_active=True)
    
    if query:
        search = f"%{query}%"
        job_query = job_query.filter(
            (Job.title.ilike(search)) | 
            (Job.description.ilike(search)) |
            (Job.requirements.ilike(search))
        )
    
    if location:
        job_query = job_query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        job_query = job_query.filter(Job.job_type == job_type)
    
    page = request.args.get('page', 1, type=int)
    jobs = job_query.order_by(Job.created_at.desc()).paginate(
        page, current_app.config['JOBS_PER_PAGE'], False)
    
    next_url = url_for('main.search', q=query, location=location, 
                      job_type=job_type, page=jobs.next_num) if jobs.has_next else None
    prev_url = url_for('main.search', q=query, location=location, 
                      job_type=job_type, page=jobs.prev_num) if jobs.has_prev else None
    
    return render_template('search.html', title='Search Jobs', form=form,
                         jobs=jobs.items, next_url=next_url, prev_url=prev_url,
                         query=query, location=location, job_type=job_type)

@bp.route('/job/<int:id>')
def job_detail(id):
    job = Job.query.get_or_404(id)
    if not job.is_active and (not current_user.is_authenticated or 
                            (current_user.id != job.user_id and not current_user.is_admin)):
        flash('This job is no longer available.')
        return redirect(url_for('main.index'))
    
    # Check if user has already applied
    has_applied = False
    if current_user.is_authenticated:
        has_applied = Application.query.filter_by(
            user_id=current_user.id, job_id=id).first() is not None
    
    return render_template('job_detail.html', job=job, has_applied=has_applied)

@bp.route('/company/<int:id>')
def company_detail(id):
    company = Company.query.get_or_404(id)
    jobs = Job.query.filter_by(company_id=id, is_active=True).all()
    return render_template('company_detail.html', company=company, jobs=jobs)

@bp.route('/about')
def about():
    return render_template('about.html', title='About Us')

@bp.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Privacy Policy')

@bp.route('/terms')
def terms():
    return render_template('terms.html', title='Terms of Service')
