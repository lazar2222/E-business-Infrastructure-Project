import json
import re
from flask import Flask
from flask import request
from flask import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from sqlalchemy       import and_

from config import Config

from models import database, User

application = Flask(__name__)
application.config.from_object(Config)

database.init_app(application)
jwt = JWTManager(application)

def verify(request, fields):
    retList = []
    for field in fields:
        if field not in request.json or len(request.json[field]) == 0:
            return errorMessage(f'Field {field} is missing.')
        else:
            retList.append(request.json[field])
    return retList

def errorMessage(string):
    return Response(json.dumps({'message': string}), 400)

@application.route('/register_customer', methods = ['POST'])
def registerCustomer():
    return register(request, 'customer')

@application.route('/register_courier', methods = ['POST'])
def registerCourier():
    return register(request, 'courier')

def register(request, role):
    FIELDS = ['forename', 'surname', 'email', 'password']
    res = verify(request, FIELDS)
    if isinstance(res, Response):
        return res
    
    regex = '^[a-zA-Z0-9.-_]+@[a-zA-Z0-9]+\.[a-z]{2,3}$'
    if not re.match(regex, res[2]):
        return errorMessage('Invalid email.')

    if len(res[3]) < 8:
        return errorMessage('Invalid password.') 

    if User.query.filter(User.email == res[2]).count() > 0:
        return errorMessage('Email already exists.')

    res.append(role)
    user = User(*res)
    database.session.add(user)
    database.session.commit()
    return Response(None, 200)

@application.route('/login', methods = ['POST'])
def login():
    FIELDS = ['email', 'password']
    res = verify(request, FIELDS)
    if isinstance(res, Response):
        return res
    
    regex = '^[a-zA-Z0-9.-_]+@[a-zA-Z0-9]+\.[a-z]{2,3}$'
    if not re.match(regex, res[0]):
        return errorMessage('Invalid email.')
    
    user = User.query.filter(and_(User.email == res[0], User.password == res[1])).all()
    if len(user) != 1:
        return errorMessage('Invalid credentials.')
    else:
        user = user[0]
    
    additionalClaims = {'forename': user.firstName, 'surname':user.lastName, 'roles': [user.role]}
    token = create_access_token(user.email, additional_claims = additionalClaims)
    return Response(json.dumps({'accessToken':token}))


@application.route('/delete', methods = ['POST'])
@jwt_required()
def delete():
    email = get_jwt_identity()

    user = User.query.filter(User.email == email).all()
    if len(user) != 1:
        return errorMessage('Unknown user.')
    else:
        user = user[0]

    database.session.delete(user)
    database.session.commit()

    return Response(None, 200)

if __name__ == '__main__':
    application.run('0.0.0.0', 5000, True)