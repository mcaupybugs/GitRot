"""
API Helper utilities for GitRot FastAPI application
Azure best practices implementation for monitoring and logging
"""

import logging
import time
import functools
from typing import Callable, Any
from fastapi import Request, HTTPException
import json

# Azure best practice: Configure structured logging
logger = logging.getLogger(__name__)

class APIMetrics:
    """Azure best practice: Simple metrics tracking for monitoring"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.generation_count = 0
        self.total_response_time = 0.0
        self.start_time = time.time()
    
    def increment_requests(self):
        self.request_count += 1
    
    def increment_errors(self):
        self.error_count += 1
    
    def increment_generations(self):
        self.generation_count += 1
    
    def add_response_time(self, response_time: float):
        self.total_response_time += response_time
    
    def get_metrics(self) -> dict:
        uptime = time.time() - self.start_time
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "total_generations": self.generation_count,
            "average_response_time": avg_response_time,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
        }

# Global metrics instance
metrics = APIMetrics()

def log_request_metrics(func: Callable) -> Callable:
    """
    Azure best practice: Decorator for logging request metrics
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        metrics.increment_requests()
        
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            metrics.add_response_time(response_time)
            
            logger.info(f"Request completed: {func.__name__} - {response_time:.3f}s")
            return result
            
        except Exception as e:
            metrics.increment_errors()
            response_time = time.time() - start_time
            metrics.add_response_time(response_time)
            
            logger.error(f"Request failed: {func.__name__} - {response_time:.3f}s - {str(e)}")
            raise
    
    return wrapper

def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL format
    Azure best practice: Input validation
    """
    if not url:
        return False
    
    # Basic GitHub URL validation
    valid_patterns = [
        "https://github.com/",
        "http://github.com/",
        "github.com/"
    ]
    
    url_lower = url.lower().strip()
    if not any(pattern in url_lower for pattern in valid_patterns):
        return False
    
    # Check for proper format: github.com/user/repo
    try:
        if "github.com/" in url_lower:
            path_part = url_lower.split("github.com/")[-1]
            path_segments = path_part.strip("/").split("/")
            return len(path_segments) >= 2 and all(segment for segment in path_segments[:2])
        return False
    except Exception:
        return False

def sanitize_repo_name(repo_url: str) -> str:
    """
    Extract and sanitize repository name from URL
    Azure best practice: Data sanitization
    """
    try:
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1]
        
        # Remove common suffixes
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # Sanitize for file system safety
        import re
        repo_name = re.sub(r'[^\w\-_\.]', '_', repo_name)
        
        return repo_name[:50]  # Limit length
    except Exception:
        return "unknown_repo"

def format_error_response(error: Exception, request_id: str = None) -> dict:
    """
    Azure best practice: Structured error response formatting
    """
    error_response = {
        "success": False,
        "error_message": str(error),
        "error_type": type(error).__name__,
        "timestamp": time.time()
    }
    
    if request_id:
        error_response["request_id"] = request_id
    
    return error_response

def log_generation_attempt(repo_url: str, method: str, user_agent: str = None):
    """
    Azure best practice: Log generation attempts for monitoring
    """
    metrics.increment_generations()
    
    log_data = {
        "event": "readme_generation_attempt",
        "repo_url": sanitize_repo_name(repo_url),  # Don't log full URL for privacy
        "generation_method": method,
        "timestamp": time.time()
    }
    
    if user_agent:
        log_data["user_agent"] = user_agent[:100]  # Truncate for storage
    
    logger.info(f"Generation attempt: {json.dumps(log_data)}")

def get_client_info(request: Request) -> dict:
    """
    Extract client information for logging and analytics
    Azure best practice: Request context tracking
    """
    return {
        "user_agent": request.headers.get("user-agent", "unknown")[:100],
        "client_host": request.client.host if request.client else "unknown",
        "content_type": request.headers.get("content-type", "unknown"),
        "timestamp": time.time()
    }

class RateLimiter:
    """
    Simple in-memory rate limiter for Azure App Service
    Azure best practice: Basic rate limiting for protection
    """
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items()
            if current_time - v['first_request'] < self.window_seconds
        }
        
        if client_id not in self.requests:
            self.requests[client_id] = {
                'count': 1,
                'first_request': current_time
            }
            return True
        
        client_data = self.requests[client_id]
        if current_time - client_data['first_request'] >= self.window_seconds:
            # Reset window
            self.requests[client_id] = {
                'count': 1,
                'first_request': current_time
            }
            return True
        
        if client_data['count'] >= self.max_requests:
            return False
        
        client_data['count'] += 1
        return True

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=50, window_minutes=60)

def check_rate_limit(request: Request) -> bool:
    """
    Check if request should be rate limited
    Azure best practice: Protect against abuse
    """
    client_id = request.client.host if request.client else "unknown"
    return rate_limiter.is_allowed(client_id)

def create_download_filename(repo_url: str) -> str:
    """
    Create a safe filename for README download
    Azure best practice: Safe file naming
    """
    repo_name = sanitize_repo_name(repo_url)
    timestamp = int(time.time())
    return f"README_{repo_name}_{timestamp}.md"
