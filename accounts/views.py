from rest_framework import generics
from accounts.models import UserAccounts
from accounts.serializers import UserSerializer, TokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


# endpoint to register, open to everyone
class UserRegistration(generics.CreateAPIView):
    queryset = UserAccounts.objects.all()
    serializer_class = UserSerializer


# endpoint to view user token. This view requires django default login for authentication instead of using token
class GetToken(generics.CreateAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def create(self, request, *args, **kwargs):
        token_lst = Token.objects.filter(user=self.request.user)
        if len(token_lst) == 1:
            token = token_lst[0]
            content = {"token": token.key}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {"token": "not found"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)


