# API Documentation

Social Media Crawler Service API Documentation

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. For production use, implement API key authentication or OAuth.

## Response Format

All responses are in JSON format with the following structure:

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## Endpoints

### 1. Root Endpoint

Get service information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "service": "Social Media Crawler API",
  "description": "Periodic crawler for X (Twitter), Xiaohongshu, and other social platforms with AI Deep Research",
  "version": "1.0.0",
  "endpoints": {
    "/": "This help message",
    "/health": "Health check",
    ...
  }
}
```

**Example:**
```bash
curl http://localhost:5000/
```

---

### 2. Health Check

Check if the service is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-05T05:30:00.000Z",
  "scheduler_running": true
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 3. Get Latest Research Results

Retrieve the most recent AI research results.

**Endpoint:** `GET /api/research/latest`

**Query Parameters:**
- `limit` (optional, default: 50): Number of results to return

**Response:**
```json
{
  "success": true,
  "count": 10,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "post_id": "507f191e810c19729de860ea",
      "platform": "Twitter",
      "analysis": "Detailed AI analysis...",
      "summary": "Brief summary...",
      "key_points": [
        "Key point 1",
        "Key point 2"
      ],
      "sentiment": "positive",
      "tokens_used": 1234,
      "created_at": "2024-11-05T05:30:00.000Z"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/research/latest?limit=20"
```

---

### 4. Get Research by Platform

Get research results filtered by social media platform.

**Endpoint:** `GET /api/research/platform/{platform}`

**Path Parameters:**
- `platform` (required): Platform name (Twitter, Xiaohongshu)

**Query Parameters:**
- `limit` (optional, default: 50): Number of results to return

**Response:**
```json
{
  "success": true,
  "platform": "Twitter",
  "count": 15,
  "results": [ ... ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/research/platform/Twitter?limit=30"
curl "http://localhost:5000/api/research/platform/Xiaohongshu"
```

---

### 5. Get Research by User

Get research results filtered by username.

**Endpoint:** `GET /api/research/user/{username}`

**Path Parameters:**
- `username` (required): Username to filter by

**Query Parameters:**
- `limit` (optional, default: 50): Number of results to return

**Response:**
```json
{
  "success": true,
  "username": "example_user",
  "count": 8,
  "results": [ ... ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/research/user/example_user?limit=10"
```

---

### 6. Trigger Twitter Crawl

Manually trigger a Twitter crawling job.

**Endpoint:** `POST /api/crawl/twitter`

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Twitter crawl completed"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/crawl/twitter
```

---

### 7. Trigger Xiaohongshu Crawl

Manually trigger a Xiaohongshu crawling job.

**Endpoint:** `POST /api/crawl/xiaohongshu`

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Xiaohongshu crawl completed"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/crawl/xiaohongshu
```

---

### 8. Analyze Custom Post

Analyze a custom post or text with AI Deep Research.

**Endpoint:** `POST /api/analyze`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Your post content here",
  "platform": "Twitter"
}
```

**Body Parameters:**
- `text` (required): Text content to analyze
- `platform` (optional): Platform name for context

**Response:**
```json
{
  "success": true,
  "analysis": {
    "post_id": null,
    "platform": "Twitter",
    "analysis": "This post discusses...",
    "summary": "Brief summary of the analysis",
    "key_points": [
      "Main topic: ...",
      "Sentiment: ...",
      "Target audience: ..."
    ],
    "sentiment": "positive",
    "tokens_used": 456
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Excited to share our latest ski resort review! The powder was amazing!",
    "platform": "Twitter"
  }'
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Missing required parameters |
| 404 | Not Found - Endpoint does not exist |
| 500 | Internal Server Error - Server-side error |

## Rate Limiting

Currently, there are no rate limits implemented. For production use, consider implementing rate limiting to prevent abuse.

## Data Models

### Post Object
```json
{
  "id": "tweet_id",
  "text": "Post content",
  "created_at": "2024-11-05T05:30:00.000Z",
  "language": "en",
  "metrics": {
    "likes": 100,
    "retweets": 50,
    "replies": 25
  }
}
```

### Research Result Object
```json
{
  "_id": "mongodb_id",
  "post_id": "related_post_id",
  "platform": "Twitter",
  "analysis": "Full AI analysis text",
  "summary": "Brief summary",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "sentiment": "positive|negative|neutral",
  "tokens_used": 1234,
  "created_at": "2024-11-05T05:30:00.000Z"
}
```

## Best Practices

1. **Pagination**: Use the `limit` parameter to control the number of results
2. **Error Handling**: Always check the `success` field in responses
3. **Scheduled Jobs**: Use manual crawl triggers sparingly; let the scheduler handle periodic tasks
4. **Text Analysis**: Keep text under 4000 characters for optimal AI analysis
5. **Caching**: Consider caching frequently accessed results

## Webhook Integration (Future)

Future versions may include webhook support for real-time notifications:

```json
{
  "webhook_url": "https://your-server.com/webhook",
  "events": ["new_post", "analysis_complete"]
}
```

## SDK Examples

### Python
```python
import requests

# Get latest research
response = requests.get('http://localhost:5000/api/research/latest')
data = response.json()

# Analyze custom text
payload = {
    "text": "Your text here",
    "platform": "Twitter"
}
response = requests.post(
    'http://localhost:5000/api/analyze',
    json=payload
)
result = response.json()
```

### JavaScript
```javascript
// Get latest research
fetch('http://localhost:5000/api/research/latest')
  .then(response => response.json())
  .then(data => console.log(data));

// Analyze custom text
fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Your text here',
    platform: 'Twitter'
  })
})
  .then(response => response.json())
  .then(result => console.log(result));
```

### cURL
```bash
# Set base URL
BASE_URL="http://localhost:5000"

# Get health status
curl "$BASE_URL/health"

# Get latest research with limit
curl "$BASE_URL/api/research/latest?limit=10"

# Trigger Twitter crawl
curl -X POST "$BASE_URL/api/crawl/twitter"

# Analyze text
curl -X POST "$BASE_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text", "platform": "Twitter"}'
```

## Support

For API issues or questions:
- Check service logs: `logs/app.log`
- Review health endpoint: `GET /health`
- Open an issue on GitHub

---

Last updated: 2024-11-05
