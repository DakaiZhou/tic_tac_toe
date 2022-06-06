from rest_framework import generics
from game.serializers import GameSerializer
from accounts.serializers import UserHighScoreSerializer
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from game.functions import *


# endpoint to create a game, the creator is the player1
class CreateGame(generics.CreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(player1=self.request.user)


# endpoint to join a game, the player must have the game id to join the game. The joiner will be player2.
class JoinGame(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    # modified update() to satisfy different join game possibilities
    def update(self, request, *args, **kwargs):
        game = Game.objects.filter(id=self.kwargs["pk"], player2=None, finished=False)

        if game.exists():
            # the game creator join own game
            if game.first().player1 == self.request.user:
                content = {"Cannot join the game": "You cannot join your hosted games to play against yourself."}
                return Response(content, status=status.HTTP_409_CONFLICT)
            # correct behaviour
            else:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        # the game is found, but player2 is already existed
        elif Game.objects.filter(id=self.kwargs["pk"], finished=False).exists():
            content = {"Cannot join the game": "You cannot join this game, because this game is already started."}
            return Response(content, status=status.HTTP_409_CONFLICT)
        # the game is not found
        else:
            content = {"Cannot join the game": "This game is not existed."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        serializer.save(player2=self.request.user)


# endpoint to make a move. It check the move whether is possible or not. At the end of each move, it will also chek
# whether the player wins or not
class MakeMove(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # a move made on a game has not started/matched yet
        if Game.objects.filter(id=self.request.data["game_id"], player2=None, finished=False).exists():
            content={"bad request": "please until someone join your game"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        game = Game.objects.filter(Q(id=self.request.data["game_id"], player1=self.request.user.id, finished=False) |
                                   Q(id=self.request.data["game_id"], player2=self.request.user.id, finished=False))
        if game.exists():
            if self.request.data.get("row") and self.request.data.get("col"):
                move = [int(self.request.data["row"]), int(self.request.data["col"])]
            else:
                move = []
            move_flag = verify_move(move, self.request.data["game_id"], self.request.user.id)
            # valid move
            if move_flag[0]:
                win_flag = check_win(move_flag[1], self.request.data["game_id"], self.request.user.id)
                # the player wins
                if win_flag[0]:
                    content = {"result": "win", "move": move}
                    return Response(content, status=status.HTTP_200_OK)
                # the player does not win
                elif win_flag[1] == "tie":
                    content = {"result": "tie", "move": move}
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    content = {"result": "unresolved", "move": move}
                    return Response(content, status=status.HTTP_200_OK)
            # the move is invalid
            else:
                content = {"result": "unresolved", "move": "bad move: " + move_flag[1]}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        # the game is not found
        else:
            content = {"result": "unresolved", "move": "", "game": "game not found"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


# this endpoint  is open to everyone
class ListHighScores(generics.ListAPIView):
    serializer_class = UserHighScoreSerializer

    def get_queryset(self):
        queryset = UserAccounts.objects.all().order_by("-score")
        top_n = int(self.request.query_params.get("top_n"))
        if top_n is not None:
            queryset = queryset[: top_n]
        return queryset


