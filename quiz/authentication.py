from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class DjangoUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the user credentials from the request data
        form = AuthenticationForm(request, data=request.data)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Log in the user
                login(request, user)
                return (user, None)
            else:
                raise AuthenticationFailed('Invalid username or password')
        else:
            raise AuthenticationFailed('Invalid username or password')