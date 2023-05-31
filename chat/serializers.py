from rest_framework import serializers
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Group, Message, BadWord
import re


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class GPCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GPListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        channel_layer = get_channel_layer()
        online_members = channel_layer.groups.get(f'chat_{representation["name"]}', {}).items()
        representation['online_members'] = len(online_members)
        return representation


class GPDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'content']
        read_only_fields = ('sender', 'recipient')
    
    def create(self, validated_data):
        sender = self.context['request'].user
        gp = self.context['view'].kwargs['gp']
        gp = get_object_or_404(Group, name=gp)
        content = validated_data['content']
        bad_words = BadWord.objects.values_list('word', flat=True)
        for bad_word in bad_words:
            bad_word_len = len(bad_word)
            bad_word_re = r'\b' + bad_word + r'\b'
            res = [m.start() for m in re.finditer(bad_word_re, content)]
            for index in res:
                content = content[:index] + "*"*bad_word_len + content[index+bad_word_len:]
        message = Message.objects.create(
            sender = sender,
            recipient = gp,
            content = content,
            is_admin = True
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.recipient.name}',
            {
                'type': 'chat.message',
                'message': f"(Admin) {message.sender}: " + message.content,
                'is_admin': True
            }
        )
        
        return message
