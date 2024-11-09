from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
import json
from django.contrib.auth.models import User
import re
# Create your views here.

class RegisterationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        # Implement logic to check if username is unique
        
        if not username:
            return JsonResponse({'error': 'Username cannot be empty'}, status=400)
    
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=409)
    
        if not username.isalnum():
            return JsonResponse({'error': 'Username should be alphanumeric'}, status=400)
    
        if len(username) < 3 or len(username) > 30:
            return JsonResponse({'error': 'Username must be between 3 and 30 characters'}, status=400)
    
        if re.search(r'[^a-zA-Z0-9]', username):
            return JsonResponse({'error': 'Username should only contain letters and numbers'}, status=400)

    # All checks passed, username is valid
        return JsonResponse({'valid': True}, status=200)

