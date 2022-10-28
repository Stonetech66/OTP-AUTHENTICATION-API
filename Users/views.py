from datetime import timedelta
from Users.cookies import delete_cookies, set_refresh_cookie, set_access_cookie
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response
from .serializers import ChangePasswordserializer, LoginSerializer, OtpSerializer, PasswordSetSerializer, PhonenumberSerializer, SignupSerializer, Update_PhonenumberSerializer, UserSerializers
from .models import VerificationCode
from django.contrib.auth import login
from .  import throttle
from .models import User
from django.utils import timezone
from Users import tasks
from django.urls import reverse
from django.conf import settings

code_expiry=settings.CODE_EXPIRY_TIME






# Create your views here.


class LoginView(APIView):
    '''
    Login (endpoint for a user to Login)

    Requires a valid phonenumber and also a Password
    '''
    serializer_class=LoginSerializer
    def get_serializer(self):
        return LoginSerializer()
    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user= serializer.validated_data['user']
            if user.is_active ==False:
                return Response({'error':'Your account has been suspended'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                response= Response({'user':serializer.validated_data['resp']})
                set_access_cookie(response, user)
                set_refresh_cookie(response, user)
                try:
                    login(request, user)
                except:
                    pass
                return response

                


class SignupView(APIView):
    '''
    Signup (endpoint for a user to signup)
    
    Requires a valid phonenumber, password and confirm_password
    A link to verify the Phonenumber is giving in the response
    '''
    serializer_class=SignupSerializer
    throttle_classes=[throttle.StrictAnonThrottle]

    def get_serializer(self):
        return SignupSerializer()
    def post(self, request,*args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            u=serializer.save()
            code=tasks.create_code()
            x=u.id
            tasks.create_VerificationCode.delay(x, code)
            p=serializer.validated_data.get('phonenumber')
            tasks.send_verification_code.delay(x, code)
            response=Response({'user':UserSerializers(u).data,'message':f'verification code sent to {p}', 'verification-link':reverse('verify-phonenumber')})
            set_access_cookie(response, u)
            set_refresh_cookie(response, u)
            return response

class VerifyPhonenumber(APIView):
    '''
    Verify-Phonenumber (endpoint to verify a user's phonunumber)
    
    Requires a code sent to the user during Signup or Resend of Verification code
    '''
    serializer_class=OtpSerializer
    permission_classes=[permissions.IsAuthenticated]
    throttle_classes=[throttle.StrictUSerThrottle]

    def get_serializer(self):
        return OtpSerializer()
    def post(self, request, *args, **kwargs):
        u=request.user
        serializer=self.serializer_class(data=request.data)
        if u.is_active ==False:
                return Response({'error':'Your account has been suspended'}, status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid(raise_exception=True):
            code=str(serializer.validated_data.get('code'))
            p=VerificationCode.objects.filter(user=u, code=code, active=True)
            v=p.last()
            if p.exists() and  v.date + timedelta(minutes=code_expiry) > timezone.now():
                tasks.verify_phonenumber.delay(u.id)
                v.active=False
                v.save()
                return Response({'success':'your phonenumber has been verified'}, status=status.HTTP_200_OK)
            return Response({'error':'invalid code or code has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetView(APIView):
    '''
    Password Reset (endpoint to reset a user's password)

    Requires the user's phonenumber
    A link to verify the code sent to the user is giving in the response if the phonenumber is valid.
    '''
    serializer_class=PhonenumberSerializer
    throttle_classes=[throttle.StrictUSerThrottle, throttle.StrictAnonThrottle]
    def get_serializer(self):
        return PhonenumberSerializer()

    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            p=serializer.validated_data.get('phonenumber')
            u=User.objects.filter(phonenumber=p)
            user=u.last()
            x=user.id
            code=tasks.create_code()
            print(code)
            tasks.create_VerificationCode.delay(x, code)
            tasks.send_verification_code.delay(x, code)
            # s=TimestampSigner(salt='passcode')
            # v=s.sign_object(str(x))
            return Response({'message':f'verification code sent to {p}', 'verification-link':reverse('password-reset-verify', kwargs={'uuid':x})}, status=status.HTTP_200_OK)


class PasswordResetVerify(APIView):
    ''' 
    Password Reset Verify (endpoint to verify code sent to a user for password-reset)

    Requires the code sent to the user
    A link to set a new password for the user is giving in the response if the code is valid
    '''
    serializer_class=OtpSerializer
    throttle_classes=[throttle.StrictAnonThrottle, throttle.StrictUSerThrottle]

    def get_serializer(self):
        return OtpSerializer()
    def post(self, request, *args, **kwargs):
        uid=self.kwargs['uuid']
        # s=TimestampSigner(salt='passcode')
        # try:
        #     v=s.unsign_object(uid, max_age=timedelta(minutes=7))
        # except:
        #     return Response({'error':'code has expired'}, status=status.HTTP_400_BAD_REQUEST)
        u=User.objects.filter(id=uid)
        if u.exists():
            u=u.last()
            serializer=self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                code=str(serializer.validated_data.get('code'))
                p=VerificationCode.objects.filter(user=u, code=code, active=True)
                if p.exists() and  p.last().date + timedelta(minutes=code_expiry) > timezone.now():
                    return Response({'success':'code is valid', 'link':reverse('password-reset-confirm', kwargs={'uuid':uid, 'code':code})}, status=status.HTTP_200_OK)
                return Response({'error':'invalid code or code has expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':'user with this id does not exists so cant verify a phonenumber'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    ''' 
    Password Reset Confirm (endpoint to set a new password for the user)

    Requires a password and confim_password    
    '''
    serializer_class=PasswordSetSerializer
    throttle_classes=[throttle.StrictUSerThrottle, throttle.StrictAnonThrottle]

    def get_serializer(self):
        return PasswordSetSerializer()

    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        uid=self.kwargs['uuid']
        # s=TimestampSigner(salt='passcode')
        # try:
        #     v=s.unsign_object(uid, max_age=timedelta(minutes=15))
        # except:
        #     return Response({'error':'code has expired'}, status=status.HTTP_400_BAD_REQUEST)
        u=User.objects.filter(id=uid)
        if u.exists():
            u=u.last()
            if serializer.is_valid(raise_exception=True):
                    code=self.kwargs['code']
                    p=VerificationCode.objects.filter(user=u, code=code, active=True)
                    password=serializer.validated_data.get('password')
                    v=p.last()
                    if p.exists() and  v.date + timedelta(minutes=code_expiry+7) > timezone.now():
                        u.set_password(password)
                        u.save()
                        v.active=False
                        v.save()
                        return Response({'success':'Your password has been reset '}, status=status.HTTP_200_OK)
                    return Response({'error':'invalid code or code has expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':'user with this id does not exists so cant verify a phonenumber'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    ''' 
    Password Change (endpoint to change a user password)
    
    Requires a old_password, new_password, confirm_password
    '''
    serializer_class=ChangePasswordserializer
    permission_classes=[permissions.IsAuthenticated]
  
    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        user=request.user
        if user.is_active ==False:
                return Response({'error':'Your account has been suspended'}, status=status.HTTP_401_UNAUTHORIZED)
        if user.phonenumber_verified !=True: 
            return  Response({'error':'Your phonenumber has not been verified'}, status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid(raise_exception=True):
            password=serializer.validated_data.get('new_password')
            user.set_password(password)
            user.save()
            return Response({'message':'password sucessfuly changed'}, status=status.HTTP_200_OK)

class ResendPhoneVerficationCodeView(APIView):
    '''
    Resend Phonenumber Verification Code (endpoint to resend Phonenumber verification code for a user)

    A link to verify the Phonenumber is giving in the response
    '''
    permission_classes=[permissions.IsAuthenticated]
    throttle_classes=[throttle.StrictUSerThrottle]
    def post(self, request, *args, **kwargs):
            u=request.user
            user=u
            code=tasks.create_code()
            p=user.phonenumber
            x=user.id
            tasks.create_VerificationCode.delay(x, code)
            tasks.send_verification_code.delay(x, code)
            return Response({'message':f'verification code sent to {p}', 'verification-link':reverse('verify-phonenumber'), 'update-phonenumber':reverse('update-phonenumber')}, status=status.HTTP_200_OK)

class Update_phonenumber(UpdateAPIView):
    ''' 
    Update Phonenumber (endpoint to update a user phonenumber)

    '''
    serializer_class=Update_PhonenumberSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetails(RetrieveAPIView):
    '''
    User Details (endpoint to get the details of a user)
    '''
    serializer_class=UserSerializers
    permission_classes=[permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class LogoutView(APIView):

    def post(self, request):
        user=request.user
        if user == None:
            return  Response({'message':'suceessfuly logged out'}, status=status.HTTP_204_NO_CONTENT)
        user.get_tokens().clear()
        response=Response({'message':'suceessfuly logged out'}, status=status.HTTP_204_NO_CONTENT)
        delete_cookies(response)
        return response

