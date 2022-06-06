from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import UserAccounts
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=UserAccounts.objects.all())]
    )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = UserAccounts
        fields = '__all__'

    def create(self, validated_data):
        user = UserAccounts.objects.create_user(username=validated_data["username"], email=validated_data["email"],
                                                password=validated_data["password"])
        return user


class UserHighScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccounts
        fields = ["username", "score"]


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'
