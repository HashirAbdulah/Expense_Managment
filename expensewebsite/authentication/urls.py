from .views import RegisterationView,UsernameValidationView,EmailValidationView,VerificationView,LoginView,LogoutView,RequestPasswordResetEmail,PasswordResetConfirmView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns =[
    path('register', RegisterationView.as_view(),name='register'),
    path('login', LoginView.as_view(),name='login'),
    path('logout', LogoutView.as_view(),name='logout'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email',csrf_exempt(EmailValidationView.as_view()),name='validate-email'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
    path('request-reset-link/', RequestPasswordResetEmail.as_view(), name='reset-password'),
    path('request-reset-link/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]
