# -*- coding: utf-8 -*-
# Generated manually for AI Assist functionality
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problem', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ai_conversation',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='AIMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_user', models.BooleanField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message_type', models.CharField(default='chat', max_length=20)),
                ('metadata', utils.models.JSONField(default=dict)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='ai_assist.AIConversation')),
            ],
            options={
                'db_table': 'ai_message',
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AIUsageStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('messages_count', models.IntegerField(default=0)),
                ('tokens_used', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ai_usage_stats',
                'ordering': ['-date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='aiusagestats',
            unique_together={('user', 'date')},
        ),
        migrations.AlterUniqueTogether(
            name='aiconversation',
            unique_together={('user', 'problem', 'session_id')},
        ),
    ]