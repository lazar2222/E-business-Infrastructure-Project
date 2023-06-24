import json
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity

from config import Config

from models import database, Order

from util import roleCheck, errorMessage

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

@application.route('/orders_to_deliver', methods = ['GET'])
@roleCheck('courier')
def toDeliver():
    orders = Order.query.filter(Order.status == 'CREATED').all()
    orders = {'orders':[{'id':order.id, 'email':order.customer} for order in orders]}

    return Response(json.dumps(orders))

@application.route('/pick_up_order', methods = ['POST'])
@roleCheck('courier')
def pickUp():
    if 'id' not in request.json:
        return errorMessage('Missing order id.')    
    id = request.json['id']
    order = Order.query.filter(Order.id == id).first()
    if order == None or order.courier != None:
        return errorMessage('Invalid order id.')
    
    order.status = 'PENDING'
    order.courier = get_jwt_identity()
    database.session.commit()

    return Response(None, 200)

if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)