import pytest
from routes.auth import is_valid_email,validate_password,generate_token,decode_token
from utils.auth import get_token_from_header,verify_token,require_admin
from unittest.mock import Mock


class TestEmailValidation:
    def test_valid_email(self):
        assert is_valid_email('user@gmail.com') == True
        assert is_valid_email('user@email.com') == True
        assert is_valid_email('name12@company.org') == True
        assert is_valid_email('test.user+tag@domain.co.us') == True
    
    def test_invalid_email(self):
        assert is_valid_email('user @ example.com') == False
        assert is_valid_email('@exmaple.com') == False
        assert is_valid_email('') == False
        assert is_valid_email('notanemail') == False
        assert is_valid_email('user@') == False

class TestPasswordValidation:
    def test_valid_password(self):
        assert validate_password('Test@1234') == True
        assert validate_password('tesT@1234556') == True
        assert validate_password("Str0ng@Pass") == True
        assert validate_password("MyP@ssw0rd") == True
    
    def test_invalid_password(self):
        assert validate_password('') == False
        assert validate_password('test@1234') == False
        assert validate_password('test1234') == False
        assert validate_password('TEST!1203') == False

class TestTokenExtraction:
    def test_valid_bearer_token(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = "Bearer abc123token"

        result = get_token_from_header(mock_request)

        assert result =="abc123token"

    def test_missing_bearer_token(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        result = get_token_from_header(mock_request)
        assert result == None
    
    def test_invalid_bearer_token(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = "Not a token"
        result = get_token_from_header(mock_request)
        assert result == None

class TestTokenVerification:
    def test_valid_token(self, app):
        with app.app_context():
            mock_user = Mock()
            mock_user.user_id = '123'
            mock_user.name = 'Test User'
            mock_user.role = 'user'

            token = generate_token(mock_user)
            result = verify_token(token)

            assert result is not None
            assert result['user_id'] == '123'
            assert result['name'] == 'Test User'
            assert result['role'] == 'user'
    
    def test_invalid_token(self, app):
        with app.app_context():
            result = verify_token("this.is.not.a.real.token")

            assert result is None

class TestAdminAuthorization:
    def test_admin_user(self):
        admin_payload = { 
        'user_id': '1234',
        'name': 'test admin',
        'role': 'admin'
        }
        result = require_admin(admin_payload) 

        assert result == True
    def test_normal_user(self):
        user_payload = {
            'user_id': '1234',
            'name': 'test user',
            'role': 'user'
        }

        result = require_admin(user_payload)

        assert result == False


    def test_none_payload(self):
        result = require_admin(None)
        assert result == False