from django.test import TestCase, Client
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

from users.models import User
from tickets.models import Ticket, Category, Priority, Status

class DashboardViewTests(TestCase):
    def setUp(self):
        self.user_group = Group.objects.get(name='User')
        self.support_group = Group.objects.get(name='Support')
        self.manager_group = Group.objects.get(name='Manager')

        self.user = User.objects.create_user(
            email='user@example.com',
            first_name='Test',
            last_name='User',
            phone_number='1111111111',
            password='password123'
        )
        self.user.groups.add(self.user_group)

        self.support = User.objects.create_user(
            email='support@example.com',
            first_name='Test',
            last_name='Support',
            phone_number='2222222222',
            password='password123'
        )
        self.support.groups.add(self.support_group)

        self.manager = User.objects.create_user(
            email='manager@example.com',
            first_name='Test',
            last_name='Manager',
            phone_number='3333333333',
            password='password123'
        )
        self.manager.groups.add(self.manager_group)

        self.other_user = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            phone_number='4444444444',
            password='password123'
        )
        self.other_user.groups.add(self.user_group)

        self.category = Category.objects.create(
            title='Technical',
            description='Technical issues'
        )

        self.other_category = Category.objects.create(
            title='Billing',
            description='Billing issues'
        )

        self.ticket = Ticket.objects.create(
            user=self.user,
            title='Test ticket',
            category=self.category,
            description='Test description',
            priority=Priority.MEDIUM,
            status=Status.NEW,
        )
        Ticket.objects.filter(pk=self.ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 9, 14, 30))
        )

        self.support1_ticket = Ticket.objects.create(
            user=self.other_user,
            title='Support ticket',
            category=self.other_category,
            description='Support description',
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
            support=self.support,
        )
        Ticket.objects.filter(pk=self.support1_ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 5, 14, 30))
        )

        self.support2_ticket = Ticket.objects.create(
            user=self.support,
            title='Support ticket',
            category=self.other_category,
            description='Support description',
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
        )
        Ticket.objects.filter(pk=self.support2_ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 12, 14, 30))
        )

        self.support3_ticket = Ticket.objects.create(
            user=self.other_user,
            title='Billing issue',
            category=self.other_category,
            description='Support description',
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
            support=self.support,
        )
        Ticket.objects.filter(pk=self.support3_ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 11, 14, 30))
        )

        self.other1_ticket = Ticket.objects.create(
            user=self.other_user,
            title='Other ticket',
            category=self.category,
            description='Other description',
            priority=Priority.LOW,
            status=Status.CLOSED,
        )
        Ticket.objects.filter(pk=self.other1_ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 10, 14, 30))
        )

        self.other2_ticket = Ticket.objects.create(
            user=self.other_user,
            title='Support ticket',
            category=self.category,
            description='Other description',
            priority=Priority.LOW,
            status=Status.CLOSED,
        )
        Ticket.objects.filter(pk=self.other2_ticket.pk).update(
            created_at=timezone.make_aware(datetime(2026, 9, 10, 15, 30))
        )

        self.client = Client()

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_allows_support(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard_support_sees_own_and_assigned_tickets(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.support1_ticket, response.context['tickets'])
        self.assertIn(self.support2_ticket, response.context['tickets'])
        self.assertNotIn(self.ticket, response.context['tickets'])
        self.assertNotIn(self.other1_ticket, response.context['tickets'])
        self.assertNotIn(self.other2_ticket, response.context['tickets'])

    def test_dashboard_manager_sees_all_tickets(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.ticket, self.support1_ticket, self.support2_ticket, self.support3_ticket, self.other1_ticket, self.other2_ticket],
            ordered=False
        )

    def test_dashboard_search_by_title(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('dashboard'), {'search':'Support'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.support1_ticket, response.context['tickets'])
        self.assertIn(self.support2_ticket, response.context['tickets'])
        self.assertNotIn(self.other2_ticket, response.context['tickets'])
        self.assertNotIn(self.support3_ticket, response.context['tickets'])

    def test_dashboard_empty_search_returns_all_visible_tickets(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse('dashboard'), {'search':''})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support1_ticket, self.support2_ticket, self.support3_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_category(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'category':self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.ticket, self.other1_ticket, self.other2_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_priority(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'priority':Priority.HIGH})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support1_ticket, self.support2_ticket, self.support3_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_status(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'status':Status.CLOSED})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.other1_ticket, self.other2_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_date_from(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'date_from': '2026-09-10'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support2_ticket, self.support3_ticket, self.other1_ticket, self.other2_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_date_to(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'date_to': '2026-09-05'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support1_ticket],
            ordered=False
        )

    def test_dashboard_filters_by_date_range(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'date_from': '2026-09-09', 'date_to': '2026-09-11'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.ticket, self.support3_ticket, self.other1_ticket, self.other2_ticket],
            ordered=False
        )

    def test_dashboard_combines_filters_with_and(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {
            'category': self.other_category.pk,
            'priority': Priority.HIGH,
            'status': Status.IN_PROGRESS,
        })
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support1_ticket, self.support2_ticket, self.support3_ticket],
            ordered=False
        )

    def test_dashboard_orders_tickets_by_created_at_desc(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'date_from': '2026-09-09', 'date_to': '2026-09-11'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['tickets'],
            [self.support3_ticket, self.other2_ticket, self.other1_ticket, self.ticket],
            ordered=True
        )
