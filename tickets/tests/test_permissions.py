from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from users.models import User
from tickets.models import Ticket
from tickets.permissions import get_visible_tickets, can_change_ticket

class PermissionTests(TestCase):
    def setUp(self):
        # Находим permissions
        content_type = ContentType.objects.get_for_model(Ticket)

        permission_view = Permission.objects.get(codename='view_ticket', content_type = content_type)
        permission_add = Permission.objects.get(codename='add_ticket', content_type = content_type)
        permission_change = Permission.objects.get(codename='change_ticket', content_type = content_type)

        # Находим Groups
        group_user = Group.objects.get(name='User')

        group_support = Group.objects.get(name='Support')

        group_manager = Group.objects.get(name='Manager')

        # Создаем пользователей с группой "User"
        self.user_with_user1 = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            phone_number='79990000001'
        )
        self.user_with_user1.groups.add(group_user)

        self.user_with_user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            phone_number='79990000002'
        )
        self.user_with_user2.groups.add(group_user)


        # Создаем пользователей с группой "Support"
        self.user_with_support1 = User.objects.create_user(
            email='user3@example.com',
            password='password123',
            phone_number='79990000003'
        )
        self.user_with_support1.groups.add(group_support)

        self.user_with_support2 = User.objects.create_user(
            email='user4@example.com',
            password='password123',
            phone_number='79990000004'
        )
        self.user_with_support2.groups.add(group_support)


        # Создаем пользователя с группой "Manager"
        self.user_with_manager = User.objects.create_user(
            email='user5@example.com',
            password='password123',
            phone_number='79990000005'
        )
        self.user_with_manager.groups.add(group_manager)

        self.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='secret_admin_password',
            first_name='Главный',
            last_name='Админ',
            phone_number='79990000006'
        )

        # Создаём тикет от 1-го user'а
        self.ticket1 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_user1,
        )

        # Создаём тикет от 2-го user'а
        self.ticket2 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_user2,
        )

        # Создаём тикет c назначенным 1-м саппортом от 1-го user'а
        self.ticket_with_support1 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_user1,
            support=self.user_with_support1,
        )

        # Создаём тикет c назначенным 1-м саппортом от 2-го user'а
        self.ticket_with_support2 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_user2,
            support=self.user_with_support1,
        )

        # Создаём тикет c назначенным 2-м саппортом от самого support'а
        self.ticket_with_support3 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_support2,
            support=self.user_with_support2,
        )

        # Создаём тикет c назначенным 2-м саппортом от 1-го user'а
        self.ticket_with_support4 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_user1,
            support=self.user_with_support2,
        )

        # Создаём тикет c назначенным 1-м саппортом от 2-го support'а
        self.ticket_with_support5 = Ticket.objects.create(
            title='Test title',
            category=None,
            description='Test description',
            user=self.user_with_support2,
            support=self.user_with_support1,
        )

    def test_get_visible_tickets(self):
        result_user1 = get_visible_tickets(self.user_with_user1)
        self.assertQuerySetEqual(result_user1, [self.ticket1, self.ticket_with_support1, self.ticket_with_support4], ordered=False)

        result_user2 = get_visible_tickets(self.user_with_user2)
        self.assertQuerySetEqual(result_user2, [self.ticket2, self.ticket_with_support2], ordered=False)

        result_support1 = get_visible_tickets(self.user_with_support1)
        self.assertQuerySetEqual(result_support1, [self.ticket_with_support1, self.ticket_with_support2, self.ticket_with_support5], ordered=False)

        result_support2 = get_visible_tickets(self.user_with_support2)
        self.assertQuerySetEqual(result_support2, [self.ticket_with_support3, self.ticket_with_support4, self.ticket_with_support5], ordered=False)

        result_manager = get_visible_tickets(self.user_with_manager)
        self.assertQuerySetEqual(result_manager, [self.ticket1, self.ticket2, self.ticket_with_support1, self.ticket_with_support2, self.ticket_with_support3, self.ticket_with_support4, self.ticket_with_support5], ordered=False)

    def test_can_change_ticket(self):
        result_user = can_change_ticket(self.user_with_user1, self.ticket1)
        self.assertFalse(result_user)

        result_support1 = can_change_ticket(self.user_with_support1, self.ticket1)
        self.assertFalse(result_support1)

        result_support2 = can_change_ticket(self.user_with_support1, self.ticket_with_support1)
        self.assertTrue(result_support2)

        result_manager = can_change_ticket(self.user_with_manager, self.ticket1)
        self.assertTrue(result_manager)

    def test_superuser_permissions(self):
        visible_tickets = get_visible_tickets(self.superuser)
        self.assertQuerySetEqual(visible_tickets, [self.ticket1, self.ticket2, self.ticket_with_support1, self.ticket_with_support2, self.ticket_with_support3, self.ticket_with_support4, self.ticket_with_support5], ordered=False)
        self.assertTrue(can_change_ticket(self.superuser, self.ticket1))
