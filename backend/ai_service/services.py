import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from x_monitor.models import Tweet, AIAnalysis, AIPromptRule, RecommendedTweet

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


class AIService:
    """AI服务统一接口"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def analyze_tweet_relevance(self, tweet_content: str, user_prompt: str = None) -> Dict:
        """
        分析推文是否与用户需求相关
        
        Args:
            tweet_content: 推文内容
            user_prompt: 用户自定义的判断标准（可选）
        
        Returns:
            {
                'is_relevant': bool,  # 是否相关
                'score': float,  # 相关度评分 0-1
                'reason': str,  # AI推荐理由
                'summary': str  # 推文摘要
            }
        """
        try:
            # 默认提示词：关注滑雪场信息
            default_prompt = """
            你是一个专业的滑雪信息分析助手。请判断以下推文是否包含有价值的滑雪相关信息。
            
            重点关注：
            - 滑雪场营业信息（开放时间、关闭通知）
            - 雪况报告（积雪深度、雪质）
            - 天气预报（降雪、气温）
            - 活动公告（比赛、特别活动）
            - 设施更新（缆车、餐厅）
            - 折扣优惠信息
            
            请不要推荐：
            - 纯粹的社交闲聊
            - 无关的广告
            - 低质量内容
            """
            
            prompt = user_prompt or default_prompt
            
            analysis_prompt = f"""
            {prompt}
            
            推文内容：
            {tweet_content}
            
            请以JSON格式返回分析结果：
            {{
                "is_relevant": true/false,
                "score": 0.0-1.0,
                "reason": "推荐理由（如果相关）或不推荐原因",
                "summary": "推文的简短摘要（20字以内）"
            }}
            """
            
            response = self.gemini_service.model.generate_content(analysis_prompt)
            result_text = response.text.strip()
            
            # 尝试解析JSON
            try:
                # 提取JSON部分（可能包含在```json```代码块中）
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                
                result = json.loads(result_text)
                
                return {
                    'is_relevant': result.get('is_relevant', False),
                    'score': float(result.get('score', 0.0)),
                    'reason': result.get('reason', ''),
                    'summary': result.get('summary', tweet_content[:50])
                }
                
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用启发式方法
                logger.warning(f"Failed to parse AI response as JSON: {result_text}")
                return self._heuristic_relevance_check(tweet_content)
                
        except Exception as e:
            logger.error(f"Error in AI relevance analysis: {e}")
            return self._heuristic_relevance_check(tweet_content)
    
    def _heuristic_relevance_check(self, tweet_content: str) -> Dict:
        """启发式相关性检查（当AI调用失败时使用）"""
        ski_keywords = [
            'スキー', 'スキー場', 'ゲレンデ', 'スノボ', 'スノーボード',
            '雪', '積雪', 'パウダー', 'リフト', '営業', 'オープン',
            'ski', 'snow', 'resort', 'slope', 'powder'
        ]
        
        keyword_count = sum(1 for keyword in ski_keywords if keyword in tweet_content.lower())
        
        is_relevant = keyword_count >= 2
        score = min(1.0, keyword_count * 0.2)
        
        return {
            'is_relevant': is_relevant,
            'score': score,
            'reason': f'包含{keyword_count}个滑雪相关关键词' if is_relevant else '未包含足够的滑雪相关信息',
            'summary': tweet_content[:50] + ('...' if len(tweet_content) > 50 else '')
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


class AIRecommendationService:
    """AI推荐服务 - 基于自定义prompt规则筛选推文"""
    
    def __init__(self):
        self.gemini = GeminiService()
    
    def filter_tweets_by_prompt(
        self, 
        tweets: List[Tweet], 
        prompt_rule: AIPromptRule
    ) -> List[Tuple[Tweet, str, float]]:
        """
        使用AI prompt规则筛选推文
        
        Args:
            tweets: 推文列表
            prompt_rule: AI提示词规则
            
        Returns:
            List of (tweet, reason, score) tuples for matching tweets
        """
        if not tweets:
            return []
        
        try:
            # 构建批量分析的prompt
            tweets_text = "\n\n".join([
                f"推文{i+1} (ID: {tweet.tweet_id}):\n内容: {tweet.content}\n发布时间: {tweet.posted_at}"
                for i, tweet in enumerate(tweets)
            ])
            
            prompt = f"""
            你是一个推文筛选助手。请根据以下规则筛选推文：
            
            规则: {prompt_rule.prompt}
            
            以下是需要筛选的推文：
            {tweets_text}
            
            请分析每条推文，判断它是否符合规则。
            对于每条推文，请以JSON格式返回：
            {{
                "tweet_id": "推文ID",
                "match": true/false,
                "reason": "匹配/不匹配的原因（简短说明）",
                "relevance_score": 0.0-1.0之间的相关度分数
            }}
            
            只返回符合规则的推文（match为true的）。
            请以JSON数组的格式返回结果，例如：
            [
                {{"tweet_id": "123", "match": true, "reason": "提到了白马47滑雪场", "relevance_score": 0.95}},
                {{"tweet_id": "456", "match": true, "reason": "讨论了白马地区的滑雪场信息", "relevance_score": 0.75}}
            ]
            
            如果没有符合的推文，返回空数组 []
            """
            
            response = self.gemini.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # 提取JSON部分
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # 解析JSON结果
            results = json.loads(result_text)
            
            # 构建返回结果
            matched_tweets = []
            tweet_dict = {str(tweet.tweet_id): tweet for tweet in tweets}
            
            for result in results:
                if result.get('match', False):
                    tweet_id = str(result['tweet_id'])
                    if tweet_id in tweet_dict:
                        matched_tweets.append((
                            tweet_dict[tweet_id],
                            result.get('reason', '符合筛选规则'),
                            float(result.get('relevance_score', 0.8))
                        ))
            
            logger.info(f"Filtered {len(matched_tweets)} tweets from {len(tweets)} using rule '{prompt_rule.name}'")
            return matched_tweets
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response text: {result_text}")
            return []
        except Exception as e:
            logger.error(f"Error filtering tweets with AI: {e}")
            return []
    
    def apply_rule_to_user_tweets(
        self, 
        user, 
        prompt_rule: AIPromptRule,
        date_filter: str = 'today'
    ) -> int:
        """
        对用户的推文应用AI规则并生成推荐
        
        Args:
            user: 用户对象
            prompt_rule: AI规则
            date_filter: 时间过滤 ('today', 'week', 'all')
            
        Returns:
            新增的推荐推文数量
        """
        try:
            # 获取用户监控的账户
            # 如果规则指定了target_accounts，只使用这些账户；否则使用所有账户
            target_accounts = prompt_rule.target_accounts.all()
            if target_accounts.exists():
                accounts = target_accounts.filter(user=user)
                logger.info(f"Applying rule '{prompt_rule.name}' to {accounts.count()} specified accounts")
            else:
                accounts = user.x_accounts.all()
                logger.info(f"Applying rule '{prompt_rule.name}' to all {accounts.count()} user accounts")
            
            if not accounts.exists():
                logger.info(f"No accounts found for rule '{prompt_rule.name}'")
                return 0
            
            # 获取这些账户的推文
            from datetime import timedelta
            from django.db.models import Q
            
            query = Tweet.objects.filter(x_account__in=accounts)
            
            # 应用时间过滤
            if date_filter == 'today':
                today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(posted_at__gte=today_start)
            elif date_filter == 'week':
                week_ago = timezone.now() - timedelta(days=7)
                query = query.filter(posted_at__gte=week_ago)
            
            tweets = list(query.order_by('-posted_at'))
            
            if not tweets:
                logger.info(f"No tweets found for user {user.email} with filter '{date_filter}'")
                return 0
            
            # 批量处理推文（每次最多50条）
            batch_size = 50
            total_recommended = 0
            
            for i in range(0, len(tweets), batch_size):
                batch = tweets[i:i + batch_size]
                matched_tweets = self.filter_tweets_by_prompt(batch, prompt_rule)
                
                # 创建推荐记录
                for tweet, reason, score in matched_tweets:
                    _, created = RecommendedTweet.objects.get_or_create(
                        user=user,
                        tweet=tweet,
                        prompt_rule=prompt_rule,
                        defaults={
                            'ai_reason': reason,
                            'relevance_score': score
                        }
                    )
                    if created:
                        total_recommended += 1
            
            # 更新规则的最后应用时间
            prompt_rule.last_applied = timezone.now()
            prompt_rule.save()
            
            logger.info(f"Applied rule '{prompt_rule.name}' to user {user.email}: {total_recommended} new recommendations")
            return total_recommended
            
        except Exception as e:
            logger.error(f"Error applying rule to user tweets: {e}")
            return 0