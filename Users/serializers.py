from phonenumber_field.serializerfields import PhoneNumberField
from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate, login


class UserSerializers(serializers.Serializer):
    tokens=serializers.SerializerMethodField()
    phonenumber_verified=serializers.BooleanField(read_only=True)
    phonenumber=serializers.CharField(read_only=True)
    id=serializers.UUIDField(read_only=True)

    def get_tokens(self, obj):
        return obj.get_tokens()


class LoginSerializer(serializers.Serializer):
    phonenumber= PhoneNumberField()
    password=serializers.CharField(write_only=True)

    def validate(self, attrs):
        phonenumber=attrs['phonenumber']
        password=attrs['password']
        p=authenticate(phonenumber=phonenumber, password=password)
        if not p:
            raise serializers.ValidationError({'error':'phonenumber or password is incorrect'})
        else:
            return {'resp':UserSerializers(p).data, 'user':p}  
        
class SignupSerializer(serializers.ModelSerializer):
    phonenumber=PhoneNumberField()
    confirm_password=serializers.CharField(write_only=True, min_length=8)
    password=serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model=User
        fields=['phonenumber', 'password','confirm_password']
    
    def validate(self, attrs):
        u=User.objects.filter(phonenumber=attrs['phonenumber'])
        if u.exists():
            raise serializers.ValidationError({'phonenumber':'User with this phonenumber already exists'})
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password':'passwords dont match'})
        
        else:
            return attrs

    def create(self, validated_data):
        phonenumber=validated_data['phonenumber']
        password=validated_data['password']
        u=User.objects.create(phonenumber=phonenumber)
        u.set_password(password)
        u.save()
        return u

class OtpSerializer(serializers.Serializer):
    code=serializers.CharField()

class ChangePasswordserializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True)
    new_password=serializers.CharField(write_only=True, min_length=8)
    confirm_password=serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        request=self.context.get('request')
        user=request.user
        old=data['old_password']
        new=data['new_password']
        confirm=data['confirm_password']
        if new != confirm :
            raise serializers.ValidationError({'new_password':'passwords dont match'})
        if not request.user.check_password(old):
            raise serializers.ValidationError({'old_password':'incorrect password'})
        return data
        
class PhonenumberSerializer(serializers.Serializer):
    phonenumber=PhoneNumberField()

    def validate(self, data):
        phonenumber=data['phonenumber']
        u=User.objects.filter(phonenumber=phonenumber)
        if not u.exists():
            raise serializers.ValidationError({'phonenumber':'user with this phonenumber does not exists'})
        return data 

class PasswordSetSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True, min_length=8)
    confirm_password=serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        new=data['password']
        confirm=data['confirm_password']
        if new != confirm :
            raise serializers.ValidationError({'password':'passwords dont match'})
        return data

class Update_PhonenumberSerializer(serializers.Serializer):
    phonenumber=PhoneNumberField