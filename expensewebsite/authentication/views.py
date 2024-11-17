from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_genrator
from django.conf import settings


class RegisterationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                uidb64 = urlsafe_base64_encode(force_bytes((user.pk)))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_genrator.make_token(user)})
                protocol = 'https' if not settings.DEBUG else 'http'
                active_url = f'{protocol}://{domain}{link}'
                email_subject = "Activate Your Account"
                email_body = (
                f"Hi {username}, To activate your account, click on the following link: "
                f"{active_url}{user.pk}"
                )
                send_mail(
                email_subject,
                email_body,
                "cimiko6016@opposir.com",#email that will be use for the reciever
                [email],
                fail_silently=False,
                )
        # Success message
        messages.success(request, 'Successfully registered')
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        return redirect('login')
    
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

