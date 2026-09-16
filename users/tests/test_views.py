from django.test import TestCase
from users.models import User
from django.contrib.auth.models import Group
from django.urls import reverse

class UserViewTests(TestCase):
    def setUp(self):
        self.register_valid_data = {
            'email':'user1@test.com',
            'first_name':'User1',
            'last_name':'Test',
            'phone_number':'+79009009090',
            'password1':'SupportFlow_Test_8472',
            'password2': 'SupportFlow_Test_8472'
        }

        self.login_valid_data = {
            'email':'user1@example.com',
            'password':'SupportFlow_Test_8472',
        }

        group_user = Group.objects.get(name='User')
        self.user = User.objects.create_user(
            email='user1@example.com',
            password='SupportFlow_Test_8472',
            phone_number='+79990000001'
        )
        self.user.groups.add(group_user)

    def test_login_success(self):
        response = self.client.post(reverse('login'), data=self.login_valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ticket-list'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_invalid_credentials(self):
        data = self.login_valid_data.copy()
        data['password']='sdadsa'
        response = self.client.post(reverse('login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['__all__'][0].code, 'invalid_login')

    def test_register_success(self):
        response = self.client.post(reverse('register'), data=self.register_valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(email=self.register_valid_data['email'])
        self.assertEqual(user.email, 'user1@test.com')
        self.assertTrue(user.groups.filter(name='User').exists())

    def test_register_invalid(self):
        data = self.register_valid_data.copy()
        data['password1']='12345678'
        data['password2']='123456789'
        response = self.client.post(reverse('register'), data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['password2'][0].code, 'password_mismatch')
        user_exists = User.objects.filter(email=self.register_valid_data['email']).exists()
        self.assertFalse(user_exists)

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('login'))





