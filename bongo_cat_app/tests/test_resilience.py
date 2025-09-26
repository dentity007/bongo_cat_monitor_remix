#!/usr/bin/env python3
"""
Tests for the resilience module - circuit breaker and caching functionality
"""

import pytest
import time
from unittest.mock import Mock, patch
from resilience import TTLCache, CircuitBreaker, resilient_json


class TestTTLCache:
    """Test the TTL cache functionality"""

    def test_cache_basic_operations(self):
        """Test basic cache get/put operations"""
        cache = TTLCache()

        # Test setting and getting
        cache.put("key1", "value1")
        hit, value, stale = cache.get("key1", ttl_s=60)
        assert hit is True
        assert value == "value1"
        assert stale is False

        # Test getting non-existent key
        hit, value, stale = cache.get("nonexistent", ttl_s=60)
        assert hit is False
        assert value is None

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL"""
        cache = TTLCache()

        cache.put("key1", "value1")
        hit, value, stale = cache.get("key1", ttl_s=60)
        assert hit is True and not stale

        # Wait for expiration (set very short TTL)
        time.sleep(0.1)
        hit, value, stale = cache.get("key1", ttl_s=0)  # TTL of 0 means always expired
        assert hit is True and stale is True

    def test_cache_cleanup(self):
        """Test that expired entries are marked as stale but not automatically cleaned"""
        cache = TTLCache()

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        # Wait for expiration
        time.sleep(0.1)

        # Access should return stale data
        hit, value, stale = cache.get("key1", ttl_s=0)
        assert hit is True and stale is True
        assert value == "value1"

        # Cache still contains the entries (no automatic cleanup)
        assert len(cache._store) == 2


class TestCircuitBreaker:
    """Test the circuit breaker functionality"""

    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in closed state"""
        import os
        # Clear any existing state for this test
        cb_state_path = os.path.join(os.path.dirname(__file__), "..", "cache", "cb_state.json")
        if os.path.exists(cb_state_path):
            os.remove(cb_state_path)
        
        breaker = CircuitBreaker("test_initial", fail_threshold=2, open_window_s=1)
        assert breaker.state == "CLOSED"
        assert breaker.fail_count == 0
        assert breaker.allow() == True

    def test_circuit_breaker_failure_recording(self):
        """Test circuit breaker records failures correctly"""
        import os
        # Clear any existing state for this test
        cb_state_path = os.path.join(os.path.dirname(__file__), "..", "cache", "cb_state.json")
        if os.path.exists(cb_state_path):
            os.remove(cb_state_path)
        
        breaker = CircuitBreaker("test_failure", fail_threshold=2, open_window_s=1)

        # Record failures
        breaker.record_failure()
        assert breaker.fail_count == 1
        assert breaker.state == "CLOSED"

        breaker.record_failure()
        assert breaker.fail_count == 2
        assert breaker.state == "OPEN"

    def test_circuit_breaker_success_recording(self):
        """Test circuit breaker records success correctly"""
        breaker = CircuitBreaker("test", fail_threshold=2, open_window_s=1)

        # Put in open state
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == "OPEN"

        # Record success should close it
        breaker.record_success()
        assert breaker.state == "CLOSED"
        assert breaker.fail_count == 0

    def test_circuit_breaker_recovery_timeout(self):
        """Test circuit breaker recovery after timeout"""
        breaker = CircuitBreaker("test", fail_threshold=1, open_window_s=1)

        # Open the circuit
        breaker.record_failure()
        assert breaker.state == "OPEN"
        assert breaker.allow() == False

        # Wait for recovery timeout
        time.sleep(1.1)

        # Should allow probe call now
        assert breaker.allow() == True
        assert breaker.state == "HALF_OPEN"


class TestResilientAPICall:
    """Test the resilient API call functionality"""

    def test_resilient_json_with_fallback(self):
        """Test that resilient_json uses fallback when network fails"""

        def local_fallback():
            return {"data": "fallback"}

        # Test with a URL that will fail and a unique cache key
        import time
        unique_key = f"test_key_{time.time()}"

        result, meta = resilient_json(
            name="test_api",
            url="http://nonexistent-domain-that-will-fail.invalid",
            cache_key=unique_key,
            ttl_s=60,
            local_fallback_fn=local_fallback,
            non_blocking=False
        )

        # Should return fallback data
        assert result == {"data": "fallback"}
        assert meta["source"] == "fallback"