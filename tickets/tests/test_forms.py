from django.test import TestCase
from users.models import User
from django.contrib.auth.models import Group
from tickets.models import Ticket, Category, Priority, Status
from tickets.forms import TicketCreationForm, TicketChangeForm

class TicketCreationFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title='Операционная система',
            description='Бла Бла Бла'
            )

        self.create_valid_data = {
            'title':'Test title',
            'category':self.category.pk,
            'description':'Test description',
        }

    def test_create_form_is_valid(self):
        form = TicketCreationForm(data=self.create_valid_data)
        self.assertTrue(form.is_valid())

    def test_title_max_length(self):
        data = self.create_valid_data.copy()
        data['title'] = '1' * 51
        form = TicketCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors.as_data()['title'][0].code, 'max_length')

    def test_title_at_max_length(self):
        data = self.create_valid_data.copy()
        data['title'] = '1' * 50
        form = TicketCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_title_is_null(self):
        data = self.create_valid_data.copy()
        data['title'] = ''
        form = TicketCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors.as_data()['title'][0].code, 'required')

    def test_category_is_optional(self):
        data = self.create_valid_data.copy()
        data['category'] = ''
        form = TicketCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_specific_fields_exist(self):
        form = TicketCreationForm()
        expected_fields = ['title', 'category', 'description']
        self.assertSequenceEqual(list(form.fields.keys()), expected_fields)


class TicketChangeFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title='Операционная система',
            description='Бла Бла Бла'
            )

        self.priority = Priority.LOW

        self.status1 = Status.NEW
        self.status2 = Status.RESOLVED

        group_user = Group.objects.get(name='User')
        group_support = Group.objects.get(name='Support')
        group_manager = Group.objects.get(name='Manager')

        self.user = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            phone_number='79990000001'
        )
        self.user.groups.add(group_user)

        self.support = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            phone_number='79990000002'
        )
        self.support.groups.add(group_support)

        self.manager = User.objects.create_user(
            email='user3@example.com',
            password='password123',
            phone_number='79990000003'
        )
        self.manager.groups.add(group_manager)

        self.ticket = Ticket.objects.create(
            title='Test title',
            category=self.category,
            description='Test description',
            user=self.user,
            priority=self.priority,
            status=self.status1,
            support=self.support
        )

        self.change_valid_data = {
            'title':'Test title',
            'category':self.category.pk,
            'description':'Test description',
            'priority':self.priority,
            'status':self.status1,
            'support':self.support.pk,
        }

    def test_change_form_is_valid(self):
        instance = self.ticket
        form = TicketChangeForm(data=self.change_valid_data, user=self.support, instance=instance)
        self.assertTrue(form.is_valid())

    def test_title_max_length(self):
        data = self.change_valid_data.copy()
        data['title'] = '1' * 51
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors.as_data()['title'][0].code, 'max_length')

    def test_title_at_max_length(self):
        data = self.change_valid_data.copy()
        data['title'] = '1' * 50
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())

    def test_title_is_null(self):
        data = self.change_valid_data.copy()
        data['title'] = ''
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors.as_data()['title'][0].code, 'required')

    def test_category_is_optional(self):
        data = self.change_valid_data.copy()
        data['category'] = ''
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())

    def test_priority_is_invalid(self):
        data = self.change_valid_data.copy()
        data['priority'] = ''
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertFalse(form.is_valid())

    def test_status_is_invalid(self):
        data = self.change_valid_data.copy()
        data['status'] = ''
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertFalse(form.is_valid())

    def test_support_is_optional(self):
        data = self.change_valid_data.copy()
        data['support'] = ''
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())

    def test_support_is_invalid(self):
        data = self.change_valid_data.copy()
        data['support'] = '-10'
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertFalse(form.is_valid())

    def test_specific_fields_exist(self):
        form = TicketChangeForm(data=self.change_valid_data, user=self.support, instance=self.ticket)
        expected_fields = ['title', 'category', 'description', 'priority', 'status', 'support']
        self.assertSequenceEqual(list(form.fields.keys()), expected_fields)

    def test_support_can_change_assigned_ticket(self):
        data = self.change_valid_data.copy()
        data['title'] = 'Test new title'
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())
        form.save()
        ticket = Ticket.objects.get(pk=self.ticket.pk)
        self.assertEqual(ticket.title, 'Test new title')

    def test_support_cannot_change_resolved_ticket_fields(self):
        self.ticket.status = Status.RESOLVED
        data = self.change_valid_data.copy()
        data['title'] = 'Title cant change'
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())
        form.save()
        ticket = Ticket.objects.get(pk=self.ticket.pk)
        self.assertEqual(ticket.title, 'Test title')

    def test_support_can_save_allowed_changes(self):
        self.ticket.status = Status.RESOLVED
        data = self.change_valid_data.copy()
        data['status'] = Status.NEW
        form = TicketChangeForm(data=data, user=self.support, instance=self.ticket)
        self.assertTrue(form.is_valid())
        form.save()
        ticket = Ticket.objects.get(pk=self.ticket.pk)
        self.assertEqual(ticket.status, Status.NEW)

    def test_manager_can_change_resolved_ticket_fields(self):
        self.ticket.status = Status.RESOLVED
        data = self.change_valid_data.copy()
        data['title'] = 'Title can change manager'
        form = TicketChangeForm(data=data, user=self.manager, instance=self.ticket)
        self.assertTrue(form.is_valid())
        form.save()
        ticket = Ticket.objects.get(pk=self.ticket.pk)
        self.assertEqual(ticket.title, 'Title can change manager')
