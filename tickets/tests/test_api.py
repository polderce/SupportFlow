from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from tickets.models import Ticket, Category, Status, Priority


class TicketTests(APITestCase):
    def setUp(self):
        self.group_user = Group.objects.get(name='User')
        self.group_support = Group.objects.get(name='Support')
        self.group_manager = Group.objects.get(name='Manager')

        self.user = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            phone_number='+79990000001'
        )
        self.user.groups.add(self.group_user)

        self.support = User.objects.create_user(
            email='support@example.com',
            password='password123',
            phone_number='+79990000002'
        )
        self.support.groups.add(self.group_support)

        self.manager = User.objects.create_user(
            email='manager@example.com',
            password='password123',
            phone_number='+79990000003'
        )
        self.manager.groups.add(self.group_manager)

        self.category = Category.objects.create(
            title='Техническая проблема',
            description='Тестовая категория'
        )

        self.ticket = Ticket.objects.create(
            user=self.user,
            title='Тестовый тикет',
            category=self.category,
            description='Описание тестового тикета',
            priority=Priority.MEDIUM,
            status=Status.NEW,
            support=self.support
        )

        self.closed_ticket = Ticket.objects.create(
            user=self.user,
            title='Закрытый тикет',
            category=self.category,
            description='Закрытый тикет',
            priority=Priority.MEDIUM,
            status=Status.CLOSED,
            support=self.support
        )

    def test_unauthenticated_user_cannot_access_api(self):
        url = reverse('tickets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_access_ticket_list(self):
        self.client.force_login(user=self.user)
        url = reverse('tickets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_sees_only_own_tickets(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='password123',
            phone_number='+79990000004'
        )
        other_user.groups.add(self.group_user)

        other_ticket = Ticket.objects.create(
            user=other_user,
            title='Чужой тикет',
            description='Чужой тикет'
        )

        self.client.force_login(user=self.user)
        url = reverse('tickets-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ticket_ids = [
            ticket['id']
            for ticket in response.data['results']
        ]

        self.assertIn(self.ticket.pk, ticket_ids)
        self.assertNotIn(other_ticket.pk, ticket_ids)

    def test_support_sees_assigned_and_created_tickets(self):
        created_ticket = Ticket.objects.create(
            user=self.support,
            title='Тикет Support',
            description='Создан Support'
        )

        self.client.force_login(user=self.support)
        url = reverse('tickets-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ticket_ids = [
            ticket['id']
            for ticket in response.data['results']
        ]

        self.assertIn(self.ticket.pk, ticket_ids)
        self.assertIn(created_ticket.pk, ticket_ids)
        self.assertIn(self.closed_ticket.pk, ticket_ids)

    def test_authenticated_user_can_create_ticket(self):
        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        data = {
            'title': 'Новый тикет',
            'category': self.category.pk,
            'description': 'Описание нового тикета'
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        ticket = Ticket.objects.get(pk=response.data['id'])

        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.title, 'Новый тикет')
        self.assertEqual(ticket.category, self.category)
        self.assertEqual(ticket.priority, Priority.LOW)
        self.assertEqual(ticket.status, Status.NEW)
        self.assertIsNone(ticket.support)

    def test_support_can_update_assigned_ticket(self):
        self.client.force_login(user=self.support)

        url = reverse(
            'tickets-detail',
            kwargs={'pk': self.ticket.pk}
        )

        response = self.client.patch(
            url,
            {'priority': Priority.HIGH}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.ticket.refresh_from_db()

        self.assertEqual(
            self.ticket.priority,
            Priority.HIGH
        )

    def test_support_cannot_update_unassigned_ticket(self):
        ticket = Ticket.objects.create(
            user=self.support,
            title='Неназначенный тикет',
            description='Тикет без Support'
        )

        self.client.force_login(user=self.support)

        url = reverse(
            'tickets-detail',
            kwargs={'pk': ticket.pk}
        )

        response = self.client.patch(
            url,
            {'priority': Priority.HIGH}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_manager_can_update_any_ticket(self):
        self.client.force_login(user=self.manager)

        url = reverse(
            'tickets-detail',
            kwargs={'pk': self.ticket.pk}
        )

        response = self.client.patch(
            url,
            {
                'priority': Priority.CRITICAL,
                'status': Status.IN_PROGRESS
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.ticket.refresh_from_db()

        self.assertEqual(
            self.ticket.priority,
            Priority.CRITICAL
        )

        self.assertEqual(
            self.ticket.status,
            Status.IN_PROGRESS
        )

    def test_support_can_change_status_of_closed_ticket(self):
        self.client.force_login(user=self.support)

        url = reverse(
            'tickets-detail',
            kwargs={'pk': self.closed_ticket.pk}
        )

        response = self.client.patch(
            url,
            {'status': Status.RESOLVED}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_support_cannot_change_basic_fields_of_closed_ticket(self):
        self.client.force_login(user=self.support)

        url = reverse(
            'tickets-detail',
            kwargs={'pk': self.closed_ticket.pk}
        )

        response = self.client.patch(
            url,
            {'priority': Priority.HIGH}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'non_field_errors',
            response.data
        )

    def test_can_filter_tickets_by_status(self):
        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        response = self.client.get(
            url,
            {'status': Status.NEW}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for ticket in response.data['results']:
            self.assertEqual(
                ticket['status'],
                Status.NEW
            )

    def test_can_filter_tickets_by_date_range(self):
        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        response = self.client.get(
            url,
            {
                'date_from': '2026-01-01',
                'date_to': '2026-12-31'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_can_search_tickets(self):
        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        response = self.client.get(
            url,
            {'search': 'Тестовый'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreaterEqual(
            response.data['count'],
            1
        )

    def test_can_order_tickets(self):
        Ticket.objects.create(
            user=self.user,
            title='Low priority',
            description='Test',
            priority=Priority.LOW
        )

        Ticket.objects.create(
            user=self.user,
            title='Critical priority',
            description='Test',
            priority=Priority.CRITICAL
        )

        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        response = self.client.get(
            url,
            {'ordering': 'priority'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        priorities = [
            ticket['priority']
            for ticket in response.data['results']
        ]

        self.assertEqual(
            priorities,
            sorted(priorities)
        )

    def test_ticket_list_is_paginated(self):
        self.client.force_login(user=self.user)

        url = reverse('tickets-list')
        response = self.client.get(
            url,
            {'limit': 1, 'offset': 0}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertLessEqual(
            len(response.data['results']),
            1
        )
