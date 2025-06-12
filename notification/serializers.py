from rest_framework import serializers
from .models import Notification
from user.serializers import UserResponseSerializer
from django.contrib.auth import get_user_model
User=get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    user=UserResponseSerializer(read_only=True)
    class Meta:
        model= Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at'] 
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        user=self.context['request'].user
        if user.is_employer:
            raise serializers.ValidationError("Employers are not allowed to receive notifications of job posting.")
        return data


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)