# Generated by Django 4.2.1 on 2023-05-28 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_message_recipient'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.TextField()),
            ],
        ),
    ]
