from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import OTPRequestSerializer, OTPVerifySerializer, TokenResponseSerializer
from .services.otp_service import OTPService

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class OTPRequestView(APIView):
    @extend_schema(
        summary="Request OTP",
        description="Request a 6-digit OTP to be sent to the provided email address",
        request=OTPRequestSerializer,
        responses={
            202: OpenApiResponse(description="OTP sent successfully"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        }
    )
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        result = OTPService.request_otp(email, ip_address, user_agent)
        
        if not result['success']:
            response_data = {'error': result['error']}
            if 'retry_after' in result:
                response_data['retry_after'] = result['retry_after']
            return Response(response_data, status=result['status_code'])
        
        return Response({
            'message': result['message'],
            'expires_in': result['expires_in']
        }, status=result['status_code'])

class OTPVerifyView(APIView):
    @extend_schema(
        summary="Verify OTP",
        description="Verify OTP and receive JWT tokens",
        request=OTPVerifySerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Invalid OTP or expired"),
            423: OpenApiResponse(description="Account locked"),
        }
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        result = OTPService.verify_otp(email, otp, ip_address, user_agent)
        
        if not result['success']:
            response_data = {'error': result['error']}
            if 'unlock_eta' in result:
                response_data['unlock_eta'] = result['unlock_eta']
            return Response(response_data, status=result['status_code'])
        
        return Response(result['tokens'], status=result['status_code'])
