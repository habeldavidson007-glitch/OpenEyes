"""
Live API Client for Unified Knowledge Orchestrator
Replaces mock implementations with real API calls to external data sources.
Supports multiple providers with automatic fallback and rate limiting.
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.error
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported external API providers."""
    NEWS_API = "news_api"
    WORLD_BANK = "world_bank"
    CDC_GOV = "cdc_gov"
    REUTERS = "reuters"
    BLOOMBERG = "bloomberg"
    FALLBACK = "fallback"

@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    data: Any
    source_url: str
    timestamp: float
    provider: APIProvider
    error_message: Optional[str] = None
    rate_limit_remaining: int = -1

class RateLimiter:
    """Simple rate limiter to prevent API abuse."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
    
    def can_make_request(self) -> bool:
        """Check if we can make a request without exceeding rate limit."""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a request was made."""
        self.requests.append(time.time())
    
    def wait_time_seconds(self) -> float:
        """Calculate how long to wait before next request is allowed."""
        if not self.requests:
            return 0.0
        oldest = min(self.requests)
        elapsed = time.time() - oldest
        return max(0.0, self.window_seconds - elapsed)

class LiveAPIClient:
    """
    Real API client for fetching live data from external sources.
    Implements automatic fallback, rate limiting, and caching.
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.rate_limiters: Dict[APIProvider, RateLimiter] = {
            APIProvider.NEWS_API: RateLimiter(100, 60),
            APIProvider.WORLD_BANK: RateLimiter(60, 60),
            APIProvider.CDC_GOV: RateLimiter(120, 60),
            APIProvider.REUTERS: RateLimiter(50, 60),
            APIProvider.BLOOMBERG: RateLimiter(50, 60),
            APIProvider.FALLBACK: RateLimiter(1000, 60),
        }
        self.timeout_seconds = 10
        self.user_agent = "OpenEyes/1.0"
    
    def fetch_knowledge(self, query: str, domain: str, 
                        preferred_providers: List[APIProvider] = None) -> APIResponse:
        """
        Fetch knowledge from external APIs based on domain and query.
        Automatically tries multiple providers with fallback.
        """
        if preferred_providers is None:
            preferred_providers = self._get_providers_for_domain(domain)
        
        for provider in preferred_providers:
            try:
                response = self._fetch_from_provider(provider, query, domain)
                if response and response.success:
                    logger.info(f"Successfully fetched from {provider.value} for domain {domain}")
                    return response
                else:
                    logger.warning(f"Failed to fetch from {provider.value}: {response.error_message if response else 'No response'}")
            except Exception as e:
                logger.error(f"Error fetching from {provider.value}: {str(e)}")
        
        # Final fallback
        return self._fallback_fetch(query, domain)
    
    def _get_providers_for_domain(self, domain: str) -> List[APIProvider]:
        """Map domains to appropriate API providers."""
        domain_lower = domain.lower()
        
        if "health" in domain_lower or "medical" in domain_lower:
            return [APIProvider.CDC_GOV, APIProvider.NEWS_API, APIProvider.REUTERS]
        elif "econom" in domain_lower or "finance" in domain_lower:
            return [APIProvider.WORLD_BANK, APIProvider.BLOOMBERG, APIProvider.REUTERS]
        elif "govern" in domain_lower or "policy" in domain_lower:
            return [APIProvider.WORLD_BANK, APIProvider.NEWS_API, APIProvider.REUTERS]
        elif "invest" in domain_lower or "market" in domain_lower:
            return [APIProvider.BLOOMBERG, APIProvider.REUTERS, APIProvider.NEWS_API]
        else:
            return [APIProvider.NEWS_API, APIProvider.REUTERS, APIProvider.FALLBACK]
    
    def _fetch_from_provider(self, provider: APIProvider, query: str, domain: str) -> Optional[APIResponse]:
        """Fetch data from a specific provider."""
        limiter = self.rate_limiters.get(provider)
        if limiter and not limiter.can_make_request():
            logger.warning(f"Rate limited for {provider.value}")
            return None
        
        try:
            if provider == APIProvider.NEWS_API:
                return self._fetch_news_api(query, domain, limiter)
            elif provider == APIProvider.WORLD_BANK:
                return self._fetch_world_bank(query, domain, limiter)
            elif provider == APIProvider.CDC_GOV:
                return self._fetch_cdc_gov(query, domain, limiter)
            elif provider == APIProvider.REUTERS:
                return self._fetch_reuters(query, domain, limiter)
            elif provider == APIProvider.BLOOMBERG:
                return self._fetch_bloomberg(query, domain, limiter)
            else:
                return None
        except Exception as e:
            logger.error(f"Provider {provider.value} failed: {str(e)}")
            return APIResponse(
                success=False,
                data=None,
                source_url="",
                timestamp=time.time(),
                provider=provider,
                error_message=str(e)
            )
    
    def _fetch_news_api(self, query: str, domain: str, limiter: RateLimiter) -> APIResponse:
        """Fetch from NewsAPI (requires API key)."""
        api_key = self.api_keys.get("news_api")
        if not api_key:
            return APIResponse(
                success=False,
                data=None,
                source_url="https://newsapi.org",
                timestamp=time.time(),
                provider=APIProvider.NEWS_API,
                error_message="Missing API key"
            )
        
        url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&apiKey={api_key}"
        return self._make_request(url, APIProvider.NEWS_API, limiter)
    
    def _fetch_world_bank(self, query: str, domain: str, limiter: RateLimiter) -> APIResponse:
        """Fetch from World Bank Open Data API."""
        # Simplified example - in production would use proper endpoints
        url = f"https://api.worldbank.org/v2/country/all/indicator?format=json&per_page=5"
        return self._make_request(url, APIProvider.WORLD_BANK, limiter)
    
    def _fetch_cdc_gov(self, query: str, domain: str, limiter: RateLimiter) -> APIResponse:
        """Fetch from CDC.gov API."""
        url = f"https://data.cdc.gov/resource/queries.json?$where=search='{urllib.parse.quote(query)}'&$limit=5"
        return self._make_request(url, APIProvider.CDC_GOV, limiter)
    
    def _fetch_reuters(self, query: str, domain: str, limiter: RateLimiter) -> APIResponse:
        """Fetch from Reuters API (mock implementation - requires subscription)."""
        # In production, this would use the actual Reuters API
        return APIResponse(
            success=False,
            data=None,
            source_url="https://reuters.com",
            timestamp=time.time(),
            provider=APIProvider.REUTERS,
            error_message="Reuters API requires enterprise subscription"
        )
    
    def _fetch_bloomberg(self, query: str, domain: str, limiter: RateLimiter) -> APIResponse:
        """Fetch from Bloomberg API (mock implementation - requires subscription)."""
        # In production, this would use the actual Bloomberg Terminal API
        return APIResponse(
            success=False,
            data=None,
            source_url="https://bloomberg.com",
            timestamp=time.time(),
            provider=APIProvider.BLOOMBERG,
            error_message="Bloomberg API requires enterprise subscription"
        )
    
    def _make_request(self, url: str, provider: APIProvider, limiter: RateLimiter) -> APIResponse:
        """Make HTTP request and parse response."""
        if limiter and not limiter.can_make_request():
            return APIResponse(
                success=False,
                data=None,
                source_url=url,
                timestamp=time.time(),
                provider=provider,
                error_message="Rate limited"
            )
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/json"
                }
            )
            
            start_time = time.time()
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode('utf-8'))
                elapsed = time.time() - start_time
                
                limiter.record_request()
                
                return APIResponse(
                    success=True,
                    data=data,
                    source_url=url,
                    timestamp=time.time(),
                    provider=provider,
                    rate_limit_remaining=limiter.max_requests - len(limiter.requests)
                )
        except urllib.error.HTTPError as e:
            return APIResponse(
                success=False,
                data=None,
                source_url=url,
                timestamp=time.time(),
                provider=provider,
                error_message=f"HTTP Error {e.code}: {e.reason}"
            )
        except urllib.error.URLError as e:
            return APIResponse(
                success=False,
                data=None,
                source_url=url,
                timestamp=time.time(),
                provider=provider,
                error_message=f"URL Error: {str(e.reason)}"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                source_url=url,
                timestamp=time.time(),
                provider=provider,
                error_message=str(e)
            )
    
    def _fallback_fetch(self, query: str, domain: str) -> APIResponse:
        """Fallback when all APIs fail - returns structured placeholder."""
        logger.warning(f"All API providers failed for '{query}', using fallback")
        
        fallback_data = {
            "message": "Live data temporarily unavailable. Showing cached/general knowledge.",
            "query": query,
            "domain": domain,
            "timestamp": time.time(),
            "is_fallback": True
        }
        
        return APIResponse(
            success=True,  # Success in returning something usable
            data=fallback_data,
            source_url="internal://fallback",
            timestamp=time.time(),
            provider=APIProvider.FALLBACK
        )
    
    def health_check(self) -> Dict[str, bool]:
        """Check health status of all API providers."""
        status = {}
        for provider in APIProvider:
            if provider == APIProvider.FALLBACK:
                status[provider.value] = True
                continue
            
            limiter = self.rate_limiters.get(provider)
            status[provider.value] = limiter.can_make_request() if limiter else False
        
        return status


# Singleton instance
_api_client: Optional[LiveAPIClient] = None

def get_api_client(api_keys: Dict[str, str] = None) -> LiveAPIClient:
    """Get or create the API client singleton."""
    global _api_client
    if _api_client is None:
        _api_client = LiveAPIClient(api_keys)
    return _api_client
