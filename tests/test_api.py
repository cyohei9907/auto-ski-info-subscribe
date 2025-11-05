"""
Tests for Flask API endpoints
"""
import pytest
from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'service' in data
    assert 'endpoints' in data


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'


def test_analyze_endpoint_missing_data(client):
    """Test analyze endpoint with missing data"""
    response = client.post('/api/analyze', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_404_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
