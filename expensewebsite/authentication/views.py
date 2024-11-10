from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json

class RegisterationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')


class UsernameValidationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            if not username:
                return JsonResponse({'error': 'Username cannot be empty'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=409)

            if not username.isalnum() or len(username) < 3 or len(username) > 30:
                return JsonResponse({'error': 'Username should be alphanumeric and between 3 to 30 characters'}, status=400)

            return JsonResponse({'valid': True}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)


class EmailValidationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()

            if not email:
                return JsonResponse({'error': 'Email cannot be empty'}, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)

            return JsonResponse({'email_valid': True}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
