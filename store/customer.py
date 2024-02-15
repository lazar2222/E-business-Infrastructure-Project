import json
import time
import datetime
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_
from web3 import Web3
from web3 import HTTPProvider
from web3 import Account
from web3.exceptions import ContractLogicError

from config import Config

from models import database, Product, Category, Order, ProductCategory, ProductOrder

from util import roleCheck, verify, errorMessage

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

if Config.USE_ETH:
    w3 = Web3(HTTPProvider(Config.ETH_URL))

@application.route('/search', methods = ['GET'])
@roleCheck('customer')
def search():
    name = request.args['name'] if 'name' in request.args else ''
    cat = request.args['category'] if 'category' in request.args else ''
    productsCategories = database.session.query(Product.name, Category.name).select_from(Product).join(ProductCategory).join(Category).filter(and_(Product.name.like(f'%{name}%'), Category.name.like(f'%{cat}%'))).distinct().all()
    products = list(set([s[0] for s in productsCategories]))
    categories = list(set([s[1] for s in productsCategories]))
    products = [Product.query.filter(Product.name == s).first() for s in products]
    products = [{'categories':[c.name for c in p.categories], 'id':p.id, 'name':p.name, 'price':p.price} for p in products]
    return Response(json.dumps({'categories':categories, 'products':products}))

@application.route('/order', methods = ['POST'])
@roleCheck('customer')
def order():
    FIELDS = ['requests']
    res = verify(request, FIELDS)
    if isinstance(res, Response):
        return res
    
    products = res[0]

    productNo = 0
    jobs = []
    for product in products:
        if 'id' not in product:
            return errorMessage(f'Product id is missing for request number {productNo}.')
        if 'quantity' not in product:
            return errorMessage(f'Product quantity is missing for request number {productNo}.')
        try:
            id = int(product['id'])
            if id <= 0:
                return errorMessage(f'Invalid product id for request number {productNo}.')
        except:
            return errorMessage(f'Invalid product id for request number {productNo}.')
        try:
            quantity = int(product['quantity'])
            if quantity <= 0:
                return errorMessage(f'Invalid product quantity for request number {productNo}.')
        except:
            return errorMessage(f'Invalid product quantity for request number {productNo}.')
        productObj = Product.query.filter(Product.id == id).first()
        if productObj == None:
            return errorMessage(f'Invalid product for request number {productNo}.')

        jobs.append((productObj, quantity))
        productNo += 1

    price = 0
    for job in jobs:
        product, quantity = job
        price += product.price * quantity

    cA = '0'
    if Config.USE_ETH:
        if 'address' not in request.json or len(request.json['address']) == 0:
            return errorMessage('Field address is missing.')
        address = request.json['address']
        if not w3.is_address(address):
            return errorMessage('Invalid address.')
        with open('Delivery.abi', 'r') as file:
            abi = file.read()
        with open('Delivery.bin', 'r') as file:
            bin = file.read()
        contract = w3.eth.contract( bytecode = bin, abi = abi)
        transaction = contract.constructor(address, int(price*100)).build_transaction({'from': Config.OWNER_PUBLIC, 'nonce': w3.eth.get_transaction_count(Config.OWNER_PUBLIC), 'gasPrice': 21000})
        signed = w3.eth.account.sign_transaction(transaction, Config.OWNER_PRIVATE)
        transaction = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(transaction)
        cA = receipt.contractAddress

    email = get_jwt_identity()
    timestamp = time.time()
    order = Order(price, 'CREATED', timestamp, email, cA)
    database.session.add(order)
    database.session.commit()

    for job in jobs:
        product, quantity = job
        po = ProductOrder(product.id, order.id, quantity)
        database.session.add(po)

    database.session.commit()

    return Response(json.dumps({'id':order.id}))

@application.route('/status', methods = ['GET'])
@roleCheck('customer')
def status():
    email = get_jwt_identity()
    orders = Order.query.filter(Order.customer == email).all()
    orders = {'orders':[{'products':[{'categories':[category.name for category in product.product.categories], 'name':product.product.name, 'price':product.product.price, 'quantity':product.quantity} for product in order.products], 'price':order.price, 'status':order.status, 'timestamp':datetime.datetime.fromtimestamp(order.timestamp).isoformat()+'Z'} for order in orders]}

    return Response(json.dumps(orders))

@application.route('/delivered', methods = ['POST'])
@roleCheck('customer')
def delivered():
    if 'id' not in request.json:
        return errorMessage('Missing order id.')    
    id = request.json['id']
    order = Order.query.filter(Order.id == id).first()
    if order == None or order.courier == None:
        return errorMessage('Invalid order id.')
    if order.customer != get_jwt_identity():
        return Response(json.dumps({'msg': 'Missing Authorization Header'}), 401)
    
    if Config.USE_ETH:
        if 'keys' not in request.json or len(request.json['keys']) == 0:
            return errorMessage('Missing keys.')
        if 'passphrase' not in request.json or len(request.json['passphrase']) == 0:
            return errorMessage('Missing passphrase.')
        keys = request.json['keys']
        keys = keys.replace('\'','"')
        keys = json.loads(keys)
        passphrase = request.json['passphrase']
        address = w3.to_checksum_address(keys['address'])
        try:
            private_key = Account.decrypt(keys, passphrase).hex()
        except:
            return errorMessage('Invalid credentials.')
        with open('Delivery.abi', 'r') as file:
            abi = file.read()
        contract = w3.eth.contract(address = order.contractAddress, abi = abi)
        try:
            transaction = contract.functions.delivered().build_transaction({'from': address, 'nonce': w3.eth.get_transaction_count(address), 'gasPrice': 21000})
            signed = w3.eth.account.sign_transaction(transaction, private_key)
            transaction = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(transaction)
        except ContractLogicError as er:
            if 'Address' in str(er):
                return errorMessage('Invalid customer account.')
            if 'CREATED' in str(er):
                return errorMessage('Transfer not complete.')
            if 'PAID' in str(er):
                return errorMessage('Delivery not complete.')
            print(er)
            return errorMessage('AAAAAAAAAAAAAAAAAAAAAAAA')

    order.status = 'COMPLETE'
    database.session.commit()

    return Response(None, 200)

@application.route('/pay', methods = ['POST'])
@roleCheck('customer')
def pay():
    if 'id' not in request.json:
        return errorMessage('Missing order id.')    
    id = request.json['id']
    order = Order.query.filter(Order.id == id).first()
    if order == None:
        return errorMessage('Invalid order id.')
    if order.customer != get_jwt_identity():
        return Response(json.dumps({'msg': 'Missing Authorization Header'}), 401)
    
    if Config.USE_ETH:
        if 'keys' not in request.json or len(request.json['keys']) == 0:
            return errorMessage('Missing keys.')
        if 'passphrase' not in request.json or len(request.json['passphrase']) == 0:
            return errorMessage('Missing passphrase.')
        keys = request.json['keys']
        keys = json.loads(keys)
        passphrase = request.json['passphrase']
        address = w3.to_checksum_address(keys['address'])
        try:
            private_key = Account.decrypt(keys, passphrase).hex()
        except:
            return errorMessage('Invalid credentials.')
        with open('Delivery.abi', 'r') as file:
            abi = file.read()
        contract = w3.eth.contract(address = order.contractAddress, abi = abi)
        try:
            transaction = contract.functions.pay().build_transaction({'from': address, 'nonce': w3.eth.get_transaction_count(address), 'gasPrice': 21000, 'value': int(order.price*100)})
            signed = w3.eth.account.sign_transaction(transaction, private_key)
            transaction = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(transaction)
        except ContractLogicError as er:
            if 'Value' in str(er):
                return errorMessage('Insufficient funds.')
            if 'PAID' in str(er):
                return errorMessage('Transfer already complete.')
            if 'COURIER_ASSIGNED' in str(er):
                return errorMessage('Transfer already complete.')
            if 'DELIVERED' in str(er):
                return errorMessage('Transfer already complete.')
            print(er)
            return errorMessage('AAAAAAAAAAAAAAAAAAAAAAAA')

    return Response(None, 200)


if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)