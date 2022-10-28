from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient, APIClient
from .models import User
from django.urls import reverse

class Testotp(APITestCase):
    
    def  setUp(self):
        self.client=APIClient()
        self.endpoint='http://127.0.0.1:8000'
        self.user=User.objects.create_user(phonenumber='08111909767', password='qwe123454', fullname='lo')

    def test_login(self):
        url='/login/'
        resp=self.client.post(url, {'phonenumber':'08111909767', 'password':'qwe123454'})
        self.assertEqual(resp.status_code, 200)
        self.maxDiff= None
        self.assertEqual(resp.data, {'user':{'tokens':self.user.get_tokens(), 'phonenumber_verified':False, 'phonenumber':'08111909767', 'id':self.user.id}})

    def test_signup(self):
        url='/signup/'
        resp=self.client.post(url, {'phonenumber':'08111087655', 'password':'000000000', 'confirm_password':'000000000'})
        self.assertEqual(resp.status_code, 200)

