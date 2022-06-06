from game.models import Game
from accounts.models import UserAccounts
import json


def verify_move(move, game_id, player_id):
    """
    verity each move made.
    :param move: a two element list, i.e. [1, 2]
    :param game_id: the id of a game which you are playing
    :param player_id: the id of the player who made this move
    :return:
    """
    # no move made
    if not move:
        return False, "no move"
    else:
        # the move out of the board
        if move[0] < 1 or move[0] > 3 or move[1] < 1 or move[1] > 3:
            return False, "out of board"

    game_lst = Game.objects.filter(id=game_id)
    num_game = len(game_lst)
    # the game is found
    if num_game == 1:
        game = game_lst[0]
        moves = json.loads(game.moves)
        # check whether the user can play for this turn
        if game.last_play != UserAccounts.objects.get(id=player_id):
            all_moves = []
            for mo in moves.values():
                all_moves += mo
            # the move was made before
            if move in all_moves:
                return False, "place taken"
            # move is correct
            else:
                if moves.get(str(player_id)):
                    moves[str(player_id)].append(move)
                else:
                    moves[str(player_id)] = []
                    moves[str(player_id)].append(move)
                # save the latest game moves
                game.moves = json.dumps(moves)
                game.last_play = UserAccounts.objects.get(id=player_id)
                game.save()
                return True, moves
        # not player's turn
        else:
            return False, "not your turn"
    # multiple games found with this game_id
    elif num_game > 1:
        return False, "internal error"
    # no game found with the game_id
    else:
        return False, "game not found"


def check_win(moves, game_id, player_id):
    """
    Check if the latest valid move finish the game.
    :param moves: a dict contains all the moves made by the players
    :param game_id: the id of the on going game
    :param player_id: id of the player who made the latest move
    :return:
    """
    # more than 2 moves are made
    if len(moves[str(player_id)]) >= 3:
        all_moves = []
        for mo in moves.values():
            all_moves += mo
        previous_moves = moves[str(player_id)]
        last_move_col = moves[str(player_id)][-1][1]
        last_move_row = moves[str(player_id)][-1][0]
        # check whether win by vertical line
        if [1, last_move_col] in previous_moves and [2, last_move_col] in previous_moves and [3, last_move_col] in previous_moves:
            game = Game.objects.get(id=game_id)
            user = UserAccounts.objects.get(id=player_id)
            game.finished = True
            game.winner = UserAccounts.objects.get(id=player_id)
            game.save()
            user.score += 1
            user.save()
            return True, "win"
        # check whether win by horizontal line
        elif [last_move_row, 1] in previous_moves and [last_move_row, 2] in previous_moves and [last_move_row, 3] in previous_moves:
            game = Game.objects.get(id=game_id)
            user = UserAccounts.objects.get(id=player_id)
            game.finished = True
            game.winner = UserAccounts.objects.get(id=player_id)
            game.save()
            user.score += 1
            user.save()
            return True, "win"
        # check whether win by diagnal lines
        elif last_move_row == last_move_col and [1,1] in previous_moves and [2,2] in previous_moves and [3,3] in previous_moves:
            game = Game.objects.get(id=game_id)
            user = UserAccounts.objects.get(id=player_id)
            game.finished = True
            game.winner = UserAccounts.objects.get(id=player_id)
            game.save()
            user.score += 1
            user.save()
            return True, "win"
        elif last_move_row + last_move_col == 4 and [3,1] in previous_moves and [2,2] in previous_moves and [1,3] in previous_moves:
            game = Game.objects.get(id=game_id)
            user = UserAccounts.objects.get(id=player_id)
            game.finished = True
            game.winner = user
            game.save()
            user.score += 1
            user.save()
            return True, "win"
        # check a tie game
        elif len(all_moves) == 9:
            game = Game.objects.get(id=game_id)
            game.finished = True
            game.save()
            return False, "tie"
        else:
            return False, "unresolved"
    # less than 3 moves, not possible to win
    else:
        return False, "unresolved"






