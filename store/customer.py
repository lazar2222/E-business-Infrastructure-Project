import json
import time
import datetime
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_

from config import Config

from models import database, Product, Category, Order, ProductCategory, ProductOrder

from util import roleCheck, verify, errorMessage

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

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

    email = get_jwt_identity()
    price = 0
    timestamp = time.time()
    order = Order(price, 'CREATED', timestamp, email)
    database.session.add(order)
    database.session.commit()

    for job in jobs:
        product, quantity = job
        price += product.price * quantity
        po = ProductOrder(product.id, order.id, quantity)
        database.session.add(po)

    database.session.commit()

    order.price = price

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
    
    order.status = 'COMPLETE'
    database.session.commit()

    return Response(None, 200)


if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)