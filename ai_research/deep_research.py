"""
AI Deep Research implementation using OpenAI
"""
from typing import Dict, List, Optional
import openai
from config import Config
from utils.logger import ai_logger


class DeepResearcher:
    """AI-powered deep research analyzer for social media posts"""
    
    def __init__(self):
        """Initialize the deep researcher"""
        self.logger = ai_logger
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
    
    def analyze_post(self, post: Dict, platform: str = None) -> Dict:
        """
        Perform deep analysis on a single post
        
        Args:
            post: Post data dictionary
            platform: Platform name (optional)
            
        Returns:
            Analysis results dictionary
        """
        try:
            post_text = post.get('text', '')
            
            if not post_text:
                self.logger.warning("Empty post text, skipping analysis")
                return {'error': 'Empty post text'}
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(post_text, platform)
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst specializing in social media content analysis, "
                                 "trend identification, and deep research. Provide detailed, insightful analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            result = {
                'post_id': post.get('id'),
                'platform': platform,
                'analysis': analysis_text,
                'summary': self._extract_summary(analysis_text),
                'key_points': self._extract_key_points(analysis_text),
                'sentiment': self._analyze_sentiment(post_text),
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
            self.logger.info(f"Successfully analyzed post {post.get('id')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze post: {e}")
            return {'error': str(e)}
    
    def analyze_multiple_posts(self, posts: List[Dict], platform: str = None) -> List[Dict]:
        """
        Analyze multiple posts
        
        Args:
            posts: List of post dictionaries
            platform: Platform name (optional)
            
        Returns:
            List of analysis results
        """
        results = []
        
        for post in posts:
            result = self.analyze_post(post, platform)
            results.append(result)
        
        return results
    
    def generate_trend_report(self, posts: List[Dict], platform: str = None) -> Dict:
        """
        Generate a comprehensive trend report from multiple posts
        
        Args:
            posts: List of post dictionaries
            platform: Platform name (optional)
            
        Returns:
            Trend report dictionary
        """
        try:
            if not posts:
                return {'error': 'No posts to analyze'}
            
            # Combine post texts
            combined_text = "\n\n---\n\n".join([
                f"Post {i+1}: {post.get('text', '')}" 
                for i, post in enumerate(posts[:10])  # Limit to 10 posts to avoid token limits
            ])
            
            # Create trend analysis prompt
            prompt = f"""Analyze the following social media posts and provide a comprehensive trend report.
            
Platform: {platform or 'Unknown'}
Number of posts: {len(posts)}

Posts:
{combined_text}

Please provide:
1. Overall themes and trends
2. Key topics and discussions
3. Sentiment analysis across posts
4. Notable patterns or insights
5. Recommendations for content strategy
"""
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trend analyst specializing in social media analytics "
                                 "and content strategy. Provide actionable insights and comprehensive reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            report_text = response.choices[0].message.content
            
            result = {
                'platform': platform,
                'posts_analyzed': len(posts),
                'report': report_text,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
            self.logger.info(f"Generated trend report for {len(posts)} posts")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate trend report: {e}")
            return {'error': str(e)}
    
    def _create_analysis_prompt(self, post_text: str, platform: str = None) -> str:
        """
        Create analysis prompt for a post
        
        Args:
            post_text: Text content of the post
            platform: Platform name
            
        Returns:
            Formatted prompt string
        """
        platform_context = f" from {platform}" if platform else ""
        
        return f"""Analyze the following social media post{platform_context}:

"{post_text}"

Please provide:
1. Main topic and subject matter
2. Key messages and takeaways
3. Sentiment and tone
4. Target audience
5. Potential impact and relevance
6. Any notable trends or patterns
7. Recommendations or insights

Provide a detailed but concise analysis."""
    
    def _extract_summary(self, analysis_text: str) -> str:
        """
        Extract a brief summary from analysis text
        
        Args:
            analysis_text: Full analysis text
            
        Returns:
            Summary string
        """
        # Simple extraction - take first paragraph or first 200 chars
        lines = analysis_text.split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) > 50:
                return line.strip()[:200] + '...' if len(line.strip()) > 200 else line.strip()
        
        return analysis_text[:200] + '...' if len(analysis_text) > 200 else analysis_text
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """
        Extract key points from analysis text
        
        Args:
            analysis_text: Full analysis text
            
        Returns:
            List of key points
        """
        key_points = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            # Look for numbered or bulleted points
            if line.strip() and (
                line.strip()[0].isdigit() or 
                line.strip().startswith('-') or 
                line.strip().startswith('•')
            ):
                # Clean up the point
                point = line.strip().lstrip('0123456789.-•)').strip()
                if len(point) > 10:
                    key_points.append(point)
        
        return key_points[:5]  # Return top 5 key points
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Basic sentiment analysis using simple heuristics
        
        Note: This is a simplified implementation. For production use, consider:
        - Using TextBlob or VADER sentiment analysis libraries
        - Leveraging OpenAI's sentiment capabilities
        - Training a domain-specific sentiment model
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment label (positive, negative, or neutral)
        """
        # Expanded word lists including ski/outdoor activity context
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 
                         'fantastic', 'love', 'best', 'happy', 'awesome', 'perfect',
                         'beautiful', 'exciting', 'incredible', 'enjoy', 'fun']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor',
                         'disappointing', 'sad', 'angry', 'frustrated', 'dangerous',
                         'closed', 'crowded', 'expensive', 'difficult']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
