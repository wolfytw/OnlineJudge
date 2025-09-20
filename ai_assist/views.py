import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.decorators import login_required, super_admin_required
from options.options import SysOptions
from problem.models import Problem
from utils.api import validate_serializer
from utils.ai_assist import chat_with_ai, get_hint, get_solution
from .models import AIConversation, AIMessage, AIUsageStats
from .serializers import (
    AIChatSerializer, AIConversationSerializer, 
    AIMessageSerializer, AIConfigSerializer
)

class AIChatAPIView(APIView):
    @login_required
    @validate_serializer(AIChatSerializer)
    def post(self, request):
        """Handle AI chat messages"""
        if not SysOptions.ai_assist_enabled:
            return Response({"error": "AI assist is disabled"}, status=status.HTTP_400_BAD_REQUEST)
        
        problem_id = request.data.get("problem_id")
        message = request.data.get("message")
        session_id = request.data.get("session_id")
        message_type = request.data.get("message_type", "chat")
        
        # Get problem
        try:
            problem = Problem.objects.get(_id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return Response({"error": "Problem does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create conversation
        if session_id:
            try:
                conversation = AIConversation.objects.get(
                    session_id=session_id, 
                    user=request.user, 
                    problem=problem
                )
            except AIConversation.DoesNotExist:
                return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            session_id = str(uuid.uuid4())
            conversation = AIConversation.objects.create(
                user=request.user,
                problem=problem,
                session_id=session_id
            )
        
        # Save user message
        user_message = AIMessage.objects.create(
            conversation=conversation,
            content=message,
            is_user=True,
            message_type=message_type
        )
        
        # Generate AI response based on message type
        problem_description = f"{problem.title}\n{problem.description}\nInput: {problem.input_description}\nOutput: {problem.output_description}"
        
        try:
            if message_type == "hint":
                ai_response = get_hint(problem_description, message)
            elif message_type == "solution":
                solution_data = get_solution(problem_description, message)
                ai_response = solution_data.get("solution", "")
            else:  # chat
                # Get recent chat history
                recent_messages = conversation.messages.order_by('timestamp')[-10:]
                chat_history = [
                    {"message": msg.content, "is_user": msg.is_user}
                    for msg in recent_messages
                    if msg.id != user_message.id  # Exclude the current message
                ]
                ai_response = chat_with_ai(problem_description, chat_history, message)
            
            # Save AI response
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                content=ai_response,
                is_user=False,
                message_type=message_type
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            
            # Update usage stats
            today = timezone.now().date()
            usage_stats, created = AIUsageStats.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={'messages_count': 0, 'tokens_used': 0}
            )
            usage_stats.messages_count += 1
            usage_stats.save()
            
            return Response({
                "session_id": session_id,
                "user_message": AIMessageSerializer(user_message).data,
                "ai_response": AIMessageSerializer(ai_message).data
            })
            
        except Exception as e:
            return Response(
                {"error": f"AI service error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AIConversationListAPIView(APIView):
    @login_required
    def get(self, request):
        """Get user's AI conversations"""
        problem_id = request.GET.get('problem_id')
        
        conversations = AIConversation.objects.filter(user=request.user)
        if problem_id:
            conversations = conversations.filter(problem___id=problem_id)
        
        conversations = conversations.order_by('-updated_at')[:10]  # Latest 10 conversations
        
        return Response({
            "conversations": AIConversationSerializer(conversations, many=True).data
        })

class AIConversationDetailAPIView(APIView):
    @login_required
    def get(self, request, session_id):
        """Get specific conversation details"""
        try:
            conversation = AIConversation.objects.get(
                session_id=session_id,
                user=request.user
            )
            return Response(AIConversationSerializer(conversation).data)
        except AIConversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @login_required
    def delete(self, request, session_id):
        """Delete a conversation"""
        try:
            conversation = AIConversation.objects.get(
                session_id=session_id,
                user=request.user
            )
            conversation.delete()
            return Response({"message": "Conversation deleted successfully"})
        except AIConversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

class AIConfigAPIView(APIView):
    @super_admin_required
    def get(self, request):
        """Get AI configuration"""
        config = {
            "ai_assist_enabled": SysOptions.ai_assist_enabled,
            "openai_api_key": "***" if SysOptions.openai_api_key else "",
            "openai_model": SysOptions.openai_model,
            "openai_base_url": SysOptions.openai_base_url,
            "azure_openai_endpoint": SysOptions.azure_openai_endpoint,
            "azure_openai_key": "***" if SysOptions.azure_openai_key else "",
            "azure_openai_deployment_name": SysOptions.azure_openai_deployment_name,
        }
        return Response(config)
    
    @super_admin_required
    @validate_serializer(AIConfigSerializer)
    def post(self, request):
        """Update AI configuration"""
        data = request.data
        
        SysOptions.ai_assist_enabled = data.get("ai_assist_enabled")
        
        if data.get("openai_api_key") and data.get("openai_api_key") != "***":
            SysOptions.openai_api_key = data.get("openai_api_key")
        
        if data.get("openai_model"):
            SysOptions.openai_model = data.get("openai_model")
            
        if data.get("openai_base_url"):
            SysOptions.openai_base_url = data.get("openai_base_url")
            
        if data.get("azure_openai_endpoint"):
            SysOptions.azure_openai_endpoint = data.get("azure_openai_endpoint")
            
        if data.get("azure_openai_key") and data.get("azure_openai_key") != "***":
            SysOptions.azure_openai_key = data.get("azure_openai_key")
            
        if data.get("azure_openai_deployment_name"):
            SysOptions.azure_openai_deployment_name = data.get("azure_openai_deployment_name")
        
        return Response({"message": "AI configuration updated successfully"})

class AIUsageStatsAPIView(APIView):
    @login_required
    def get(self, request):
        """Get user's AI usage statistics"""
        stats = AIUsageStats.objects.filter(user=request.user).order_by('-date')[:30]
        
        data = [{
            "date": stat.date,
            "messages_count": stat.messages_count,
            "tokens_used": stat.tokens_used
        } for stat in stats]
        
        return Response({"usage_stats": data})