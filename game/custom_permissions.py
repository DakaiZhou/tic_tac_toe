from rest_framework import permissions


class IsPlayerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow players of this game to edit it. Other users can view the game
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the players of the game, or player that are invited
        if obj.player2:
            return obj.player1 == request.user or obj.player2 == request.user
        else:
            return obj.password == request.password
