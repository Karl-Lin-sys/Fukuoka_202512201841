from flask import jsonify, request
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    return error_response(400, message)

def unauthorized(message='Please authenticate to access this resource'):
    return error_response(401, message)

def forbidden(message='You do not have permission to access this resource'):
    return error_response(403, message)

def not_found(message='The requested resource was not found'):
    return error_response(404, message)

def method_not_allowed(message='The method is not allowed for the requested URL'):
    return error_response(405, message)

def validation_error(field, message):
    return error_response(422, {field: [message]})

def rate_limit_exceeded():
    return error_response(429, 'Too many requests')

class ValidationError(ValueError):
    pass

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(str(e))

@api.errorhandler(404)
def not_found_error(error):
    return not_found('The requested resource was not found')

@api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return error_response(500, 'An internal error occurred')
