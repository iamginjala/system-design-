from flask import jsonify,Blueprint,request
from models import User
from utils.database import SessionLocal
from sqlalchemy.exc import IntegrityError,DatabaseError
import re
import uuid
from datetime import datetime

auth_bp = Blueprint('auth',__name__,url_prefix='/auth')

def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern,email) is not None


# Function to validate password
def validate_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    if re.match(pattern, password):
        return True
    else:
        return False


@auth_bp.route('/register', methods=['POST'])
def register():
        data = request.get_json()
        with SessionLocal() as db:
            try:
                if not data:
                    return jsonify({'status': False, 'message': 'No data provided'}), 400
                email = data.get('email')
                if not is_valid_email(email):
                    return jsonify({'status': False, 'message': 'Please enter valid email'}), 400
                result = db.query(User).filter(User.email == email).first()
                if result is not None:
                    return jsonify({'status': False, 'message': 'Already have an account with the email'}), 409

                password = data.get('password')
                if not validate_password(password):
                    return jsonify({'status': False, 'message': 'Please enter valid password'}), 400

                new_user = User(
                    email=email,
                    name=data.get('name'),
                )
                new_user.set_password(password)
                db.add(new_user)
                db.commit()
                return jsonify({'status': True, 'message': "user registered sucessfully",'user':new_user.to_dict()}), 201
            except DatabaseError as dbe:
                return jsonify({'status': False, 'error': f"Database Error: {dbe}"}), 400
            except Exception as e:
                return jsonify({'status': False, 'message': f"{e}"}), 400

