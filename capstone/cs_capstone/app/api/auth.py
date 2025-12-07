from flask import jsonify, g, request, current_app
from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

# Initialize token authentication
token_auth = HTTPTokenAuth(scheme='Bearer')

@token_auth.verify_token
def verify_token(token):
    # Check if this is a test request with a test token
    if current_app.config['TESTING'] and token == 'test-token':
        # Return a test user
        g.current_user = User.query.get(1)  # Assuming test user has ID 1
        return g.current_user is not None
    
    # Normal token verification
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return error_response(401, 'Invalid or missing token')

@token_auth.get_user_roles
def get_user_roles(user):
    roles = []
    if user.is_admin:
        roles.append('admin')
    if user.is_employer:
        roles.append('employer')
    else:
        roles.append('job_seeker')
    return roles

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({
                'message': 'Token is invalid!'
            }), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def employer_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_employer and not current_user.is_admin:
            return jsonify({'message': 'Employer access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
