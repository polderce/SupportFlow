from django.test import TestCase
from users.models import User
from django.contrib.auth.models import Group
from users.forms import RegisterForm, LoginForm

class UsersFormTests(TestCase):
    def setUp(self):
        self.register_valid_data = {
            'email':'user1@test.com',
            'first_name':'User1',
            'last_name':'Test',
            'phone_number':'89009009090',
            'password1':'SupportFlow_Test_8472',
            'password2': 'SupportFlow_Test_8472'
        }

        self.login_valid_data = {
            'email':'user1@test.com',
            'password':'SupportFlow_Test_8472',
        }

        group_user = Group.objects.get(name='User')
        self.user = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            phone_number='79990000001'
        )
        self.user.groups.add(group_user)

    def test_register_form_valid(self):
        form = RegisterForm(data=self.register_valid_data)
        self.assertTrue(form.is_valid())

    def test_register_form_password_mismatch(self):
        data = self.register_valid_data.copy()
        data['password2'] = 'password12'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['password2'][0].code, 'password_mismatch')

    def test_register_form_duplicate_email(self):
        data = self.register_valid_data.copy()
        data['email'] = 'user1@example.com'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['email'][0].code, 'unique')


    def test_register_form_duplicate_phone(self):
        data = self.register_valid_data.copy()
        data['phone_number'] = '79990000001'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['phone_number'][0].code, 'unique')

    def test_login_form_required_fields(self):
        data = self.login_valid_data.copy()
        data['email'] = ''
        data['password'] = ''
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['email'][0].code, 'required')
        self.assertEqual(form.errors.as_data()['password'][0].code, 'required')
