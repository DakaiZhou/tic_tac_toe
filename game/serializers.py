from rest_framework import serializers
from game.models import Game


class GameSerializer(serializers.ModelSerializer):
    player1 = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Game
        fields="__all__"
