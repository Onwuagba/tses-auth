import redis
import random
from django.conf import settings

redis_client = redis.from_url(settings.REDIS_URL)

def generate_otp():
    """Generate 6-digit OTP"""
    return f"{random.randint(100000, 999999)}"

def store_otp(email, otp, ttl=300):
    """Store OTP in Redis with TTL (default 5 minutes)"""
    key = f"otp:{email}"
    redis_client.setex(key, ttl, otp)

def get_otp(email):
    """Get OTP from Redis"""
    key = f"otp:{email}"
    otp = redis_client.get(key)
    return otp.decode() if otp else None

def delete_otp(email):
    """Delete OTP from Redis"""
    key = f"otp:{email}"
    redis_client.delete(key)

def check_rate_limit_email(email, max_requests=3, window=600):
    """Check email rate limit (3 requests per 10 minutes)"""
    key = f"rate_limit:email:{email}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True, 0
    
    current = int(current)
    if current >= max_requests:
        ttl = redis_client.ttl(key)
        return False, ttl
    
    redis_client.incr(key)
    return True, 0

def check_rate_limit_ip(ip, max_requests=10, window=3600):
    """Check IP rate limit (10 requests per hour)"""
    key = f"rate_limit:ip:{ip}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True, 0
    
    current = int(current)
    if current >= max_requests:
        ttl = redis_client.ttl(key)
        return False, ttl
    
    redis_client.incr(key)
    return True, 0

def track_failed_attempt(email, max_attempts=5, window=900):
    """Track failed OTP attempts (5 attempts per 15 minutes)"""
    key = f"failed_attempts:{email}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return 1, False, 0
    
    current = int(current)
    new_count = redis_client.incr(key)
    
    if new_count >= max_attempts:
        ttl = redis_client.ttl(key)
        return new_count, True, ttl
    
    return new_count, False, 0

def is_locked(email):
    """Check if email is locked due to failed attempts"""
    key = f"failed_attempts:{email}"
    current = redis_client.get(key)
    
    if current is None:
        return False, 0
    
    current = int(current)
    if current >= 5:
        ttl = redis_client.ttl(key)
        return True, ttl
    
    return False, 0

def clear_failed_attempts(email):
    """Clear failed attempts after successful verification"""
    key = f"failed_attempts:{email}"
    redis_client.delete(key)