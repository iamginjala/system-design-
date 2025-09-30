from utils.database import SessionLocal,Base
from flask import Blueprint,jsonify,request
from sqlalchemy.exc import DatabaseError
from uuid import UUID
from models.order import Orders

order_bp = Blueprint('order', __name__, url_prefix='/api')

@order_bp.route('/orders/<order_id>/track',methods=['GET'])
def track_orders(order_id):
    with SessionLocal() as db:
        try:
            results_db = db.query(Orders).filter(Orders.order_id == UUID(order_id)).first()
            if not results_db: 
                return jsonify({'status': False,'message':'No orders found for this order_id'}),400

            order_data ={
                'Customer':str(results_db.customer_id),
                'Status' : results_db.status,
                'tracking_info' : results_db.tracking_info,
                'amount_paid':results_db.total_amount,
                'last_updated':results_db.last_updated.isoformat() if getattr(results_db , 'last_updated',None) else None,
            }

            return jsonify({'status':True,'order_information':order_data}),200
        except DatabaseError as dbe:
            return jsonify({'status':False,'message':f"{dbe}"}),400
        except ValueError as ve:
            return jsonify({'status':False,'message':f"{ve}"}),400
        except Exception as e:
            return jsonify({'status':False,'message':f"{e}"}),400



