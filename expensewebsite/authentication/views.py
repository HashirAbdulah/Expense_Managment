from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json
from django.contrib import messages, auth
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_genrator
from django.conf import settings
from django.contrib.auth import logout,get_user_model
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now
from django.core.cache import cache


# RegisterationView remains unchanged, as registration should not be login-protected
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
                    "filelip663@kindomd.com",  # Email used as sender
                    [email],
                    fail_silently=False,
                )
                # Success message
                messages.success(request, 'Successfully registered. Check your email to activate your account.')
                return redirect('register')

        messages.error(request, 'Username or email already exists.')
        return render(request, 'authentication/register.html')

class LoginView(View):
    def get(self, request):
        # Display the login page
        return render(request, 'authentication/login.html')

    def post(self, request):
        # Process login form submission
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate input
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'authentication/login.html')

        # Authenticate user
        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('expenses:expenses')
            else:
                messages.error(request, "Your account is not active. Please check your email.")
        else:
            messages.error(request, "Invalid username or password.")

        # If authentication fails, reload login page
        return render(request, 'authentication/login.html')

# VerificationView remains unchanged, as it's accessed via activation link
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from the URL
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # Validate the token
            if not token_genrator.check_token(user, token):
                messages.error(request, 'Activation link is invalid or has expired.')
                return redirect('expenses:expenses')

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

# Making UsernameValidationView and EmailValidationView accessible without login
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

# LogoutView does not require login protection
class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'Successfully logged out.')
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):
        email = request.POST.get('email')
        context = {
            "values": request.POST
        }

        # Validate the email format using Django's built-in EmailValidator
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email or email format.')
            return render(request, 'authentication/reset_password.html', context)

        # Check if the email has made a recent request (rate-limiting)
        last_request_time = cache.get(f'password_reset_{email}')
        if last_request_time and (now() - last_request_time).seconds < 60:  # 1 minute throttle
            messages.error(request, 'Too many requests. Please try again later.')
            return render(request, 'authentication/reset_password.html', context)

        # Check if the user exists silently (don't give away whether the email exists or not)
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal whether email exists or not
            pass

        # Generate reset token
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_genrator.make_token(user)

            # Generate password reset URL
            domain = get_current_site(request).domain
            link = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
            protocol = 'https' if not settings.DEBUG else 'http'
            reset_url = f'{protocol}://{domain}{link}'

            # Compose email
            email_subject = "Password Reset Request"
            email_body = f"""
            Hi {user.username},

            To reset your password, click on the following link:
            {reset_url}

            If you did not request a password reset, please ignore this email.
            """

            # Send the email
            send_mail(
                email_subject,
                email_body,  # Directly passing the string body
                settings.DEFAULT_FROM_EMAIL,  # From email
                [email],  # To email
                fail_silently=False,
            )

            # Store timestamp for rate-limiting
            cache.set(f'password_reset_{email}', now(), timeout=3600)  # 1 hour timeout

        # Success message (even if the email doesn't exist, we prevent account enumeration)
        messages.success(request, 'Password reset link sent! Check your email.')
        return redirect('reset-password')

class PasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the UID from the URL
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (ValueError, TypeError, User.DoesNotExist):
            raise Http404("Invalid link")

        # Check if the token is valid
        if not token_genrator.check_token(user, token):
            messages.error(request, 'Invalid or expired token.')
            return redirect('reset-password')

        # Render the password reset form
        return render(request, 'authentication/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        try:
            # Decode the UID from the URL
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (ValueError, TypeError, User.DoesNotExist):
            raise Http404("Invalid link")

        # Check if the token is valid
        if not token_genrator.check_token(user, token):
            messages.error(request, 'Invalid or expired token.')
            return redirect('reset-password')

        # Get the new password from the form
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')

        # Ensure passwords match
        if password != password_confirmation:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})

        # Enforce strong password rules (e.g., minimum length, complexity)
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'authentication/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})
        
        # Set the new password and save the user
        user.set_password(password)
        user.save()

        # Invalidate the reset token after it is used (for security)
        cache.delete(f'password_reset_{user.email}')

        # Send success message and redirect to login page
        messages.success(request, 'Your password has been reset successfully. You can now log in.')
        return redirect('login')
    
# Ensure cache is cleared after logout
def clear_cache_after_logout(response):
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response['Pragma'] = 'no-cache'
    return response