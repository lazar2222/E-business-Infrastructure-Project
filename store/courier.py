import json
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from web3 import Web3
from web3 import HTTPProvider
from web3 import Account

from config import Config

from models import database, Order

from util import roleCheck, errorMessage

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

if Config.USE_ETH:
    w3 = Web3(HTTPProvider(Config.ETH_URL))

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
    
    if Config.USE_ETH:
        if 'address' not in request.json or len(request.json['address']) == 0:
            return errorMessage('Missing address.')
        address = request.json['address']
        if not w3.is_address(address):
            return errorMessage('Invalid address.')
        with open('Delivery.abi', 'r') as file:
            abi = file.read()
        contract = w3.eth.contract(address = order.contractAddress, abi = abi)
        contract.functions.assignCourier(address).transact({'from': Config.OWNER_PUBLIC})

    order.status = 'PENDING'
    order.courier = get_jwt_identity()
    database.session.commit()

    return Response(None, 200)

if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)