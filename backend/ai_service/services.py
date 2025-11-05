import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
from x_monitor.models import Tweet, AIAnalysis

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini AI サービス"""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Gemini モデルを初期化"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
    
    def analyze_tweet_sentiment(self, text: str) -> str:
        """ツイートの感情分析"""
        try:
            prompt = f"""
            以下のツイートの感情を分析してください。
            結果は「positive」「negative」「neutral」のいずれかで返してください。
            
            ツイート: {text}
            
            感情:
            """
            
            response = self.model.generate_content(prompt)
            sentiment = response.text.strip().lower()
            
            # 結果を正規化
            if 'positive' in sentiment:
                return 'positive'
            elif 'negative' in sentiment:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 'neutral'
    
    def summarize_tweet(self, text: str) -> str:
        """ツイートの要約"""
        try:
            prompt = f"""
            以下のツイートを簡潔に要約してください（50文字以内）。
            要約のみを返してください。
            
            ツイート: {text}
            
            要約:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing tweet: {e}")
            return text[:50] + "..." if len(text) > 50 else text
    
    def extract_topics(self, text: str) -> List[str]:
        """ツイートからトピックを抽出"""
        try:
            prompt = f"""
            以下のツイートから主要なトピックやキーワードを抽出してください。
            結果はJSON配列形式で返してください。例: ["トピック1", "トピック2", "トピック3"]
            
            ツイート: {text}
            
            トピック:
            """
            
            response = self.model.generate_content(prompt)
            topics_text = response.text.strip()
            
            # JSON形式の結果をパース
            try:
                topics = json.loads(topics_text)
                return topics if isinstance(topics, list) else []
            except json.JSONDecodeError:
                # JSONパースに失敗した場合は、カンマ区切りで分割
                return [topic.strip() for topic in topics_text.split(',')]
                
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def calculate_importance_score(self, text: str, hashtags: List[str], metrics: Dict) -> float:
        """ツイートの重要度スコアを計算"""
        try:
            prompt = f"""
            以下のツイートの重要度を0.0から1.0の間で評価してください。
            スキー場情報、雪の状況、営業情報などが含まれている場合は高いスコアをつけてください。
            
            ツイート: {text}
            ハッシュタグ: {', '.join(hashtags)}
            いいね数: {metrics.get('like_count', 0)}
            リツイート数: {metrics.get('retweet_count', 0)}
            
            重要度スコア（0.0-1.0）:
            """
            
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            
            # スコアを抽出
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # 0.0-1.0の範囲に制限
            except ValueError:
                # 数値変換に失敗した場合は基本スコアを計算
                return self._calculate_basic_importance_score(text, hashtags, metrics)
                
        except Exception as e:
            logger.error(f"Error calculating importance score: {e}")
            return self._calculate_basic_importance_score(text, hashtags, metrics)
    
    def _calculate_basic_importance_score(self, text: str, hashtags: List[str], metrics: Dict) -> float:
        """基本的な重要度スコア計算"""
        score = 0.0
        
        # キーワードベースのスコア
        ski_keywords = ['スキー', 'スノボ', 'ゲレンデ', '雪', 'リフト', '営業', '積雪']
        for keyword in ski_keywords:
            if keyword in text:
                score += 0.1
        
        # エンゲージメントベースのスコア
        like_count = metrics.get('like_count', 0)
        retweet_count = metrics.get('retweet_count', 0)
        
        # いいね数とリツイート数を正規化してスコアに追加
        engagement_score = min(0.3, (like_count + retweet_count * 2) / 100)
        score += engagement_score
        
        # ハッシュタグの影響
        relevant_hashtags = ['スキー場', 'ゲレンデ', '雪質', 'powder']
        for hashtag in hashtags:
            if any(keyword in hashtag.lower() for keyword in relevant_hashtags):
                score += 0.1
        
        return min(1.0, score)
    
    def analyze_tweet_comprehensive(self, tweet: Tweet) -> Dict:
        """ツイートの包括的な分析"""
        try:
            metrics = {
                'like_count': tweet.like_count,
                'retweet_count': tweet.retweet_count,
                'reply_count': tweet.reply_count
            }
            
            sentiment = self.analyze_tweet_sentiment(tweet.content)
            summary = self.summarize_tweet(tweet.content)
            topics = self.extract_topics(tweet.content)
            importance_score = self.calculate_importance_score(
                tweet.content, 
                tweet.hashtags, 
                metrics
            )
            
            return {
                'sentiment': sentiment,
                'summary': summary,
                'topics': topics,
                'importance_score': importance_score
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                'sentiment': 'neutral',
                'summary': tweet.content[:50] + "..." if len(tweet.content) > 50 else tweet.content,
                'topics': [],
                'importance_score': 0.0
            }


def analyze_tweet_with_ai(tweet_id: int) -> Optional[AIAnalysis]:
    """ツイートをAIで分析してAIAnalysisオブジェクトを作成"""
    try:
        tweet = Tweet.objects.get(id=tweet_id)
        
        # 既に分析済みの場合はスキップ
        if hasattr(tweet, 'ai_analysis'):
            return tweet.ai_analysis
        
        gemini_service = GeminiService()
        analysis_result = gemini_service.analyze_tweet_comprehensive(tweet)
        
        ai_analysis = AIAnalysis.objects.create(
            tweet=tweet,
            sentiment=analysis_result['sentiment'],
            summary=analysis_result['summary'],
            topics=analysis_result['topics'],
            importance_score=analysis_result['importance_score']
        )
        
        return ai_analysis
        
    except Tweet.DoesNotExist:
        logger.error(f"Tweet with id {tweet_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error analyzing tweet {tweet_id}: {e}")
        return None