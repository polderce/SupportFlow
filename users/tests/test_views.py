from django.test import TestCase
from users.models import User
from users.permissions import can_access_profile
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

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

        self.change_valid_data = {
            'first_name':'Иван',
            'last_name':'Иванов',
            'phone_number':'89032321221'
        }

        group_user = Group.objects.get(name='User')
        self.user = User.objects.create_user(
            email='user1@example.com',
            password='SupportFlow_Test_8472',
            phone_number='+79990000001'
        )
        self.user.groups.add(group_user)

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            phone_number='+79990000002'
        )
        self.user2.groups.add(group_user)

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

    def test_can_access_own_profile(self):
        self.assertTrue(can_access_profile(self.user, target_user=self.user))

    def test_cannot_access_other_profile(self):
        self.assertFalse(can_access_profile(self.user, target_user=self.user2))

    def test_profile_view_authenticated_owner(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user, response.context['profile_user'])
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_authenticated_other_user_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile', kwargs={'pk':self.user2.pk}))
        self.assertEqual(response.status_code, 403)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('profile', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile', kwargs={'pk':self.user.pk})}")

    def test_profile_change_view_authenticated_owner(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile-change', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_change.html')
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertIsNotNone(response.context['form'])

    def test_profile_change_view_other_user_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile-change', kwargs={'pk':self.user2.pk}))
        self.assertEqual(response.status_code, 403)

    def test_profile_change_success(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile-change', kwargs={'pk':self.user.pk}), data=self.change_valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'pk':self.user.pk}))
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Иванов')
        self.assertEqual(user.phone_number, '+79032321221')

    def test_profile_change_invalid_phone(self):
        self.client.force_login(self.user)
        data = self.change_valid_data.copy()
        data['phone_number'] = '98123848884'
        response = self.client.post(reverse('profile-change', kwargs={'pk':self.user.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.phone_number, '+79990000001')

    def test_profile_change_unauthenticated(self):
        response = self.client.post(reverse('profile-change', kwargs={'pk':self.user.pk}), data=self.change_valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile-change', kwargs={'pk':self.user.pk})}")

    def test_profile_change_duplicate_phone(self):
        self.client.force_login(self.user)
        data = self.change_valid_data.copy()
        data['phone_number'] = '+79990000002'
        response = self.client.post(reverse('profile-change', kwargs={'pk':self.user.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.phone_number, '+79990000001')

    def test_profile_change_photo_upload(self):
        self.client.force_login(self.user)
        file_io = BytesIO()
        image = Image.new('RGB', (100, 100), 'white')
        image.save(file_io, 'JPEG')
        file_io.seek(0)

        avatar = SimpleUploadedFile(
            name='real_image.jpg',
            content=file_io.read(),
            content_type='image/jpeg'
        )
        data = self.change_valid_data.copy()
        data['photo']= avatar
        response = self.client.post(reverse('profile-change', kwargs={'pk':self.user.pk}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'pk':self.user.pk}))
        self.user.refresh_from_db()
        self.assertIn('real_image', self.user.photo.name)
        self.assertTrue(self.user.photo.storage.exists(self.user.photo.name))









