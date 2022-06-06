from rest_framework.test import APITestCase
from django.test import TestCase
from accounts.models import UserAccounts
from rest_framework import status
from django.urls import reverse
from game.functions import *
from rest_framework.authtoken.models import Token


class GameTest(APITestCase):
    def setUp(self):
        self.test_user1 = UserAccounts.objects.create_user("test_user1", "user@test.com", "testpassword")
        self.test_user2 = UserAccounts.objects.create_user("test_user2", "user2@test.com", "testpassword")
        self.create_game_url = reverse("create-game")
        self.token1 = Token.objects.get(user_id=self.test_user1.id)
        self.token2 = Token.objects.get(user_id=self.test_user2.id)

    def test_create_game(self):
        response = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["player1"], self.test_user1.id)
        self.assertFalse(response.data["player2"])
        self.assertFalse(response.data["winner"])
        self.assertFalse(response.data["finished"])
        self.assertFalse(response.data["last_play"])
        self.assertEqual(response.data["password"], "000000")
        self.assertEqual(response.data["moves"], json.dumps({}))

    def test_without_token(self):
        response = self.client.post(self.create_game_url, follow='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_wrong_token(self):
        response = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + "adfasd", follow='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Token ' + self.token1.key, follow='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_game(self):
        response1 = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json')
        join_game_url = reverse("join-game", args=[response1.data["id"]])
        response2 = self.client.put(join_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json')
        self.assertEqual(response2.data["player2"], self.test_user2.id)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_join_game_without_token(self):
        response1 = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key,
                                     follow='json')
        join_game_url = reverse("join-game", args=[response1.data["id"]])
        response2 = self.client.put(join_game_url, follow='json')
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_creator_join_game(self):
        response1 = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key,
                                     follow='json')
        join_game_url = reverse("join-game", args=[response1.data["id"]])
        response2 = self.client.put(join_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json')
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)

    def test_join_non_existed_game(self):
        join_game_url = reverse("join-game", args=["22"])
        response = self.client.put(join_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GameFunctionsTest(TestCase):
    def setUp(self):
        self.test_user1 = UserAccounts.objects.create_user("test_user1", "user@test.com", "testpassword")
        self.test_user2 = UserAccounts.objects.create_user("test_user2", "user2@test.com", "testpassword")
        self.token = Token.objects.get(user_id=self.test_user1.id)
        self.create_game_url = reverse("create-game")
        self.game = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token.key, follow='json')
        self.join_game_url = reverse("join-game", args=[self.game.data["id"]])
        self.client.put(self.join_game_url, data={"game_id": self.game.data["id"]}, follow='json')

    def test_good_move(self):
        move_flag = verify_move([1,1], self.game.data["id"], self.test_user1.id)
        game = Game.objects.get(id=self.game.data["id"])
        self.assertTrue(move_flag[0])
        self.assertEqual(game.last_play.id, self.test_user1.id)
        self.assertEqual(move_flag[1], {str(self.test_user1.id): [[1,1]]})

    def test_bad_move(self):
        verify_move([1, 1], self.game.data["id"], self.test_user1.id)
        move_flag1 = verify_move([1, 1], self.game.data["id"], self.test_user2.id)
        move_flag2 = verify_move([0, 1], self.game.data["id"], self.test_user2.id)
        move_flag3 = verify_move([1, 4], self.game.data["id"], self.test_user2.id)
        move_flag4 = verify_move([1, 2], 44, self.test_user2.id)
        move_flag5 = verify_move([1, 2], self.game.data["id"], self.test_user1.id)
        move_flag6 = verify_move([], self.game.data["id"], self.test_user2.id)
        self.assertEqual(move_flag1[1], "place taken")
        self.assertFalse(move_flag1[0])
        self.assertEqual(move_flag2[1], "out of board")
        self.assertFalse(move_flag2[0])
        self.assertEqual(move_flag3[1], "out of board")
        self.assertFalse(move_flag3[0])
        self.assertEqual(move_flag4[1], "game not found")
        self.assertFalse(move_flag4[0])
        self.assertEqual(move_flag5[1], "not your turn")
        self.assertFalse(move_flag5[0])
        self.assertEqual(move_flag6[1], "no move")
        self.assertFalse(move_flag6[0])

    def test_win_and_unresolved_game(self):
        verify_move([1, 1], self.game.data["id"], self.test_user1.id)
        move_flag1 = verify_move([1, 2], self.game.data["id"], self.test_user2.id)
        win_flag1 = check_win(move_flag1[1], self.game.data["id"], self.test_user2.id)
        verify_move([2, 2], self.game.data["id"], self.test_user1.id)
        verify_move([1, 3], self.game.data["id"], self.test_user2.id)
        move_flag2 = verify_move([3, 3], self.game.data["id"], self.test_user1.id)
        win_flag2 = check_win(move_flag2[1], self.game.data["id"], self.test_user1.id)
        self.assertFalse(win_flag1[0])
        self.assertEqual(win_flag1[1], "unresolved")
        self.assertTrue(win_flag2[0])
        self.assertEqual(win_flag2[1], "win")
        self.assertEqual(UserAccounts.objects.get(id=self.test_user1.id).score, 1)

    def test_tie_game(self):
        moves = {"1":[[1,1], [1,3], [2,2], [3,1]],
                 "2": [[2,1], [3,2], [3,3], [2,3], [1,2]]}
        game = Game.objects.get(id=self.game.data["id"])
        game.last_play = UserAccounts.objects.get(id=self.test_user1.id)
        win_flag = check_win(moves, self.game.data["id"], self.test_user2.id)
        self.assertFalse(win_flag[0])
        self.assertEqual(win_flag[1], "tie")


class MakeMoveTest(APITestCase):
    def setUp(self):
        # set up users, create a game and join the game
        self.test_user1 = UserAccounts.objects.create_user("test_user1", "user@test.com", "testpassword")
        self.test_user2 = UserAccounts.objects.create_user("test_user2", "user2@test.com", "testpassword")
        self.token1 = Token.objects.get(user_id=self.test_user1.id)
        self.token2 = Token.objects.get(user_id=self.test_user2.id)
        self.create_game_url = reverse("create-game")
        self.game = self.client.post(self.create_game_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json')
        self.join_game_url = reverse("join-game", args=[self.game.data["id"]])
        self.client.put(self.join_game_url, data={"game_id": self.game.data["id"]}, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json')
        self.make_move_url = reverse("make-move")

    def test_make_move(self):
        input_data = {"game_id": self.game.data["id"], "row": 1, "col":1}
        self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)
        input_data = {"game_id": self.game.data["id"], "row": 1, "col": 2}
        response2 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json',
                                    data=input_data)
        input_data = {"game_id": self.game.data["id"], "row": 2, "col":2}
        self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)
        input_data = {"game_id": self.game.data["id"], "row": 1, "col": 3}
        self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json',
                                    data=input_data)
        input_data = {"game_id": self.game.data["id"], "row": 3, "col": 3}
        response3 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)

        self.assertEqual(response2.data["result"], "unresolved")
        self.assertEqual(response2.data["move"], [1, 2])
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data["result"], "win")
        self.assertEqual(response3.data["move"], [3, 3])
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(UserAccounts.objects.get(id=self.test_user1.id).score, 1)

    def test_make_bad_move(self):
        input_data = {"game_id": self.game.data["id"], "row": 1, "col": 1}
        self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                        data=input_data)
        response1 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json',
                                    data=input_data)

        input_data = {"game_id": self.game.data["id"], "row": 1, "col": 2}
        response2 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)

        input_data = {"game_id": self.game.data["id"], "row": 1, "col": 4}
        response3 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token2.key, follow='json',
                                    data=input_data)

        input_data = {"game_id": 99999, "row": 1, "col": 3}
        response4 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)

        input_data = {"game_id": self.game.data["id"]}
        response5 = self.client.put(self.make_move_url, HTTP_AUTHORIZATION='Bearer ' + self.token1.key, follow='json',
                                    data=input_data)

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.data["move"], "bad move: place taken")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data["move"], "bad move: not your turn")
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.data["move"], "bad move: out of board")
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response4.data["game"], "game not found")
        self.assertEqual(response5.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response5.data["move"], "bad move: no move")


class HighScoreListTes(APITestCase):
    def setUp(self):
        UserAccounts.objects.create(username="test_user1", email="test1@email.com", password="testpassword", score=1)
        UserAccounts.objects.create(username="test_user2", email="test2@email.com", password="testpassword", score=8)
        UserAccounts.objects.create(username="test_user3", email="test3@email.com", password="testpassword", score=5)
        UserAccounts.objects.create(username="test_user4", email="test4@email.com", password="testpassword", score=2)
        UserAccounts.objects.create(username="test_user5", email="test5@email.com", password="testpassword", score=5)
        UserAccounts.objects.create(username="test_user6", email="test6@email.com", password="testpassword", score=3)
        self.list_high_score_url = reverse("list-high-scores")

    def test_high_score_list(self):
        response = self.client.get(self.list_high_score_url, data={"top_n": 5}, follow='json')

        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["score"], 8)
