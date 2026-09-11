from django.test import TestCase
from users.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from tickets.models import Ticket, Category, Priority, Status
from tickets.forms import TicketCreationForm, TicketChangeForm

class TicketViewTests(TestCase):
    def setUp(self):
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

        self.category = Category.objects.create(
            title='Операционная система',
            description='Бла Бла Бла'
            )

        self.priority = Priority.LOW

        self.status1 = Status.NEW
        self.status2 = Status.RESOLVED

        self.ticket = Ticket.objects.create(
            title='Test title',
            category=self.category,
            description='Test description',
            user=self.user,
            priority=self.priority,
            status=self.status1,
            support=self.support
        )

        self.ticket2 = Ticket.objects.create(
            title='Test title',
            category=self.category,
            description='Test description',
            user=self.manager,
            priority=self.priority,
            status=self.status1,
            support=self.support
        )

        self.ticket3 = Ticket.objects.create(
            title='Test title',
            category=self.category,
            description='Test description',
            user=self.manager,
            priority=self.priority,
            status=self.status1,
            support=None
        )

        self.ticket4 = Ticket.objects.create(
            title='Test title',
            category=self.category,
            description='Test description',
            user=self.support,
            priority=self.priority,
            status=self.status1,
            support=None
        )

        self.change_valid_data = {
            'title':'Test new title',
            'category':self.category.pk,
            'description':'Test new description',
            'priority':self.priority,
            'status':self.status1,
            'support':self.support.pk,
        }

    def test_list_unauthorized(self):
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ticket-list')}")

    def test_detail_unauthorized(self):
        response = self.client.get(reverse('ticket-detail', kwargs={'pk':self.ticket.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ticket-detail', kwargs={'pk':self.ticket.pk})}")

    def test_change_unauthorized(self):
        response = self.client.get(reverse('ticket-change', kwargs={'pk':self.ticket.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ticket-change', kwargs={'pk':self.ticket.pk})}")

    def test_user_sees_only_own_tickets(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ticket, response.context['tickets'])
        self.assertNotIn(self.ticket2, response.context['tickets'])

    def test_support_sees_created_and_assigned_tickets(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ticket, response.context['tickets'])
        self.assertIn(self.ticket2, response.context['tickets'])
        self.assertNotIn(self.ticket3, response.context['tickets'])

    def test_manager_sees_all_tickets(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.ticket, self.ticket2, self.ticket3, self.ticket4],
            ordered=False
        )

    def test_user_can_open_own_ticket(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ticket-detail', kwargs={'pk':self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ticket, response.context['ticket'])

    def test_user_cannot_open_foreign_ticket(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ticket-detail', kwargs={'pk':self.ticket2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_support_cannot_open_inaccessible_ticket(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('ticket-detail', kwargs={'pk':self.ticket3.pk}))
        self.assertEqual(response.status_code, 404)

    def test_support_can_change_assigned_ticket(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('ticket-change', kwargs={'pk':self.ticket2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ticket2, response.context['ticket'])

    def test_support_cannot_change_unassigned_ticket(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('ticket-detail', kwargs={'pk':self.ticket4.pk}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('ticket-change', kwargs={'pk':self.ticket4.pk}), data=self.change_valid_data)
        self.assertEqual(response.status_code, 403)

    def test_manager_can_change_any_ticket(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('ticket-change', kwargs={'pk':self.ticket3.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ticket'], self.ticket3)

    def test_successful_ticket_change(self):
        self.client.force_login(self.support)
        response = self.client.post(reverse('ticket-change', kwargs={'pk':self.ticket2.pk}), data=self.change_valid_data)
        self.assertRedirects(
            response,
            reverse('ticket-detail', kwargs={'pk': self.ticket2.pk})
        )
        ticket = Ticket.objects.get(pk=self.ticket2.pk)
        self.assertEqual(ticket.title, 'Test new title')

    def test_invalid_ticket_change(self):
        self.client.force_login(self.support)
        data = self.change_valid_data.copy()
        data['title'] = '1' * 51
        response = self.client.post(reverse('ticket-change', kwargs={'pk':self.ticket2.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        ticket = Ticket.objects.get(pk=self.ticket2.pk)
        self.assertEqual(ticket.title, 'Test title')
        self.assertIn('title', response.context['form'].errors)
