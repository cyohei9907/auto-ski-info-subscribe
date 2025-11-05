# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-05

### Added
- Initial release of Social Media Crawler Service
- Twitter/X crawler with API v2 support
- Xiaohongshu crawler with basic implementation
- AI Deep Research integration using OpenAI GPT-4
- MongoDB database for persistent storage
- RESTful API with Flask
- Background scheduler for periodic crawling
- Docker support with docker-compose
- Comprehensive documentation
- Test suite with pytest
- Configuration management with .env files
- Logging system with file and console handlers

### Features
- Periodic crawling of configured social media accounts
- AI-powered content analysis and sentiment detection
- Trend report generation
- API endpoints for accessing research results
- Filtering by platform and username
- Manual crawl triggering
- Health check endpoint
- Custom post analysis endpoint

### Technical
- Python 3.8+ compatibility
- Modular architecture with base crawler class
- Error handling and logging
- Rate limiting support
- Docker containerization
- MongoDB aggregation for complex queries
