from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import GeminiService


@swagger_auto_schema(
    method='post',
    operation_description="テキストの感情分析",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING, description='分析対象のテキスト')
        },
        required=['text']
    ),
    responses={
        200: openapi.Response(
            description="分析成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'sentiment': openapi.Schema(type=openapi.TYPE_STRING),
                    'text': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_sentiment(request):
    """感情分析API"""
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'テキストが必要です'}, status=400)
    
    gemini_service = GeminiService()
    sentiment = gemini_service.analyze_tweet_sentiment(text)
    
    return Response({
        'sentiment': sentiment,
        'text': text
    })


@swagger_auto_schema(
    method='post',
    operation_description="テキストの要約",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING, description='要約対象のテキスト')
        },
        required=['text']
    ),
    responses={
        200: openapi.Response(
            description="要約成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'summary': openapi.Schema(type=openapi.TYPE_STRING),
                    'original_text': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def summarize_text(request):
    """テキスト要約API"""
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'テキストが必要です'}, status=400)
    
    gemini_service = GeminiService()
    summary = gemini_service.summarize_tweet(text)
    
    return Response({
        'summary': summary,
        'original_text': text
    })


@swagger_auto_schema(
    method='post',
    operation_description="テキストからトピック抽出",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING, description='分析対象のテキスト')
        },
        required=['text']
    ),
    responses={
        200: openapi.Response(
            description="抽出成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'topics': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)
                    ),
                    'text': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_topics(request):
    """トピック抽出API"""
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'テキストが必要です'}, status=400)
    
    gemini_service = GeminiService()
    topics = gemini_service.extract_topics(text)
    
    return Response({
        'topics': topics,
        'text': text
    })


urlpatterns = [
    path('sentiment/', analyze_sentiment, name='analyze-sentiment'),
    path('summarize/', summarize_text, name='summarize-text'),
    path('topics/', extract_topics, name='extract-topics'),
]