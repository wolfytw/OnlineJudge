from django.db import models
from account.models import User
from problem.models import Problem
from utils.models import JSONField

class AIConversation(models.Model):
    """AI conversation session for a specific problem"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "ai_conversation"
        unique_together = ('user', 'problem', 'session_id')
        ordering = ['-updated_at']

class AIMessage(models.Model):
    """Individual messages in AI conversation"""
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField()  # True if from user, False if from AI
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=20, default='chat')  # 'chat', 'hint', 'solution'
    metadata = JSONField(default=dict)  # Store additional info like tokens used, model, etc.
    
    class Meta:
        db_table = "ai_message"
        ordering = ['timestamp']

class AIUsageStats(models.Model):
    """Track AI usage statistics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    messages_count = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    
    class Meta:
        db_table = "ai_usage_stats"
        unique_together = ('user', 'date')
        ordering = ['-date']