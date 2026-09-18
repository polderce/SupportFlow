from rest_framework import serializers
from .models import Ticket
from .permissions import can_edit_basic_fields

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance:
            fields_to_remove = ['user', 'created_at', 'updated_at', 'priority', 'status', 'support']
        else:
            fields_to_remove = ['user', 'created_at', 'updated_at']
        for field in fields_to_remove:
            self.fields.pop(field, None)

    def validate(self, data):
        if self.instance is not None:
            user = self.context['request'].user
            ticket = self.instance
            if not can_edit_basic_fields(user, ticket):
                input_fields = set(data.keys())
                if input_fields - {'status'}:
                    raise serializers.ValidationError(
                        "Базовые поля недоступны для изменения."
                    )
        return data

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'title',
            'description',
            'category',
            'priority',
            'status',
            'support',
        ]
