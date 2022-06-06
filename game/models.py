from django.db import models
from accounts.models import UserAccounts
from django.core.exceptions import ValidationError
import json


def moves_default():
    return json.dumps({})


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    player1 = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, related_name="player2", null=True)
    last_play = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, related_name="last_play", null=True)
    moves = models.JSONField(default=moves_default)
    finished = models.BooleanField(default=False)
    winner = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, default=None, related_name="winner", null=True)
    password = models.CharField(max_length=16, default="000000")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # check that player1 and player2 should not be the same
        if self.player1 == self.player2:
            raise ValidationError('Player1 and player2 are the same')
        else:
            super(Game, self).save()
