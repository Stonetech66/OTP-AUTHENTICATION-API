from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns= [ 
    path('login/', views.LoginView.as_view(), name='logout'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view()),
    path('refresh/token/', TokenRefreshView.as_view()),
    path('', include('rest_framework.urls')),
    path('verify-phonenumber/', views.VerifyPhonenumber.as_view(), name='verify-phonenumber'),
    path('password/reset-verify/<uuid>/', views.PasswordResetVerify.as_view(), name='password-reset-verify'),
    path('password/reset-confirm/<code>/<uuid>/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('resend-phone-verification-code/', views.ResendPhoneVerficationCodeView.as_view(), name='resend code verification code'),
    path('update-phonenumber/', views.Update_phonenumber.as_view(), name='update-phonenumber'),
    path('user-details/', views.UserDetails.as_view(), name='user-details')

]