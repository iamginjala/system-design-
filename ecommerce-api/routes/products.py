from flask import Blueprint,request,jsonify
from utils.database import SessionLocal
from models.product import Products,UUID
from utils.cache import get_data,set_data
from sqlalchemy.exc import DatabaseError

stocks = Blueprint('products',__name__,url_prefix='/api')

@stocks.route('/product/<product_id>',methods=['GET'])
def get_product_details(product_id):
    try:
        cached_data = get_data(product_id)
        if isinstance(cached_data,dict): # vlaid data found
            return jsonify({'status':True,'data':cached_data,'source':'cache'}),200
        with SessionLocal() as db:
            result_db = db.query(Products).filter(Products.product_id== UUID(product_id)).first()
            if not result_db:
                return jsonify({'status':False,'error':'No datafound for this product_id'}),404
            prod_data = {'product_id':str(result_db.product_id),
                         'stock_count':result_db.stock_count,
                         'price':result_db.price,
                         'last_updated':result_db.last_updated.isoformat() if getattr(result_db, 'last_updated', None) else None}
            set_data(product_id,prod_data)
            return jsonify({'status': True,'data': prod_data,'source':'Database'}),200
    except DatabaseError as dbe:
        return jsonify({'status':False,'error':{'message':'Database Error','response':str(dbe)[:100]}}),400
    except ValueError as VE:
        return jsonify({'status':False,'error': "Not a valid product_id"}),400
    except Exception as e:
        return jsonify({'status': False, 'message': f"found an unexpected response {e}"}),500
        