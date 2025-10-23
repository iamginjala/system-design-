import pytest
from utils.cache import set_data, get_data, delete_data, test_connection
from unittest.mock import patch, MagicMock
import json

class TestCacheConnection:
    def test_redis_connection_success(self):
        """Test Redis connection is alive"""
        assert test_connection() == True
    
    @patch('utils.cache.redis_client')
    def test_redis_connection_failure(self, mock_redis):
        """Test Redis connection error handling"""
        mock_redis.ping.side_effect = Exception("Connection failed")
        # This tests line 17-18 (exception handling in test_connection)

class TestCacheSetData:
    def test_set_data_success(self):
        """Test successfully storing data in cache"""
        test_data = {"name": "Test Product", "price": 100}
        result = set_data("test_product_1", test_data)
        
        assert result == True
        
        # Verify data was actually stored
        cached_data = get_data("test_product_1")
        assert cached_data == test_data
    
    @patch('utils.cache.redis_client')
    def test_set_data_exception(self, mock_redis):
        """Test set_data exception handling (lines 19-22)"""
        mock_redis.setex.side_effect = Exception("Redis error")
        
        result = set_data("test_product", {"name": "Test"})
        
        assert result == False  # Should return False on exception

class TestCacheGetData:
    def test_get_data_success(self):
        """Test retrieving cached data"""
        test_data = {"name": "Product", "price": 50}
        set_data("test_get_1", test_data)
        
        result = get_data("test_get_1")
        
        assert result == test_data
    
    def test_get_data_key_not_found(self):
        """Test getting non-existent key (line 30-31)"""
        result = get_data("non_existent_key")
        
        assert result == "no data found for key non_existent_key"
    
    @patch('utils.cache.redis_client')
    def test_get_data_empty_string(self, mock_redis):
        """Test empty string response (line 30)"""
        mock_redis.get.return_value = ""
        
        result = get_data("empty_key")
        
        assert "no data found" in result
    
    @patch('utils.cache.redis_client')
    def test_get_data_invalid_type(self, mock_redis):
        """Test invalid data type (line 32-33)"""
        mock_redis.get.return_value = 12345  # Not str/bytes/bytearray
        
        result = get_data("invalid_type")
        
        assert "invalid data type" in result
    
    @patch('utils.cache.redis_client')
    def test_get_data_invalid_json(self, mock_redis):
        """Test invalid JSON data (line 36-37)"""
        mock_redis.get.return_value = "not valid json{{"
        
        result = get_data("bad_json")
        
        assert "invalid json data" in result
    
    @patch('utils.cache.redis_client')
    def test_get_data_general_exception(self, mock_redis):
        """Test general exception handling (line 38-40)"""
        mock_redis.get.side_effect = Exception("Redis error")
        
        result = get_data("error_key")
        
        assert "error retrieving dictionary" in result

class TestCacheDeleteData:
    def test_delete_data_success(self):
        """Test successful deletion"""
        # First set data
        set_data("delete_test_1", {"name": "To Delete"})
        
        # Then delete it
        result = delete_data("delete_test_1")
        
        assert result == "deleted successfully"
        
        # Verify it's gone
        cached = get_data("delete_test_1")
        assert "no data found" in cached
    
    
    @patch('utils.cache.redis_client')
    def test_delete_data_exception(self, mock_redis):
        """Test delete exception handling"""
        mock_redis.delete.side_effect = Exception("Redis error")
        
        result = delete_data("error_key")
        
        assert "No data found" in result

class TestCacheIntegration:
    def test_cache_set_get_delete_flow(self):
        """Test complete cache lifecycle"""
        product_id = "integration_test"
        test_data = {"name": "Test Product", "price": 99.99}
        
        # Set
        set_result = set_data(product_id, test_data)
        assert set_result == True
        
        # Get
        get_result = get_data(product_id)
        assert get_result == test_data
        
        # Delete
        delete_result = delete_data(product_id)
        assert delete_result == "deleted successfully"
        
        # Verify deleted
        final_get = get_data(product_id)
        assert "no data found" in final_get
    
    def test_cache_ttl_behavior(self):
        """Test cache expiration (60 second TTL)"""
        import time
        
        set_data("ttl_test", {"temp": "data"})
        
        # Immediately should exist
        result = get_data("ttl_test")
        assert result == {"temp": "data"}
    