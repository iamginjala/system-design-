from models.payment import Payments
from utils.database import SessionLocal
from sqlalchemy.exc import DatabaseError
from uuid import UUID,uuid4
from flask import Blueprint,request,jsonify

payment_bp = Blueprint('payment',__name__,url_prefix='/api/payments')

@payment_bp.route('/international', methods=['GET','POST'])
def accept_payment():
    if request.method == 'POST':
        data = request.get_json()
        with SessionLocal() as db:
            try:
                if not data:
                    return jsonify({'status':False,'message':'No data provided'}),400
                order_id = data.get('order_id')
                customer_id = data.get('customer_id')
                amount = data.get('amount')
                currency = data.get('currency')
                pay_met = data.get('payment_method')

                #validation check 
                if not all([order_id,customer_id,amount,currency,pay_met]):
                    return jsonify({'status':False,'error':'missing reuired fields'}),400

                transaction_id = f"TXN-{uuid4().hex[:12].upper()}"
                order_id = UUID(order_id)
                    
                new_pay =  Payments(order_id = order_id,customer_id= customer_id,
                                    amount=amount,currency=currency,
                                    payment_method = pay_met,
                                    transaction_id=transaction_id)
                db.add(new_pay)
                db.commit()
                return jsonify({'status':True, 'message':"sucessfully stored payment details"}),200
            except DatabaseError as dbe:
                return jsonify({'status':False,'error': f"Database Error: {dbe}"}),400
            except Exception as e:
                return jsonify({'status':False,'message':f"{e}"}),400
    else:
        return "please try again"
