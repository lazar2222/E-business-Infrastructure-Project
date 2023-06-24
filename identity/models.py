from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    id        = database.Column(database.Integer, primary_key = True)
    email     = database.Column(database.String(256), nullable = False, unique = True)
    password  = database.Column(database.String(256), nullable = False)
    firstName = database.Column(database.String(256), nullable = False)
    lastName  = database.Column(database.String(256), nullable = False)
    role      = database.Column(database.String(256), nullable = False)

    def __init__(self, firstName, lastName, email, password, role):
        self.email = email
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.role = role