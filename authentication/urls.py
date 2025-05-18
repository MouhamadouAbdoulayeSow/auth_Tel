from django.urls import path
from .views import RegistrationView, VerificationView, LoginView, PasswordResetRequestView, PasswordResetVerifyConfirmView, LogoutView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify/', VerificationView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetVerifyConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]