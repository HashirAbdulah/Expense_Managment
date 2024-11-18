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
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
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

                # Create a new inactive user
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # Generate activation URL
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_genrator.make_token(user)})
                protocol = 'https' if not settings.DEBUG else 'http'
                activation_url = f'{protocol}://{domain}{link}'

                # Compose email
                email_subject = "Activate Your Account"
                email_body = (
                    f"Hi {username},\n\n"
                    f"To activate your account, click on the following link:\n{activation_url}\n\n"
                    "If you did not register for this account, please ignore this email."
                )

                # Send email
                send_mail(
                    email_subject,
                    email_body,
                    "xameni8509@kazvi.com",#email that will be use for the reciever
                    [email],
                    fail_silently=False,
                )
                # Success message
                messages.success(request, 'Successfully registered. Check your email to activate your account.')
                return redirect('register')

        messages.error(request, 'Username or email already exists.')
        return render(request, 'authentication/register.html')

class LoginView(View):
    # Implement login functionality here
    def get(self, request):
        return render(request, 'authentication/login.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from the URL
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # Validate the token
            if not token_genrator.check_token(user, token):
                messages.error(request, 'Activation link is invalid or has expired.')
                return redirect('register')

            # Check if the user is already active
            if user.is_active:
                messages.info(request, 'Account is already activated. Please log in.')
                return redirect('login')

            # Activate the user
            user.is_active = True
            user.save()

            # Pass the activation_success flag to the template
            return render(request, 'authentication/register.html', {'activation_success': True})

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as ex:
            print(f"Error during account activation: {ex}")
            messages.error(request, 'Invalid activation link.')
            return redirect('register')

        except Exception as ex:
            print(f"Unexpected error during account activation: {ex}")
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect('register')
   
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

