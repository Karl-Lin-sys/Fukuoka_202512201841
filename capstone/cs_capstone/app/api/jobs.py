from flask import jsonify, request, url_for, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Job, Company, Application, Skill
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response

@bp.route('/jobs', methods=['GET'])
def get_jobs():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Filtering
    query = Job.query.filter_by(is_active=True)
    
    # Search by keyword
    if 'q' in request.args:
        search = f"%{request.args['q']}%"
        query = query.filter(
            (Job.title.ilike(search)) | 
            (Job.description.ilike(search)) |
            (Job.requirements.ilike(search))
        )
    
    # Filter by location
    if 'location' in request.args:
        query = query.filter(Job.location.ilike(f"%{request.args['location']}%"))
    
    # Filter by job type
    if 'job_type' in request.args:
        query = query.filter(Job.job_type == request.args['job_type'])
    
    # Filter by remote
    if 'remote' in request.args:
        query = query.filter(Job.is_remote == (request.args['remote'].lower() == 'true'))
    
    # Filter by company
    if 'company_id' in request.args:
        query = query.filter(Job.company_id == request.args['company_id'])
    
    # Order by
    order_by = request.args.get('order_by', 'created_at')
    order_dir = request.args.get('order_dir', 'desc')
    
    if order_by == 'title':
        if order_dir == 'asc':
            query = query.order_by(Job.title.asc())
        else:
            query = query.order_by(Job.title.desc())
    elif order_by == 'company':
        if order_dir == 'asc':
            query = query.join(Company).order_by(Company.name.asc())
        else:
            query = query.join(Company).order_by(Company.name.desc())
    else:  # Default: order by created_at
        if order_dir == 'asc':
            query = query.order_by(Job.created_at.asc())
        else:
            query = query.order_by(Job.created_at.desc())
    
    # Paginate the results
    data = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Build response
    items = [item.to_dict() for item in data.items]
    
    # Build pagination links
    next_url = url_for('api.get_jobs', page=page + 1, per_page=per_page, 
                      _external=True) if data.has_next else None
    prev_url = url_for('api.get_jobs', page=page - 1, per_page=per_page,
                      _external=True) if data.has_prev else None
    
    return jsonify({
        'items': items,
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': data.pages,
            'total_items': data.total
        },
        '_links': {
            'next': next_url,
            'prev': prev_url
        }
    })

@bp.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    job = Job.query.get_or_404(id)
    
    # Only show inactive jobs to the owner or admin
    if not job.is_active and (not current_user.is_authenticated or 
                            (current_user.id != job.user_id and not current_user.is_admin)):
        return error_response(404, 'Job not found')
    
    return jsonify(job.to_dict(include_company=True, include_skills=True))

@bp.route('/jobs', methods=['POST'])
@token_auth.login_required
def create_job():
    if not current_user.is_employer and not current_user.is_admin:
        return error_response(403, 'Only employers can post jobs')
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['title', 'description', 'requirements', 'location', 'job_type']
    for field in required_fields:
        if field not in data:
            return bad_request(f'must include {field} field')
    
    # Get or create company
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        company = Company(
            name=f"{current_user.username}'s Company",
            user_id=current_user.id
        )
        db.session.add(company)
        db.session.commit()
    
    # Create job
    job = Job()
    job.from_dict(data)
    job.company_id = company.id
    job.user_id = current_user.id
    
    # Add skills if provided
    if 'skills' in data and isinstance(data['skills'], list):
        for skill_name in data['skills']:
            skill = Skill.query.filter_by(name=skill_name.lower()).first()
            if not skill:
                skill = Skill(name=skill_name.lower())
                db.session.add(skill)
            job.skills.append(skill)
    
    db.session.add(job)
    db.session.commit()
    
    response = jsonify(job.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_job', id=job.id, _external=True)
    return response

@bp.route('/jobs/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_job(id):
    job = Job.query.get_or_404(id)
    
    # Check permissions
    if current_user.id != job.user_id and not current_user.is_admin:
        return error_response(403, 'You do not have permission to update this job')
    
    data = request.get_json() or {}
    
    # Update job fields
    job.from_dict(data)
    
    # Update skills if provided
    if 'skills' in data and isinstance(data['skills'], list):
        job.skills = []
        for skill_name in data['skills']:
            skill = Skill.query.filter_by(name=skill_name.lower()).first()
            if not skill:
                skill = Skill(name=skill_name.lower())
                db.session.add(skill)
            job.skills.append(skill)
    
    db.session.commit()
    
    return jsonify(job.to_dict())

@bp.route('/jobs/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_job(id):
    job = Job.query.get_or_404(id)
    
    # Check permissions
    if current_user.id != job.user_id and not current_user.is_admin:
        return error_response(403, 'You do not have permission to delete this job')
    
    db.session.delete(job)
    db.session.commit()
    
    return '', 204

@bp.route('/jobs/<int:id>/applications', methods=['GET'])
@token_auth.login_required
def get_job_applications(id):
    job = Job.query.get_or_404(id)
    
    # Check permissions
    if current_user.id != job.user_id and not current_user.is_admin:
        return error_response(403, 'You do not have permission to view these applications')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Get applications
    data = job.applications.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    # Build response
    items = [item.to_dict(include_user=True) for item in data.items]
    
    # Build pagination links
    next_url = url_for('api.get_job_applications', id=id, page=page + 1, 
                      per_page=per_page, _external=True) if data.has_next else None
    prev_url = url_for('api.get_job_applications', id=id, page=page - 1,
                      per_page=per_page, _external=True) if data.has_prev else None
    
    return jsonify({
        'items': items,
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': data.pages,
            'total_items': data.total
        },
        '_links': {
            'next': next_url,
            'prev': prev_url
        }
    })
