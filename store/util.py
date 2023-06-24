import json
from flask import Response
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from functools import wraps

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

def roleCheck(role):
    def decorator(function):
        @jwt_required()
        @wraps(function)
        def wrapper(*args,**kwargs):
            claims = get_jwt()
            if(role in claims['roles']):
                return function (*args, **kwargs)
            else:
                return Response(json.dumps({'msg': 'Missing Authorization Header'}), 401)
        return wrapper
    return decorator