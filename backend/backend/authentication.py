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
        self.subscription = user_data.get('subscription', None)
        self.password = user_data.get('password')
        self.phone_number = user_data.get('phone_number')
        self.joined = user_data.get('joined')
        self.admin = user_data.get('admin', None)
        self.faculty_member = user_data.get('faculty_member', None)
        self.otp = user_data.get('otp')
        self.subscribed_user_seats_left = user_data.get('subscribed_user_seats_left', None)
        self.faculty_member_boss = user_data.get('faculty_member_boss', None)
        self.institution = user_data.get('institution', None)

        if self.faculty_member is not None:
            self.faculty_member_program = user_data.get('faculty_member_program', [])
            self.faculty_member_semester = user_data.get('faculty_member_semester', [])
            self.faculty_member_subject = user_data.get('faculty_member_subject', [])
            self.faculty_member_timing = user_data.get('faculty_member_timing', [])
        else:
            self.faculty_member_program = None
            self.faculty_member_semester = None
            self.faculty_member_subject = None
            self.faculty_member_timing = None

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