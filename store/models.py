from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class ProductCategory(database.Model):
    id         = database.Column(database.Integer, primary_key = True)
    productId  = database.Column(database.Integer, database.ForeignKey('product.id'), nullable = False)
    categoryId = database.Column(database.Integer, database.ForeignKey('category.id'), nullable = False)

    def __init__(self, productId, categoryId):
        self.productId = productId
        self.categoryId = categoryId

class ProductOrder(database.Model):
    id        = database.Column(database.Integer, primary_key = True)
    productId = database.Column(database.Integer, database.ForeignKey('product.id'), nullable = False)
    orderId   = database.Column(database.Integer, database.ForeignKey('order.id'), nullable = False)
    quantity  = database.Column(database.Integer, nullable = False)

    product = database.relationship('Product', back_populates = 'orders')
    order = database.relationship('Order', back_populates = 'products')

    def __init__(self, productId, orderId, quantity):
        self.productId = productId
        self.orderId = orderId
        self.quantity = quantity

class Product(database.Model):
    id    = database.Column(database.Integer, primary_key = True)
    name  = database.Column(database.String(256), nullable = False, unique = True)
    price = database.Column(database.Double, nullable = False)

    categories = database.relationship('Category', secondary = ProductCategory.__table__, back_populates = 'products' )
    orders = database.relationship('ProductOrder', back_populates = 'product')

    def __init__(self, name, price):
        self.name = name
        self.price = price

class Category(database.Model):
    id   = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), nullable = False, unique = True)

    products = database.relationship('Product', secondary = ProductCategory.__table__, back_populates = 'categories' )

    def __init__(self, name):
        self.name = name

class Order(database.Model):
    id              = database.Column(database.Integer, primary_key = True) 
    status          = database.Column(database.String(256), nullable = False)
    timestamp       = database.Column(database.Integer, nullable = False)
    price           = database.Column(database.Double, nullable = False)
    customer        = database.Column(database.String(256), nullable = False)
    courier         = database.Column(database.String(256))
    contractAddress = database.Column(database.String(256), nullable = False)

    products = database.relationship('ProductOrder', back_populates = 'order')

    def __init__(self, price, status, timestamp, customer, address):
        self.status = status
        self.price = price
        self.timestamp = timestamp
        self.customer = customer
        self.courier = None
        self.contractAddress = address