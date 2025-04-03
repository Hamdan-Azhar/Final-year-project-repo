from rest_framework_simplejwt.tokens import RefreshToken
# def generate_jwt_tokens(user_id):
#     refresh = RefreshToken()
#     refresh['user_id'] = user_id
#     access_token = refresh.access_token
#     access_token['user_id'] = user_id
#     return {
#         'refresh': str(refresh),
#         'access': str(access_token),
#     }


def generate_jwt_tokens(user):
    """
    Generates JWT tokens with user roles and metadata
    Args:
        user: MongoDB user document (dict) containing:
            - _id (ObjectId)
            - admin (bool, optional)
            - subscription (bool, optional)
            - other relevant fields
    Returns:
        {
            'refresh': str,
            'access': str,
            'user_id': str,
            'is_admin': bool,
            'is_subscribed': bool
        }
    """
    refresh = RefreshToken()
    
    # Add standard claims
    user_id = str(user['_id'])
    refresh['user_id'] = user_id
    refresh['is_admin'] = user.get('admin', False)
    refresh['is_subscribed'] = user.get('subscription', False)
    
    # Create access token from refresh token
    access_token = refresh.access_token
    access_token['user_id'] = user_id
    access_token['is_admin'] = user.get('admin', False)
    access_token['is_subscribed'] = user.get('subscription', False)

    return {
        'refresh': str(refresh),
        'access': str(access_token),
        'user_id': user_id,
        'is_admin': str(user.get('admin', False)),
        'is_subscribed': str(user.get('subscription', False))
    }