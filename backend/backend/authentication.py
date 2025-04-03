from rest_framework_simplejwt.authentication import JWTAuthentication

# from .helper import *
from django.conf import settings
from bson import ObjectId
from rest_framework_simplejwt.exceptions import InvalidToken


class SimpleUser:
    def __init__(self, user_data):
        self._id = user_data.get('_id')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.subscription = user_data.get('subscription', False)
        self.password = user_data.get('password')
        self.admin = user_data.get('admin', False)
        self.otp = user_data.get('otp')

        self.is_authenticated = True  # Ensure this attribute is available

    def __str__(self):
        return self.name


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token['user_id']
        # print(f"---------------------User ID from token: {user_id}")  # Debugging statement
        collection = settings.MONGO_DB['users']
        user = collection.find_one({'_id': ObjectId(user_id)})
        # print(f"------------------------User from MongoDB: {user}")  # Debugging statement
        if not user or user.get('is_blocked') :
            raise InvalidToken('User not found')

        # Return a user-like object
        return SimpleUser(user)