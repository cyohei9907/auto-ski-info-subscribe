"""
Flask API server for social media crawler service
"""
from flask import Flask, jsonify, request
from datetime import datetime
import signal
import sys
from config import Config
from scheduler import crawler_scheduler
from crawlers import TwitterCrawler, XiaohongshuCrawler
from ai_research import DeepResearcher
from utils.database import db_manager
from utils.logger import app_logger

# Initialize Flask app
app = Flask(__name__)


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    app_logger.info("Shutting down gracefully...")
    crawler_scheduler.stop()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Social Media Crawler API',
        'description': 'Periodic crawler for X (Twitter), Xiaohongshu, and other social platforms with AI Deep Research',
        'version': '1.0.0',
        'endpoints': {
            '/': 'This help message',
            '/health': 'Health check',
            '/api/research/latest': 'Get latest research results',
            '/api/research/platform/<platform>': 'Get research by platform',
            '/api/research/user/<username>': 'Get research by username',
            '/api/crawl/twitter': 'Trigger Twitter crawl (POST)',
            '/api/crawl/xiaohongshu': 'Trigger Xiaohongshu crawl (POST)',
            '/api/analyze': 'Analyze specific post (POST)'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'scheduler_running': crawler_scheduler.scheduler.running if crawler_scheduler.scheduler else False
    })


@app.route('/api/research/latest')
def get_latest_research():
    """Get latest research results"""
    try:
        limit = request.args.get('limit', 50, type=int)
        results = db_manager.get_research_results(limit=limit)
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
            if 'post_id' in result:
                result['post_id'] = str(result['post_id'])
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        app_logger.error(f"Error fetching research results: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/research/platform/<platform>')
def get_research_by_platform(platform):
    """Get research results by platform"""
    try:
        limit = request.args.get('limit', 50, type=int)
        results = db_manager.get_research_results(platform=platform, limit=limit)
        
        # Convert ObjectId to string
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
            if 'post_id' in result:
                result['post_id'] = str(result['post_id'])
        
        return jsonify({
            'success': True,
            'platform': platform,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        app_logger.error(f"Error fetching research for platform {platform}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/research/user/<username>')
def get_research_by_user(username):
    """Get research results by username"""
    try:
        limit = request.args.get('limit', 50, type=int)
        results = db_manager.get_research_results(username=username, limit=limit)
        
        # Convert ObjectId to string
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
            if 'post_id' in result:
                result['post_id'] = str(result['post_id'])
        
        return jsonify({
            'success': True,
            'username': username,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        app_logger.error(f"Error fetching research for user {username}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/crawl/twitter', methods=['POST'])
def trigger_twitter_crawl():
    """Manually trigger Twitter crawl"""
    try:
        app_logger.info("Manual Twitter crawl triggered")
        crawler_scheduler.crawl_twitter()
        return jsonify({
            'success': True,
            'message': 'Twitter crawl completed'
        })
    except Exception as e:
        app_logger.error(f"Manual Twitter crawl failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/crawl/xiaohongshu', methods=['POST'])
def trigger_xiaohongshu_crawl():
    """Manually trigger Xiaohongshu crawl"""
    try:
        app_logger.info("Manual Xiaohongshu crawl triggered")
        crawler_scheduler.crawl_xiaohongshu()
        return jsonify({
            'success': True,
            'message': 'Xiaohongshu crawl completed'
        })
    except Exception as e:
        app_logger.error(f"Manual Xiaohongshu crawl failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_post():
    """Analyze a specific post with AI"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: text'
            }), 400
        
        researcher = DeepResearcher()
        platform = data.get('platform', 'Unknown')
        
        result = researcher.analyze_post(data, platform)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        app_logger.error(f"Analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def main():
    """Main entry point"""
    try:
        # Validate configuration
        Config.validate()
        
        app_logger.info("Starting Social Media Crawler Service")
        
        # Start the scheduler
        crawler_scheduler.start()
        
        # Start Flask app
        app_logger.info(f"Starting API server on {Config.API_HOST}:{Config.API_PORT}")
        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=Config.FLASK_ENV == 'development'
        )
        
    except Exception as e:
        app_logger.error(f"Failed to start service: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
