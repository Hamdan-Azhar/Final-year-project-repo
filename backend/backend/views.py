from google.cloud import storage
from datetime import datetime, timedelta
from django.conf import settings
import modal
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from .helper import *
from .authentication import CustomJWTAuthentication
from bson import ObjectId
import random
from backend.permissions import *
from google.oauth2 import service_account
from re import match

class UserLoginView(APIView):
    def options(self, request, *args, **kwargs):
        """
        Handle OPTIONS request for CORS preflight
        """
        response = Response()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def post(self, request):
        """
        Handle user login with email and password
        """
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return Response(
                    {'error': 'Email and password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            collection = settings.MONGO_DB['users']
            user = collection.find_one({'email': email})
            
            if not user:
                return Response(
                    {'error': 'Invalid email or password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Password comparison (consider using proper password hashing)
            if password != user.get('password'):
                return Response(
                    {'error': 'Invalid email or password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if user.get('blocked'):
                return Response(
                    {'error': 'You need to verify your email first', 'needs_verification': True},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Generate JWT tokens
            tokens = generate_jwt_tokens(user)
            print("subscription", tokens['is_subscribed'])
            return Response({
                'message': 'Login successful',
                'user_id': tokens['user_id'],
                'subscription': tokens['is_subscribed'],
                'admin': tokens['is_admin'],
                'faculty': tokens['is_faculty'],
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
class UserSignUpView(APIView):
    def post(self, request):
        try:
            data = request.data
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            phone_number = data.get('phoneNo')
            role = data.get('role')
            institution = data.get('institution')
            location = data.get('location')

            if not name or not email or not password or not phone_number or not role: 
                return Response({'error': 'Name, email, password, phone number and role are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password strength
            password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$'
            if not match(password_regex, password):
                return Response({
                    'error': 'Password must be 8-20 characters long and contain at least one uppercase letter, one lowercase letter, and one number.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Optional confirm password match if provided
            if confirm_password and password != confirm_password:
                return Response({'error': 'Password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate Pakistan phone number format
            phone_regex = r'^(\+92|0092|0)?(3\d{2})(\d{7})$'
            if not match(phone_regex, phone_number):
                return Response({'error': 'Invalid Pakistan phone number format.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate role
            if role not in ['user', 'admin']:
                return Response({'error': 'Role must be either "user" or "admin".'}, status=status.HTTP_400_BAD_REQUEST)

            collection = settings.MONGO_DB['users']
            existing_user = collection.find_one({'email': email})
            existing_user_with_phone = collection.find_one({'phone_number': phone_number})

            if existing_user_with_phone:
                # check if user is blocked
                if not existing_user_with_phone.get('blocked'):
                    return Response({'error': 'A user with this phone number already exists.'}, status=status.HTTP_409_CONFLICT)
        
            # check if user exists
            if existing_user:
                # check if user is blocked
                if not existing_user.get('blocked'):
                    return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_409_CONFLICT)
                
            hashed_password = password
            otp = random.randint(100000, 999999)  # 6-digit OTP
            otp_expires_at = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            if existing_user:
                if existing_user.get('name') == name and existing_user.get('email') == email and existing_user.get('phone_number') == phone_number and existing_user.get('password') == hashed_password:
                    collection.update_one(
                        {'email': email},
                        {
                            '$set': {
                                'otp': otp, 
                                'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                                'otp_attempts': 0  # Track failed attempts
                            }
                        }
                    )
                else:
                    return Response({'error': 'A user with this email already exists. Kindly enter correct details for email verification'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if role == 'user':
                    user_document = {
                        'name': name,
                        'email': email,
                        'password': hashed_password,
                        'institution': institution,
                        'location': location,
                        'phone_number': phone_number,
                        'subscription': False,
                        'otp': otp,
                        'blocked': True,
                        'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_attempts': 0  # Track failed attempts
                    }
                else:
                    user_document = {
                        'name': name,
                        'email': email,
                        'password': hashed_password,
                        'institution': institution,
                        'location': location,
                        'phone_number': phone_number,
                        'admin': True,
                        'otp': otp,
                        'blocked': True,
                        'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_attempts': 0  # Track failed attempts
                    }
                
                collection.insert_one(user_document)
            
            # Send OTP via email
            try:
                subject = 'Your account verification email'
                message = f'Your OTP is: {otp}. It will expire in 5 minutes.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            return Response({
                'message': 'OTP sent to email.',
                'otp_expires_in': 300  # 5 minutes in seconds
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )
    

class DeleteUserView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def delete(self, request, email):
        try:
            if not email:
                return Response({'error': 'Video ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the subscription field in the users table
            users_collection = settings.MONGO_DB['users']

            user = users_collection.find_one({'email': email})

            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            name = user.get('name', 'User')
            users_collection.delete_one({'email': email})

            # Compose email
            subject = 'Subscription Status Updated'
            message = f"Hello {name},\n\nYour account has been deleted. Kindly reply to this email for reasons.\n\nThank you!"
           
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            return Response({'message': 'User Deleted Successfully.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Failed to remove user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOtpView(APIView):
    def post(self, request):
        try:
            data = request.data
            otp = data.get('otp')
            email = data.get('email')  # Email should be passed from frontend
            
            if not otp or not email:
                return Response(
                    {'error': 'OTP and email are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            collection = settings.MONGO_DB['users']
            user = collection.find_one({'email': email})

            if not user:
                return Response(
                    {'error': 'No OTP session found. Please sign up again.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Check if OTP is expired
            otp_expires_at = datetime.strptime(
                user['otp_expires_at'], 
                '%Y-%m-%d %H:%M:%S'
            )
            current_time = datetime.now()
            if current_time > otp_expires_at:
                # Clear the expired OTP
                print("triggered otp expires")
                collection.update_one(
                    {'email': email},
                    {
                        '$unset': {
                            'otp': 1, 
                            'otp_created_at': 1, 
                            'otp_expires_at': 1
                        }
                    }
                )
                return Response(
                    {'error': 'OTP has expired. Please request a new one.'},
                    status=status.HTTP_410_GONE
                )
            
         
            # Verify OTP
            if str(user.get('otp')) != str(otp):
                print("triggered otp not equal")
                # Increment failed attempts
                collection.update_one(
                    {'email': email},
                    {'$inc': {
                        'otp_attempts': 1
                        }
                    }
                )
                
                # Check if exceeded max attempts
                if user.get('otp_attempts', 0) >= 3:

                    collection.update_one(
                        {'email': email},
                        {
                            '$unset': {
                                'otp': 1, 
                                'otp_created_at': 1, 
                                'otp_expires_at': 1,
                                'otp_attempts': 1
                            }
                        }
                    )
                   
                    return Response(
                        {'error': 'Maximum attempts reached. Please request a new OTP.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                
                return Response(
                    {'error': 'Invalid OTP. Attempts remaining: {}'.format(
                        3 - user.get('otp_attempts', 0)
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Successful verification
            collection = collection.update_one(
                {'email': email},
                {
                    '$unset': {
                        'otp': 1, 
                        'otp_created_at': 1, 
                        'otp_expires_at': 1,
                        'otp_attempts': 1,
                        'blocked': True,
                    },
                    "$set": {
                        "joined" : datetime.today().date().strftime('%Y-%m-%d'),
                    }
                },
            )
            
            tokens = generate_jwt_tokens(user)     # generate JWT tokens
            return Response(
                {
                    'message': 'OTP verified successfully',
                    'access_token': tokens["access"],  
                    'refresh_token': tokens["refresh"]
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class ResendOtpView(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')

            if not email:
                return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)

            collection = settings.MONGO_DB['users']
        
            otp = random.randint(100000, 999999)  # 6-digit OTP
            otp_expires_at = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            updated_result = collection.update_one(
                {'email': email},
                {
                    '$set': {
                        'otp': otp, 
                        'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'otp_attempts': 0  # Track failed attempts
                    }
                }
            )

            if updated_result.modified_count == 0:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

            # Send OTP via email
            try:
                subject = 'Your account verification email'
                message = f'Your OTP is: {otp}. It will expire in 5 minutes.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            response = Response({
                'message': 'User created successfully. OTP sent to email.',
                'otp_expires_in': 300  # 5 minutes in seconds
            }, status=status.HTTP_201_CREATED)
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# google storage 
class UploadVideoView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsUnsubscribedOrFaculty]
    
    def post(self, request):
        try:
            # Check if a video file is included in the request
            model_type = request.data.get('model_type', None)
            subject = request.data.get('subject', None)
            exam_type = request.data.get('exam_type', None)

            if 'video_file' not in request.FILES:
                # print("---video_file----")
                return Response({'error': 'No video file provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # current authenticated user
            user = request.user
            user_id = user._id
            video_file = request.FILES['video_file']

            # Initialize GCS client
            credentials = service_account.Credentials.from_service_account_info(settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = storage.Client(credentials=credentials)
            bucket = client.bucket(settings.GCS_BUCKET_NAME)

            # Generate a unique filename for the video
            video_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.name}"

            # Upload the video to GCS
            blob = bucket.blob(video_filename)
            blob.upload_from_file(video_file, rewind=True)

            # Get the public URL of the uploaded video
            video_url = blob.public_url

            # Store the GCS file path, video URL, and user ID in MongoDB
            collection = settings.MONGO_DB['videos']
            date_str = datetime.today().date().strftime('%Y-%m-%d')
            
            try:
                # Send the video file for classification
                if model_type != "Deep Learning Model" or model_type == None:
                    classification_func = modal.Function.from_name(settings.MODAL_APP, settings.ML_MODEL_FUNCTION)
                else:
                    classification_func = modal.Function.from_name(settings.MODAL_APP, settings.DL_MODEL_FUNCTION)

                classification_result = classification_func.remote(video_url)
            except Exception as e:
                # print(f"Error during classification: {str(e)}")
                return Response({'error': f"Error during classification - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if user.subscription == False:
                blob.delete()
                # Return a success response
                return Response({
                    'message': 'Video classified successfully.',
                    'classification': classification_result if classification_result else "no cheating",
                    'video_name': video_filename,
                    'url': video_url,
                }, status=status.HTTP_200_OK)
            else:
                print("bro")
                print("user faculy member subject", user.faculty_member_subject)
                subject_index = user.faculty_member_subject.index(subject)
                print("subject index", subject_index)
                semester = user.faculty_member_semester[subject_index]
                program = user.faculty_member_program[subject_index]
                timing = user.faculty_member_timing[subject_index]
                print("program", program)
                # Store the video document in MongoDB
                video_document = {
                    'user_id': user_id,
                    'video_name': video_filename,
                    'size': round(video_file.size / 1048576, 2),
                    'url': video_url,
                    'classification': classification_result if classification_result else "no cheating",
                    'model_type': model_type,
                    'subject': subject,
                    'exam_type': exam_type,
                    'semester': semester,
                    'program': program,
                    'timing': timing,
                    'date': date_str
                }

                # Insert the video document into the MongoDB collection
                collection.insert_one(video_document)

                # Return a success response
                return Response({
                    'message': 'Video classified and uploaded to GCS successfully.',
                    'classification': classification_result if classification_result else "no cheating",
                    'video_name': video_filename,
                    'url': video_url,
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class VideoView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFaculty]

    def get(self, request, video_id):    
        try:
            print("video id", video_id)
            if not video_id:
                return Response({'error': 'Video ID is required'}, status=status.HTTP_400_BAD_REQUEST)

             # Get the registered user
            user = request.user
            user_id = user._id

            # Access the MongoDB collection
            collection = settings.MONGO_DB['videos']

            # Find the video document associated with the user and video_name
            video = collection.find_one({'video_name': video_id, 'user_id': ObjectId(user_id)})
            if not video:
                return Response({'error': 'Video not found or not owned by the user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Return the video URL in the response
            return Response({'url': video.get('url'), 'classification': video.get('classification'), 'model_type': video.get('model_type')}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, video_id):
        try:
            print("video id", video_id)
            if not video_id:
                return Response({'error': 'Video ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the registered user
            user = request.user
            user_id = user._id

            # Access the MongoDB collection
            collection = settings.MONGO_DB['videos']

            # Find the video document associated with the user and video_name
            video = collection.find_one({'video_name': video_id, 'user_id': ObjectId(user_id)})
            if not video:
                return Response({'error': 'Video not found or not owned by the user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize GCS client
            credentials = service_account.Credentials.from_service_account_info(settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = storage.Client(credentials=credentials)
            # client = storage.Client.from_service_account_json(settings.GCS_CREDENTIALS_PATH)
            bucket = client.bucket(settings.GCS_BUCKET_NAME)

            # Delete the video from GCS
            blob = bucket.blob(video_id)
            blob.delete()

            # Remove the video document from MongoDB
            collection.delete_one({'_id': video['_id']})

            # Return a success response
            return Response({'message': 'Video deleted successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetVideosView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFaculty]

    def get(self, request):
        user = request.user  # Assuming user authentication is done
        user_id = user._id
      
        # Fetch all videos for the user
        video_collection = settings.MONGO_DB['videos']

        videos = video_collection.find({'user_id': ObjectId(user_id)})
        total_size_mb = 0.0
        video_data = []

        for video in videos:
            url = video.get('url')
            video_name = video.get('video_name', 'Unknown')
            total_size_mb += video.get('size', 0)

            video_data.append({
                'name': video_name,
                'size': f"{video.get('size', 0):.2f} MB",
                'url': url,
                'date': video.get('date', 0),
                'subject': video.get('subject', 'Unknown'),
                'exam_type': video.get('exam_type', 'Unknown'),
                'semester': video.get('semester', 'Unknown'),
                'program': video.get('program', 'Unknown'),
                'timing': video.get('timing', 'Unknown'),
            })
        total_storage_gb = 10  # 50 GB
        total_storage_mb = total_storage_gb * 1024  # Convert GB to MB
        used_storage_mb = total_size_mb  # Sum all video sizes
        remaining_storage_gb = (total_storage_mb - used_storage_mb) / 1024
        used_storage_gb = used_storage_mb / 1024

        return Response({
            'cloud_storage': {
                    'used': f'{used_storage_gb:.2f} GB',
                    'remaining': f'{remaining_storage_gb:.2f} GB',
                    'total': f'{total_storage_gb} GB',
                            },
            'videos': video_data,
                            }, status=status.HTTP_200_OK)
    

class GetAllVideosView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            # Fetch all videos for the user
            videos_collection = settings.MONGO_DB['videos']
            videos = videos_collection.find()

            print("all videos", videos)
            total_size_mb = 0.0
            video_data = []

            for video in videos:
                url = video.get('url')
                video_name = video.get('video_name', 'Unknown')
                total_size_mb += video.get('size', 0)
                date = video.get('date', 0)
                model_type = video.get('model_type', 'Unknown')
                video_data.append({
                    'name': video_name,
                    'size': f"{video.get('size', 0):.2f} MB",
                    'url': url,
                    'date': date,
                    'model_type': model_type,
                    'subject': video.get('subject', 'Unknown'),
                    'exam_type': video.get('exam_type', 'Unknown'),
                    'timing': video.get('timing', 'Unknown'),
                    'semester': video.get('semester', 'Unknown'),
                    'program': video.get('program', 'Unknown'),
                })
            # print("video data", video_data)
            total_storage_gb = 10  # 10 GB
            total_storage_mb = total_storage_gb * 1024  # Convert GB to MB
            used_storage_mb = total_size_mb  # Sum all video sizes
            remaining_storage_gb = (total_storage_mb - used_storage_mb) / 1024
            used_storage_gb = used_storage_mb / 1024

            return Response({
                # 'models': list(model_names if model_names else ""),
                'cloud_storage': {
                        'used': f'{used_storage_gb:.2f} GB',
                        'remaining': f'{remaining_storage_gb:.2f} GB',
                        'total': f'{total_storage_gb} GB',
                                },
                'videos': video_data,
                                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
            
class GetUsersView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        user_collection = settings.MONGO_DB['users']
        # Fetch only users where the 'admin' key does not exist
        users = user_collection.find({'admin': {'$exists': False}, 'faculty_member': {'$exists': False}})

        user_data = []
        for user in users:
            user_data.append({
                'name': user.get('name', None),
                'email': user.get('email', None),
                'joined': user.get('joined', None),
                'phone_number': user.get('phone_number', None),
                'subscription': user.get('subscription', 'Inactive'),
                'institution': user.get('institution', None),
                'location': user.get('location', None),
            })
        
        return Response({'users': user_data}, status=status.HTTP_200_OK)
    

class GetUserView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            print("Fucj invoked")
            user = request.user 
            print("users", user)
            print("user name", user.subscribed_user_seats_left)
            print("faculty boss", user.faculty_member_boss)
            print("faculty ", user.faculty_member)
            
            data = {
                'name': user.name,
                'password': user.password,
                'email': user.email,
                # 'phone_number': user.phone_number,
                # 'subscription': user.subscription,
                # 'joined': user.joined,
                # 'admin': user.admin,
                # 'subscribed_user_seats_left': user.subscribed_user_seats_left,
                # 'faculty_member_boss': str(user.faculty_member_boss),
                # 'faculty_member': user.faculty_member
            }

            print("data", data)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
class UpdateUserView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            data = request.data
            print("data", data)
            user = request.user 
            user_id = user._id
            name = data.get('name')
            password = data.get('password')  # Email should be passed from frontend
            confirm_password = data.get('confirm_password')

            if not name or not password:
                return Response(
                    {'error': 'At least name or password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate password strength
            password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$'
            if not match(password_regex, password):
                return Response({
                    'error': 'Password must be 8-20 characters long and contain at least one uppercase letter, one lowercase letter, and one number.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Optional confirm password match if provided
            if confirm_password and password != confirm_password:
                return Response({'error': 'Password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            collection = settings.MONGO_DB['users']
            existing_user = collection.find_one({'_id': ObjectId(user_id)})

            if existing_user.get('name') == name and existing_user.get('password') == password:
                return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
            
            updated_result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'name': name, 'password': password}})

            if updated_result.modified_count == 0:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UpdateSubscriptionView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            action = request.data.get('action')  # 'approve' or 'reject'
            email = request.data.get('email')

            if not action or not email:
                return Response({'error': 'Both action and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

            users_collection = settings.MONGO_DB['users']
            user = users_collection.find_one({'email': email})

            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            name = user.get('name', 'User')

            requests_collection = settings.MONGO_DB['requests']
            requests_collection.delete_one({'email': email})

            if action == 'approve':
                current_status = user.get('subscription', False)
                new_status = not current_status

                users_collection.update_one({'email': email}, {'$set': {'subscription': new_status}})
                if not users_collection.find_one({'email': email, 'subscribed_user_seats_left': {'$exists': True}}):
                    users_collection.update_one(
                        {'email': email},
                        {'$set': {'subscribed_user_seats_left': 10}}
                    )
                # Compose email
                subject = 'Subscription Status Updated'
                if new_status:
                    message = f"Hello {name},\n\nYour subscription request has been approved. You are now subscribed to our premium plan.\n\nThank you!"
                else:
                    message = f"Hello {name},\n\nYour subscription has been removed as per your request. You are no longer subscribed to the premium plan.\n\nThank you!"
            elif action == 'reject':
                subject = 'Subscription Request Rejected'
                message = f"Hello {name},\n\nYour subscription change request has been rejected.\n Kindly reply to this email for further assistance\n\nThank you!"
            else:
                return Response({'error': 'Invalid action type.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            updated_user = users_collection.find_one({'email': email})
            return Response({
                'message': 'Subscription request processed.',
                'subscription': updated_user.get('subscription', None)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({'error': 'Failed to process subscription request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestSubscriptionView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribedOrUnsubscribed]

    def post(self, request):
        try:
            user = request.user
            # Log the request in "requests" collection
            request_document = {
                'name': user.name,
                'email': user.email,
                'phone_number': user.phone_number,
                'joined': user.joined,
                'subscription': user.subscription,
                'action': 'unsubscribe' if user.subscription else 'subscribe',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            requests_collection = settings.MONGO_DB['requests']
            requests_collection.insert_one(request_document)

            return Response({'message': 'Request submitted successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckSubscriptionView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribedOrUnsubscribed]

    def get(self, request):
        try:
            user = request.user
            email = user.email
            subscription_status = user.subscription
            requests_collection = settings.MONGO_DB['requests']
            res = requests_collection.find_one({'email': email})

            if res:
                return Response({
                    'email': email,
                    'subscription': subscription_status,
                    'request_status': 'pending'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'email': email,
                    'subscription': subscription_status,
                    'request_status': 'not_requested'
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllRequestsView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            # Fetch all videos for the user
            requests_collection = settings.MONGO_DB['requests']
            requests = requests_collection.find()

            requests_data = []

            for request in requests:
                requests_data.append({
                    'name': request.get('name', 'Unknown'),
                    'email': request.get('email', 'Unknown'),
                    'phone_number': request.get('phone_number', 'Unknown'),
                    'joined': request.get('joined', 'Unknown'),
                    'subscription': request.get('subscription', 'Unknown'),
                    'action': request.get('action', 'Unknown'),
                    'timestamp': request.get('timestamp', 'Unknown'),
                })
            return Response({
                'requests': requests_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

class GetFacultyMembersView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribed]

    def get(self, request):
        try:
            user = request.user
            id = user._id
            users_collection = settings.MONGO_DB['users']
            faculty_members = users_collection.find({'faculty_member_boss': id})  # Fetch users whose faculty_member_boss field matches the current user's id

            faculty_data = []  # Initialize an empty list to store faculty member data
            for member in faculty_members:
                faculty_data.append({
                    'name': member.get('name', 'Unknown'),
                    'email': member.get('email', 'Unknown'),
                    'password': member.get('password', 'Unknown'),
                    'phone_number': member.get('phone_number', 'Unknown'),
                    'faculty_member_program': member.get('faculty_member_program', ['Unknown']),
                    'faculty_member_semester': member.get('faculty_member_semester', ['Unknown']),
                    'faculty_member_subject': member.get('faculty_member_subject', ['Unknown']),
                    'faculty_member_timing': member.get('faculty_member_timing', ['Unknown'])
                })
                print("sss", user.subscribed_user_seats_left)

            return Response({'faculty': faculty_data, 'remaining_seats':user.subscribed_user_seats_left}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetLoggedInFacultyMemberView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFaculty]

    def get(self, request):
        try:
            user = request.user

            faculty_data = {
                'faculty_member_program': user.faculty_member_program or [],
                'faculty_member_semester': user.faculty_member_semester or [],
                'faculty_member_subject': user.faculty_member_subject or [],
                'faculty_member_timing': user.faculty_member_timing or []
            }

            return Response({'faculty_data': faculty_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteFacultyMemberView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribed]

    def delete(self, request, email):
        try:
            if not email:
                return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the subscription field in the users table
            users_collection = settings.MONGO_DB['users']

            user = users_collection.find_one({'email': email, 'faculty_member_boss': request.user._id})

            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            name = user.get('name', 'User')
            users_collection.delete_one({'email': email})
            user = request.user
            users_collection.update_one({'_id': user._id}, {'$inc': {'subscribed_user_seats_left': 1}})

            # Compose email
            subject = 'Subscription Status Updated'
            message = f"Hello {name},\n\nYour account has been deleted. Kindly reply to this email for reasons.\n\nThank you!"
           
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            return Response({'message': 'User Deleted Successfully.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Failed to remove user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateFacultyMemberView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribed]
    def post(self, request):
        try:
            user = request.user
            user_id = user._id
            institution = user.institution
            data = request.data
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            phone_number = data.get('phoneNo')

            if user.subscribed_user_seats_left <= 0:
                return Response({'error': 'You have reached the maximum number of faculty members.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not name or not email or not password or not phone_number:
                return Response({'error': 'Name, email, password, phone number are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password strength
            password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$'
            if not match(password_regex, password):
                return Response({
                    'error': 'Password must be 8-20 characters long and contain at least one uppercase letter, one lowercase letter, and one number.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Optional confirm password match if provided
            if confirm_password and password != confirm_password:
                return Response({'error': 'Password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate Pakistan phone number format
            phone_regex = r'^(\+92|0092|0)?(3\d{2})(\d{7})$'
            if not match(phone_regex, phone_number):
                return Response({'error': 'Invalid Pakistan phone number format.'}, status=status.HTTP_400_BAD_REQUEST)

            collection = settings.MONGO_DB['users']
            existing_user = collection.find_one({'email': email})
            existing_user_with_phone = collection.find_one({'phone_number': phone_number})

            if existing_user_with_phone:
                # check if user is blocked
                if not existing_user_with_phone.get('blocked'):
                    return Response({'error': 'A user with this phone number already exists.'}, status=status.HTTP_409_CONFLICT)
        
            # check if user exists
            if existing_user:
                # check if user is blocked
                if not existing_user.get('blocked'):
                    return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_409_CONFLICT)
                
            hashed_password = password
            otp = random.randint(100000, 999999)  # 6-digit OTP
            otp_expires_at = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            if existing_user:
                if existing_user.get('name') == name and existing_user.get('email') == email and existing_user.get('phone_number') == phone_number and existing_user.get('password') == hashed_password:
                    collection.update_one(
                        {'email': email},
                        {
                            '$set': {
                                'otp': otp, 
                                'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                                'otp_attempts': 0  # Track failed attempts
                            }
                        }
                    )
                else:
                    return Response({'error': 'A user with this email already exists.\
                    Kindly enter correct details for email verification'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_document = {
                    'name': name,
                    'email': email,
                    'password': hashed_password,
                    'phone_number': phone_number,
                    'faculty_member': True,
                    'faculty_member_boss': ObjectId(user_id),
                    'otp': otp,
                    'blocked': True,
                    'otp_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'otp_expires_at': otp_expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'otp_attempts': 0  # Track failed attempts
                }
                
                collection.insert_one(user_document)
            
            # Send OTP via email
            try:
                subject = 'Your account verification email'
                message = f'Your account has been created for a faculty member role \
                for {institution} institution. Please verify your account by entering your otp. \
                Your OTP is: {otp}. It will expire in 5 minutes. Your password is {password}. \
                Use it after otp verification.'

                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            users_collection = settings.MONGO_DB['users']
            users_collection.update_one({'_id': user_id}, {'$inc': {'subscribed_user_seats_left': -1}})

            return Response({
                'message': 'OTP sent to email.',
                'otp_expires_in': 300  # 5 minutes in seconds
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )


class AddSubjectToFacultyMemberView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribed]

    def post(self, request):
        try:
            subject = request.data.get('subject')
            timing = request.data.get('timing')
            semester = request.data.get('semester')
            program = request.data.get('program')
            email = request.data.get('email')

            if not subject or not timing or not email or not semester or not program:
                return Response({'error': 'subject, timing, semester, program and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

            users_collection = settings.MONGO_DB['users']
            user = users_collection.find_one({'email': email, 'faculty_member_boss': request.user._id})

            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            name = user.get('name', 'User')

            current_subjects = user.get('faculty_member_subject', [])
            current_timings = user.get('faculty_member_timing', [])
            current_programs = user.get('faculty_member_program', [])
            current_semesters = user.get('faculty_member_semester', [])

            # Check for overlapping timings (each class is 1 hour)
            try:
                new_time = datetime.strptime(timing, '%H:%M')
                for t in current_timings:
                    existing_time = datetime.strptime(t, '%H:%M')
                    if abs((new_time - existing_time).total_seconds()) < 3600:
                        return Response({'error': f"New timing {timing} overlaps with existing timing {t}."},
                                        status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': 'Invalid time format. Use HH:MM (24-hour format).'},
                                status=status.HTTP_400_BAD_REQUEST)

            users_collection.update_one(
                {'email': email},
                {'$set': {
                    'faculty_member_subject': current_subjects + [subject],
                    'faculty_member_timing': current_timings + [timing],
                    'faculty_member_program': current_programs + [program],
                    'faculty_member_semester': current_semesters + [semester]
                }}
            )

            # Compose and send email
            email_subject = 'New subject added'
            message = f"Hello {name},\n\nNew subject {subject} has been added to your timetable with timing {timing}.\n\nThank you!"
            try:
                send_mail(email_subject, message, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            return Response({'message': 'Subject added successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({'error': 'Failed to process subject addition request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteSubjectOfFacultyMemberView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsSubscribed]

    def delete(self, request):
        try:
            subject = request.data.get('subject')
            timing = request.data.get('timing')
            semester = request.data.get('semester')
            program = request.data.get('program')
            email = request.data.get('email')
            name = request.user.name

            if not subject or not timing or not email:
                return Response({'error': 'Subject, timing, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

            users_collection = settings.MONGO_DB['users']
            user = users_collection.find_one({'email': email, 'faculty_member_boss': request.user._id})

            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            current_subjects = user.get('faculty_member_subject', [])
            current_timings = user.get('faculty_member_timing', [])
            current_programs = user.get('faculty_member_program', [])
            current_semesters = user.get('faculty_member_semester', [])

            if subject in current_subjects and timing in current_timings and program in current_programs and semester in current_semesters:
                subject_index = current_subjects.index(subject)
                timing_index = current_timings.index(timing)
                program_index = current_programs.index(program)
                semester_index = current_semesters.index(semester)
                # Ensure both indices match
                if subject_index == timing_index and timing_index == program_index and program_index == semester_index:
                    current_subjects.pop(subject_index)
                    current_timings.pop(timing_index)
                    current_programs.pop(program_index)
                    current_semesters.pop(semester_index)

                    users_collection.update_one(
                        {'email': email},
                        {'$set': {'faculty_member_subject': current_subjects, 'faculty_member_timing': current_timings, 'faculty_member_program': current_programs, 'faculty_member_semester': current_semesters}}
                    )
                                # Compose and send email
                    email_subject = 'subject removed'
                    message = f"Hello {name},\n\nYour subject {subject} has been removed from your timetable with timing {timing}.\n\n Reply to this email for reasons.\n\nThank you!"
                    try:
                        send_mail(email_subject, message, settings.EMAIL_HOST_USER, [email])
                    except Exception as e:
                        print(f"Email sending failed: {str(e)}")
                    
                    return Response({'message': 'Subject removed successfully.'}, status=status.HTTP_200_OK)

            return Response({'error': 'Subject not found'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({'error': 'Failed to delete subject'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
