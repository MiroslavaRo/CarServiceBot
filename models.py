"""Modules"""
class User:
    """Creates class User that contains attributes"""
    def __init__(self, name):
        self.name = name
        self.phone = None
        self.email = None


class Car:
    """Creates class Car that contains attributes"""
    def __init__(self, user):
        self.user = user
        self.brand = None
        self.model = None
        self.year = None
        self.engine = None
        self.car_id = None
        self.tech_passport = None

class Service:
    """Creates class Service that contains attributes"""
    def __init__(self, name):
        self.name = name
        self.price = None

class Apointment:
    """Creates class Apointment that contains attributes"""
    def __init__(self, user):
        self.user = user
        self.car = None
        self.service = None
        self.service_name = None
        self.comments = None
        self.app_date = None
        self.photo = None
        self.app_id = None

user_dict = {}
car_dict = {}
services_dict = {}
apps_dict = {}
