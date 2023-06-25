import csv
import json
import os
import subprocess
import time
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from sqlalchemy import func, desc, literal

from config import Config

from models import database, Product, Category, Order, ProductCategory, ProductOrder

from util import roleCheck, errorMessage

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

@application.route('/update', methods = ['POST'])
@roleCheck('owner')
def update():
    if 'file' not in request.files:
        return errorMessage(f'Field file is missing.')

    jobs = []
    lineno = 0
    str = request.files['file'].stream.read().decode()
    for row in csv.reader(str.splitlines()):
        if len(row) != 3:
            return errorMessage(f'Incorrect number of values on line {lineno}.')
        categories = row[0].split('|')
        name = row[1]
        try:
            price = float(row[2])
            if price <= 0:
                return errorMessage(f'Incorrect price on line {lineno}.')
        except:
            return errorMessage(f'Incorrect price on line {lineno}.')
        if Product.query.filter(Product.name == name).count() > 0:
            return errorMessage(f'Product {name} already exists.')
        
        jobs.append((name, price, categories))
        lineno += 1
    
    for job in jobs:
        name, price, categories = job
        mappedCategories = []
        for category in categories:
            cat = Category.query.filter(Category.name == category).all()
            if len(cat) != 1:
                cat = Category(category)
                database.session.add(cat)
                database.session.commit()
            else:
                cat = cat[0]
            mappedCategories.append(cat)
        product = Product(name, price)
        database.session.add(product)
        database.session.commit()
        for mappedCategory in mappedCategories:
            pc = ProductCategory(product.id, mappedCategory.id)
            database.session.add(pc)
        database.session.commit()

    return Response(None, 200)

@application.route('/product_statistics', methods = ['GET'])
@roleCheck('owner')
def productStatistics():
    #SELECT Count(*) from products join productOrder join order where status group by product having count > 0
    if Config.USE_SPARK:
        os.environ['SPARK_APPLICATION_PYTHON_LOCATION'] = '/app/productStatSpark.py'
        os.environ['SPARK_SUBMIT_ARGS'] = '--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar'
        file = f'/app/{time.time()}.txt'
        os.environ['SPARK_APPLICATION_ARGS'] = file
        result = subprocess.check_output (['/template.sh'])
        print(result.decode())
        with open(file, 'r') as fd:
            result = fd.read()
        os.remove(file)
        print(result)
        return Response(result)
    else:
        sold = database.session.query(Product.name, func.sum(ProductOrder.quantity)).select_from(Product).join(ProductOrder).join(Order).filter(Order.status == 'COMPLETE').group_by(Product.name).having(func.sum(ProductOrder.quantity) > 0).all()
        waiting = database.session.query(Product.name, func.sum(ProductOrder.quantity)).select_from(Product).join(ProductOrder).join(Order).filter(Order.status != 'COMPLETE').group_by(Product.name).having(func.sum(ProductOrder.quantity) > 0).all()
        products = list(set([s[0] for s in sold] + [w[0] for w in waiting]))
        statistics = []
        for product in products:
            s = 0
            w = 0
            for so in sold:
                if so[0] == product:
                    s = so[1]
            for wa in waiting:
                if wa[0] == product:
                    w = wa[1]
            statistics.append({'name':product, 'sold':int(s), 'waiting': int(w)})
        #statistics = database.session.query(Product.name, func.sum(case((Order.status == 'COMPLETE', ProductOrder.quantity), else_ = 0)), func.sum(case((Order.status != 'COMPLETE'), else_ = 0))).select_from(Product).join(ProductOrder).join(Order).group_by(Product.name).having(func.sum(ProductOrder.quantity) > 0).all()
        #statistics = [{'name':s[0], 'sold':s[1], 'waiting': s[2]} for s in statistics]
        return Response(json.dumps({'statistics':statistics}))

@application.route('/category_statistics', methods = ['GET'])
@roleCheck('owner')
def categoryStatistics():
    #SELECT name sum(quantity) from categories join products join product order join order where status = COMPLETE group by category.id order by sum(quantity) desc, name asc
    if Config.USE_SPARK:
        os.environ['SPARK_APPLICATION_PYTHON_LOCATION'] = '/app/categoryStatSpark.py'
        os.environ['SPARK_SUBMIT_ARGS'] = '--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar'
        file = f'/app/{time.time()}.txt'
        os.environ['SPARK_APPLICATION_ARGS'] = file
        result = subprocess.check_output (['/template.sh'])
        print(result.decode())
        with open(file, 'r') as fd:
            result = fd.read()
        os.remove(file)
        print(result)
        return Response(result)
    else:
        categories = database.session.query(Category.name.label('name'), func.sum(ProductOrder.quantity).label('val')).select_from(Category).join(ProductCategory).join(Product).join(ProductOrder).join(Order).filter(Order.status == 'COMPLETE').group_by(Category.name).order_by(desc('val'), 'name').all()
        allCat = database.session.query(Category.name).select_from(Category).order_by(Category.name).all()
        categories = [c[0] for c in categories]
        for c in allCat:
            if c[0] not in categories:
                categories.append(c[0])
        return Response(json.dumps({'statistics':categories}))

if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)