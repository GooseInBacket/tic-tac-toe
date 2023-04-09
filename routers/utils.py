from fastapi import WebSocket
import numpy as np
import random


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
        self.__players = ['red', 'blue']
        self.__borad = np.zeros(9, dtype=str)
        self.__win_a = np.array(['X', 'X', 'X'])
        self.__win_b = np.array(['O', 'O', 'O'])
        self.__current_player = None

    def check_bord(self):
        board = self.__borad.reshape(3, 3)
        print(board)

        if (board[:, :] == '').all():
            return 'clear'

        if (board[:, :] != '').all():
            return 'draw'

        for line in range(board.shape[1]):
            if (board[:, line] == self.__win_a).all() or (board[line] == self.__win_a).all():
                return 'X'
            elif (board[:, line] == self.__win_b).all() or (board[line] == self.__win_b).all():
                return 'O'
        else:
            a = np.array((board[0][0], board[1][1], board[2][2]))
            b = np.array((board[0][2], board[1][1], board[2][0]))

            if (a == self.__win_a).all() or (b == self.__win_a).all():
                return 'X'
            elif (a == self.__win_b).all() or (b == self.__win_b).all():
                return '0'

    def get_board(self):
        return self.__borad

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

    def next_player(self):
        print(self.__current_player)
        n = self.__players.index(self.__current_player)
        self.__current_player = self.__players[not n]
        print(self.__current_player)

