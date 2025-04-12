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
                    {'error': 'You need to verify your email first'},
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
            # print("data", data)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phoneNo')

            if not name or not email or not password:
                return Response({'error': 'Name, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            collection = settings.MONGO_DB['users']
            existing_user = collection.find_one({'email': email})

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
                user_document = {
                    'name': name,
                    'email': email,
                    'password': hashed_password,
                    'phone_number': phone_number,
                    'subscription': False,
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
                # Continue even if email fails - you might want to handle this differently

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
            print("now deleting user")
            # email = request.query_params.get('email')
            print("user id", email)
            if not email:
                return Response({'error': 'Video ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the subscription field in the users table
            users_collection = settings.MONGO_DB['users']
            users_collection.delete_one({'email': email})

            return Response({'message': 'User Deleted Successfully.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Failed to remove user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOtpView(APIView):
    def post(self, request):
        try:
            data = request.data
            print("data", data)
            otp = data.get('otp')
            email = data.get('email')  # Email should be passed from frontend
            
            if not otp or not email:
                return Response(
                    {'error': 'OTP and email are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            collection = settings.MONGO_DB['users']
            user = collection.find_one({'email': email})
            # print("1")
            if not user:
                return Response(
                    {'error': 'No OTP session found. Please sign up again.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            # print("user data", user)
            # Check if OTP is expired
            otp_expires_at = datetime.strptime(
                user['otp_expires_at'], 
                '%Y-%m-%d %H:%M:%S'
            )
            current_time = datetime.now()
            # print("time zone", current_time, "otp expires at", otp_expires_at)
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
            # print("data", data)
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
                # Continue even if email fails - you might want to handle this differently

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
    permission_classes = [IsSubscribedOrUnsubscribed]
    
    def post(self, request):
        # print("-----start video uploading----")
        try:
            # Check if a video file is included in the request
            model_type = request.data.get('model_type', None)

            # print("model type", model_type)
            # print("model type", model_type)
            if 'video_file' not in request.FILES:
                # print("---video_file----")
                return Response({'error': 'No video file provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # current authenticated user
            user = request.user
            user_id = user._id
            # user_id = "bro"
            video_file = request.FILES['video_file']

            # Initialize GCS client
            # print("default google credentials", settings.GOOGLE_APPLICATION_CREDENTIALS)

            credentials = service_account.Credentials.from_service_account_info(settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = storage.Client(credentials=credentials)
            # client = storage.Client.from_service_account_json(settings.GCS_CREDENTIALS_PATH)
            bucket = client.bucket(settings.GCS_BUCKET_NAME)

            # Generate a unique filename for the video
            video_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.name}"

            # Upload the video to GCS
            blob = bucket.blob(video_filename)
            blob.upload_from_file(video_file, rewind=True)

            # Get the public URL of the uploaded video
            video_url = blob.public_url

            # video_url =  "https://storage.googleapis.com/fyp-data-bucket/20250314205040_23_1.mp4"

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
            
            # nigga = True
            # classification_result = None

            if user.subscription == False:
            # if nigga == True:
                blob.delete()
                # Return a success response
                return Response({
                    'message': 'Video classified successfully.',
                    'classification': classification_result if classification_result else "no cheating",
                    'video_name': video_filename,
                    'url': video_url,
                }, status=status.HTTP_200_OK)
            else:
                # Store the video document in MongoDB
                video_document = {
                    # 'user_id': ObjectId("6762ce83bc0c6756461cba41"),  # Store the user ID as an ObjectId
                    'user_id': user_id,
                    'video_name': video_filename,
                    'size': round(video_file.size / 1048576, 2),
                    'url': video_url,
                    'classification': classification_result if classification_result else "no cheating",
                    'model_type': model_type,
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
    permission_classes = [IsSubscribed]

    def get(self, request, video_id):    
        try:
            print("video id", video_id)
            if not video_id:
                return Response({'error': 'Video ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Access the MongoDB collection
            collection = settings.MONGO_DB['videos']

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
    permission_classes = [IsSubscribed]

    def get(self, request):
        user = request.user  # Assuming user authentication is done
        user_id = user._id
        # print("---user---------------",user)
        
        # user_id=ObjectId(user._id)
        # user_id = ObjectId('6762ce83bc0c6756461cba41')

        # print(ObjectId(user._id),"---model_names----",model_names)

        # Fetch all videos for the user
        video_collection = settings.MONGO_DB['videos']

        videos = video_collection.find({'user_id': user_id})
        # print("videos found",videos)
        total_size_mb = 0.0
        video_data = []

        for video in videos:
            url = video.get('url')
            video_name = video.get('video_name', 'Unknown')

            total_size_mb += video.get('size', 0)

            # print("user id", video.get('user_id'))

            video_data.append({
                'name': video_name,
                # 'size': f'{video.get('size', 0):.2f} MB',
                'size': f"{video.get('size', 0):.2f} MB",
                # 'size': f"{video.get("size", 0):.2f} MB",
                'url': url,
                # 'asset_id': video.get('asset_id', None)
            })
            # s += video['size']
            # print("----s-----",s)
        # print("video data", video_data)
        total_storage_gb = 10  # 50 GB
        total_storage_mb = total_storage_gb * 1024  # Convert GB to MB
        used_storage_mb = total_size_mb  # Sum all video sizes
        # print("used storage mb", used_storage_mb)
        remaining_storage_gb = (total_storage_mb - used_storage_mb) / 1024
        # print("remaning storage gb without", remaining_storage_gb)
        # print("remaining storage mb",  f'{remaining_storage_gb:.2f} GB')
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
    
            
class GetUsersView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        user_collection = settings.MONGO_DB['users']
        # Fetch only users where the 'admin' key does not exist
        users = user_collection.find({'admin': {'$exists': False}})

        user_data = []
        for user in users:
            user_data.append({
                'name': user.get('name', None),
                'email': user.get('email', None),
                'joined': user.get('joined', None),
                'phone_number': user.get('phone_number', None),
                'subscription': user.get('subscription', 'Inactive')
            })
        
        return Response({'users': user_data}, status=status.HTTP_200_OK)
    

class UserView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user 
            print("users", user)
            return Response({'name': user.name,'password': user.password}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
    def put(self, request):
        try:
            data = request.data
            print("data", data)
            user = request.user 
            user_id = user._id
            name = data.get('name')
            password = data.get('password')  # Email should be passed from frontend
            
            if not name and not password:
                return Response(
                    {'error': 'At least name or password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            collection = settings.MONGO_DB['users']
            updated_result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'name': name, 'password': password}})

            if updated_result.modified_count == 0:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
            # print("users", user_data)
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Unexpected error - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UpdateSubscriptionView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            # print("--------user----------",user)

            subscription_status = request.data.get('subscription')
            email = request.data.get('email')

            if subscription_status is None:
                return Response({'error': 'Subscription status is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the subscription field in the users table
            users_collection = settings.MONGO_DB['users']
            users_collection.update_one(
                {'email': email},
                {'$set': {'subscription': subscription_status}}
            )
            res = users_collection.find_one({'email': email},)
            print("----res-----------------",res)
            return Response({'message': 'Subscription status updated successfully.', 'subscription':res.get('subscription', None)}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Failed to update subscription status.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
