from routes.auth import decode_token
from flask import Request

def get_token_from_header(request: Request):
    token = request.headers.get('Authorization')
    if token is not None:
        result_token = token.removeprefix('Bearer ')
        return result_token
    
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
