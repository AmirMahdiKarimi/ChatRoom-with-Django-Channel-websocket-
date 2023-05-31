from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=50, blank=True, null=True)


class Group(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return str(self.name)
    

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.content} - {self.timestamp}"

class BadWord(models.Model):
    word = models.TextField()

    def __str__(self) -> str:
        return f"{self.word}"