from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MCPTweetResourceViewSet, MCPAccountResourceViewSet

app_name = 'mcp_service'

router = DefaultRouter()
router.register(r'tweets', MCPTweetResourceViewSet, basename='mcp-tweet')
router.register(r'accounts', MCPAccountResourceViewSet, basename='mcp-account')

urlpatterns = [
    path('', include(router.urls)),
]
