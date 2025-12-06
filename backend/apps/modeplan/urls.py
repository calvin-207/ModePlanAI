from django.urls import path
from rest_framework import routers
from .views import MConversationsViewSet,MConversationsLogViewSet, ChatAPIView

system_url = routers.SimpleRouter()

system_url.register(r'conversations', MConversationsViewSet, basename='MConversations')
system_url.register(r'conversationLogs', MConversationsLogViewSet, basename='MConversationLog')

urlpatterns = [
    path("chat/", ChatAPIView.as_view()),
]

urlpatterns += system_url.urls