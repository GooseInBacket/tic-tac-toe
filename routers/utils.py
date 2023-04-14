import random
from itertools import cycle

from fastapi import WebSocket
import numpy as np


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: (dict[str, str], str)):
        for connection in self.active_connections:
            await connection.send_json(message)


class Game:
    def __init__(self):
        self.__players = {
            'red': [None, 0],
            'blue': [None, 0]
        }
        self.__marks = cycle(('X', 'O'))
        self.__borad = np.zeros(9, dtype=str)
        self.__win_a = np.array(['X', 'X', 'X'])
        self.__win_b = np.array(['O', 'O', 'O'])
        self.__current_player = None
        self.__ready_for_resume = 0;

    def check_bord(self):
        board = self.__borad.reshape(3, 3)
        print(board)

        if (board[:, :] == '').all():
            return 'clear'

        if (board[:, :] != '').all():
            return 'draw'

        for line in range(board.shape[1]):
            if (board[:, line] == self.__win_a).all() or (board[line] == self.__win_a).all():
                winner = 'red' if self.__players['red'][0] == 'X' else 'blue'
                return winner
            elif (board[:, line] == self.__win_b).all() or (board[line] == self.__win_b).all():
                winner = 'red' if self.__players['red'][0] == 'O' else 'blue'
                return winner
        else:
            a = np.array((board[0][0], board[1][1], board[2][2]))
            b = np.array((board[0][2], board[1][1], board[2][0]))

            if (a == self.__win_a).all() or (b == self.__win_a).all():
                winner = 'red' if self.__players['red'][0] == 'X' else 'blue'
                return winner
            elif (a == self.__win_b).all() or (b == self.__win_b).all():
                winner = 'red' if self.__players['red'][0] == 'O' else 'blue'
                return winner

    def restart(self):
        self.__borad = np.zeros(9, dtype=str)
        self.set_current_player()

    def ready(self):
        self.__ready_for_resume += 1
        if self.__ready_for_resume == 2:
            self.__ready_for_resume = 0
            self.restart()
            return True

    def next_player(self):
        players_list = list(self.__players.keys())
        current_player = players_list.index(self.__current_player)
        self.__current_player = players_list[not current_player]

    def get_board(self):
        return self.__borad

    def get_mark(self):
        return next(self.__marks)

    def get_new_mark(self, player):
        current_mark = self.__players[player][0]
        print(current_mark)
        self.__players[player][0] = 'X' if current_mark == 'O' else 'O'
        print(self.__players[player][0])
        return self.__players[player][0]

    def get_score(self, player: str):
        return self.__players[player][1]

    def set_cell(self, pos: int, mark: str):
        assert pos in range(10)
        assert mark.isalpha()
        assert mark in "XO"
        assert self.__borad[pos] == ''

        self.__borad[pos] = mark

    def get_current_player(self):
        return self.__current_player

    def set_current_player(self):
        self.__current_player = random.choice(['red', 'blue'])

    def set_mark(self, player: str, mark: str):
        self.__players.get(player)[0] = mark

    def set_score_for(self, player):
        self.__players.get(player)[1] += 1
