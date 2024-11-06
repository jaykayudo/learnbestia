from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import HttpRequest
from rest_framework.response import Response

from .serializers import (
    ChangePasswordSerializer,
    EmailLoginSerializer,
    EmailRegisterSerializer,
    EthereumLoginSerializer,
    EthereumRegisterSerializer,
    ForgotPasswordSerializer,
    GoogleLoginSerializer,
    GoogleRegisterSerializer,
    PolkadotLoginSerializer,
    PolkadotRegisterSerializer,
    ResetPasswordSerializer,
)

# Create your views here.

# register views


class GoogleRegisterAPIView(GenericAPIView):
    serializer_class = GoogleRegisterSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class EmailRegisterAPIView(GenericAPIView):
    serializer_class = EmailRegisterSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class EthereumRegisterAPIView(GenericAPIView):
    serializer_class = EthereumRegisterSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class PolkadotRegisterAPIViw(GenericAPIView):
    serializer_class = PolkadotRegisterSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


# login views


class GoogleLoginAPIView(GenericAPIView):
    serializer_class = GoogleLoginSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class EmailLoginAPIView(GenericAPIView):
    serializer_class = EmailLoginSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class EthereumLoginAPIView(GenericAPIView):
    serializer_class = EthereumLoginSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class PolkadotLoginAPIViw(GenericAPIView):
    serializer_class = PolkadotLoginSerializer

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


# password related


class ChangePasswordAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request: HttpRequest):
        user = request.user
        request_data = {**request.data, "user": user.id_str}
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordAPIView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request: HttpRequest):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request: HttpRequest):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
