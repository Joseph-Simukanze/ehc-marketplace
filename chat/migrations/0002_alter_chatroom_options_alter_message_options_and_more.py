# Generated by Django 4.2.7 on 2025-05-14 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatroom',
            options={},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={},
        ),
        migrations.RenameField(
            model_name='message',
            old_name='text',
            new_name='content',
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='chatroom',
            unique_together={('buyer', 'seller')},
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='product',
        ),
    ]
