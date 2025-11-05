# Auto Ski Info Subscribe - Social Media Crawler Service

这是一个X爬虫服务器，定期爬取X（Twitter）、小红书等社交平台上的固定博主信息，通过AI Deep Research后将结果返回到接口。

This is a social media crawler service that periodically scrapes X (Twitter), Xiaohongshu (Little Red Book), and other social platforms for specific blogger information, processes the data through AI Deep Research, and returns results via API endpoints.

## Features

- 🔄 **Periodic Crawling**: Automatically scrapes social media platforms at configurable intervals
- 🐦 **Twitter/X Integration**: Uses Twitter API v2 for efficient data collection
- 📱 **Xiaohongshu Support**: Crawler for Little Red Book platform
- 🤖 **AI Deep Research**: Powered by OpenAI GPT-4 for comprehensive content analysis
- 🗄️ **MongoDB Storage**: Persistent storage for posts and research results
- 🚀 **RESTful API**: Easy-to-use API endpoints for accessing research results
- 📊 **Trend Analysis**: Generate trend reports from multiple posts
- ⏰ **Scheduler**: Background task scheduler with configurable intervals

## Architecture

```
┌─────────────────┐
│   Flask API     │  ← REST API endpoints
└────────┬────────┘
         │
┌────────▼────────┐
│   Scheduler     │  ← Periodic task execution
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Twitter│  │XiaoHS │  ← Platform crawlers
│Crawler│  │Crawler│
└───┬──┘  └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │ MongoDB │  ← Data storage
    └────┬────┘
         │
    ┌────▼────────┐
    │ AI Research │  ← OpenAI GPT-4
    └─────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key
- Twitter API credentials (Bearer Token or OAuth tokens)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/cyohei9907/auto-ski-info-subscribe.git
cd auto-ski-info-subscribe
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Required environment variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `TWITTER_BEARER_TOKEN`: Twitter API Bearer Token
   - `MONGODB_URI`: MongoDB connection string
   - `TWITTER_TARGET_USERS`: Comma-separated list of Twitter usernames to monitor
   - `XIAOHONGSHU_TARGET_USERS`: Comma-separated list of Xiaohongshu usernames

## Usage

### Start the service

```bash
python app.py
```

The service will:
1. Start the Flask API server (default: http://localhost:5000)
2. Initialize the scheduler for periodic crawling
3. Begin monitoring configured social media accounts

### API Endpoints

#### Get Service Info
```bash
GET /
```

#### Health Check
```bash
GET /health
```

#### Get Latest Research Results
```bash
GET /api/research/latest?limit=50
```

#### Get Research by Platform
```bash
GET /api/research/platform/Twitter?limit=50
GET /api/research/platform/Xiaohongshu?limit=50
```

#### Get Research by User
```bash
GET /api/research/user/username?limit=50
```

#### Manually Trigger Crawl
```bash
POST /api/crawl/twitter
POST /api/crawl/xiaohongshu
```

#### Analyze Custom Post
```bash
POST /api/analyze
Content-Type: application/json

{
  "text": "Your post content here",
  "platform": "Twitter"
}
```

### Example Response

```json
{
  "success": true,
  "count": 10,
  "results": [
    {
      "_id": "...",
      "post_id": "...",
      "platform": "Twitter",
      "analysis": "Detailed AI analysis...",
      "summary": "Brief summary...",
      "key_points": [
        "Point 1",
        "Point 2"
      ],
      "sentiment": "positive",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

## Configuration

Edit `.env` file to customize:

- **Crawling Interval**: `SCRAPE_INTERVAL_HOURS` (default: 6 hours)
- **API Port**: `API_PORT` (default: 5000)
- **OpenAI Model**: `OPENAI_MODEL` (default: gpt-4)
- **Target Users**: Add usernames to monitor
- **Enable/Disable Scheduler**: `ENABLE_SCHEDULER` (true/false)

## Project Structure

```
auto-ski-info-subscribe/
├── app.py                 # Flask API server
├── config.py              # Configuration management
├── scheduler.py           # Task scheduler
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py   # Base crawler class
│   ├── twitter_crawler.py     # Twitter implementation
│   └── xiaohongshu_crawler.py # Xiaohongshu implementation
├── ai_research/
│   ├── __init__.py
│   └── deep_research.py  # AI analysis module
└── utils/
    ├── __init__.py
    ├── logger.py         # Logging utilities
    └── database.py       # MongoDB management
```

## Development

### Add New Platform

1. Create new crawler in `crawlers/` extending `BaseCrawler`
2. Implement `authenticate()` and `get_user_posts()` methods
3. Add platform configuration in `config.py`
4. Register crawler in scheduler

### Run Tests

```bash
# Tests can be added here
pytest
```

## Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t ski-info-crawler .

# Run container
docker run -d \
  --env-file .env \
  -p 5000:5000 \
  --name crawler \
  ski-info-crawler
```

### Production Considerations

- Use production-grade WSGI server (Gunicorn, uWSGI)
- Set up reverse proxy (Nginx)
- Configure proper logging
- Implement rate limiting
- Set up monitoring and alerts
- Use environment-specific configurations

## Security

- Never commit `.env` file or API credentials
- Use environment variables for sensitive data
- Implement API authentication for production
- Follow platform API rate limits and terms of service
- Regularly update dependencies

## Troubleshooting

### MongoDB Connection Issues
- Verify MongoDB is running
- Check connection string in `.env`
- Ensure network access to MongoDB server

### Twitter API Errors
- Verify API credentials
- Check rate limits
- Ensure proper API access level

### OpenAI API Errors
- Verify API key is valid
- Check account balance/credits
- Monitor token usage

## License

MIT License

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs in `logs/` directory

## Roadmap

- [ ] Support for more social platforms (Instagram, TikTok, etc.)
- [ ] Advanced filtering and search capabilities
- [ ] Real-time notifications for new posts
- [ ] Web dashboard for visualization
- [ ] Sentiment trend analysis
- [ ] Multi-language support
- [ ] Export to various formats (CSV, Excel, PDF)

---

Built with ❤️ for social media intelligence and research