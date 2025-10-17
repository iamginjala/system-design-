from routes.auth import decode_token
from flask import Request

def get_token_from_header(request: Request):
    token = request.headers.get('Authorization')
    if token is not None:
        if token.startswith('Bearer '):
            ans = token.removeprefix('Bearer ')
            if not ans.strip():  # Check for empty or whitespace
                return None
            return ans
    return None 
def verify_token(token):
    result = decode_token(token)

    if result['valid'] == True:
        return dict(result['payload'])
    
    return None
def require_admin(user_payload):
    if user_payload is not None and user_payload['role'] == 'admin':
        return True
    return False
def authenticate_admin(info):
    flask_request = info.context["request"]
    token = get_token_from_header(flask_request)
    if not token:
        raise Exception("Authentication required")
    payload = verify_token(token)
    if not payload:
        raise Exception("Invalid Token")
    if not require_admin(payload):
        raise Exception("Admin access required")
    return payload
def authenticate_user(info):
    flask_request = info.context["request"]
    token = get_token_from_header(flask_request)
    if not token:
        raise Exception("Authentication required")
    payload = verify_token(token)
    if not payload:
        raise Exception("Invalid Token")
    return payload
