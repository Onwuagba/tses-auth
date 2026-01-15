from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class OTPRequestView(APIView):
    def post(self, request):
        return Response({"detail": "OTP request stub"}, status=status.HTTP_202_ACCEPTED)


class OTPVerifyView(APIView):
    def post(self, request):
        return Response({"detail": "OTP verify stub"})
