import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests

logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()

# Replace this with your actual Google Client ID from Google Cloud Console
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '885449350134-p7nineermvf3f8c337psqurcnc61l4e3.apps.googleusercontent.com')

class GoogleLoginAPIView(APIView):
    """
    Verifies a Google Identity Services token, creates/fetches the Django User,
    logs them into the standard Django session, and returns JWT tokens.
    """
    permission_classes = () # Allow any

    def post(self, request):
        try:
            credential = request.data.get('credential')
            if not credential:
                return Response({'error': 'No credential provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Strictly verify the token signature and issuer using Google's official library
            try:
                idinfo = id_token.verify_oauth2_token(credential, requests.Request(), GOOGLE_CLIENT_ID)
                
                # Check issuer
                if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')
            except ValueError as ve:
                logger.error(f"Token verification failed: {str(ve)}")
                return Response({'error': 'Invalid Google token.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'No email found in token.'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract user info
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            
            # Get or create the user
            user, created = User.objects.get_or_create(username=email, defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })

            # Important: Log the user into the standard Django session so templates like home.html work!
            login(request, user)

            # Generate JWTs for API usage
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Logged in successfully',
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
            
        except Exception as e:
            logger.error(f"Google login failed: {str(e)}", exc_info=True)
            return Response({'error': 'Authentication failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
