from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from ..utils.redis_utils import (
    generate_otp, store_otp, get_otp, delete_otp,
    check_rate_limit_email, check_rate_limit_ip,
    track_failed_attempt, is_locked, clear_failed_attempts
)
from ..tasks.email_tasks import send_otp_email
from apps.audit.tasks.audit_tasks import write_audit_log

User = get_user_model()

class OTPService:
    @staticmethod
    def request_otp(email, ip_address, user_agent):
        """Handle OTP request with rate limiting"""
        email_allowed, email_retry_after = check_rate_limit_email(email)
        if not email_allowed:
            return {
                'success': False,
                'error': 'Too many OTP requests for this email',
                'retry_after': email_retry_after,
                'status_code': 429
            }
        
        ip_allowed, ip_retry_after = check_rate_limit_ip(ip_address)
        if not ip_allowed:
            return {
                'success': False,
                'error': 'Too many OTP requests from this IP',
                'retry_after': ip_retry_after,
                'status_code': 429
            }
        
        otp = generate_otp()
        store_otp(email, otp)
        
        send_otp_email.delay(email, otp)
        write_audit_log.delay('OTP_REQUESTED', email, ip_address, user_agent)
        
        return {
            'success': True,
            'message': 'OTP sent successfully',
            'expires_in': 300,
            'status_code': 202
        }
    
    @staticmethod
    def verify_otp(email, otp, ip_address, user_agent):
        """Handle OTP verification"""
        locked, unlock_eta = is_locked(email)
        if locked:
            write_audit_log.delay('OTP_LOCKED', email, ip_address, user_agent)
            return {
                'success': False,
                'error': 'Account temporarily locked due to too many failed attempts',
                'unlock_eta': unlock_eta,
                'status_code': 423
            }
        
        stored_otp = get_otp(email)
        if not stored_otp:
            write_audit_log.delay('OTP_FAILED', email, ip_address, user_agent, {'reason': 'expired'})
            return {
                'success': False,
                'error': 'OTP expired or not found',
                'status_code': 400
            }
        
        if stored_otp != otp:
            attempts, locked, unlock_eta = track_failed_attempt(email)
            if locked:
                write_audit_log.delay('OTP_LOCKED', email, ip_address, user_agent)
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to too many failed attempts',
                    'unlock_eta': unlock_eta,
                    'status_code': 423
                }
            else:
                write_audit_log.delay('OTP_FAILED', email, ip_address, user_agent, {'reason': 'invalid', 'attempts': attempts})
                return {
                    'success': False,
                    'error': 'Invalid OTP',
                    'status_code': 400
                }
        
        # OTP is valid - delete it and clear failed attempts
        delete_otp(email)
        clear_failed_attempts(email)
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email}
        )
        
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        write_audit_log.delay('OTP_VERIFIED', email, ip_address, user_agent)
        
        return {
            'success': True,
            'tokens': {
                'access': str(access),
                'refresh': str(refresh),
                'user_id': user.id,
                'email': user.email
            },
            'status_code': 200
        }