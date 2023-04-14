import secrets

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from .utils import ConnectionManager, Game

router = APIRouter()
manager = ConnectionManager()

JOIN = dict()


async def get_map(game: Game, ws: WebSocket):
    board = game.get_board()
    cells = {i: cell for i, cell in enumerate(board) if cell}

    response = {
        'type': 'mapping',
        'map': cells,
    }

    await ws.send_json(response)


async def start_game(game: Game, ws: WebSocket, connections: set[WebSocket]):
    while True:
        event = await ws.receive_json()
        if event['type'] == 'ok':
            player = game.get_current_player()

            await ws.send_json({
                'type': 'player',
                'current': player
            })
            logger.info(f'Player ready to play')
            break

    while True:
        event = await ws.receive_json()

        current_player = game.get_current_player()
        player = event['player']

        if event['type'] == 'resume':
            player = event['player']
            all_ready = game.ready()

            if all_ready:
                game.next_player()
                next_player = game.get_current_player()

                await ws.send_json({'type': 'mark', 'mark': game.get_new_mark(player)})

                response = {
                    'type': 'all_ready',
                    'player': next_player,
                }
                for socket in connections:
                    await socket.send_json(response)
            else:
                response = {
                    'type': 'ready',
                    'player': player,
                    'mark': game.get_new_mark(player)
                }
                await ws.send_json(response)
            continue

        if player != current_player:
            response = {
                'type': 'exception',
                'description': 'wrong player'
            }
            await ws.send_json(response)
            continue

        pos = int(event['pos'])
        mark = event['mark']
        game.set_cell(pos, mark)
        state = game.check_bord()
        response = {}

        if state is None:
            game.next_player()
            next_player = game.get_current_player()
            response = {
                'type': 'game',
                'pos': pos,
                'mark': mark,
                'player': next_player
            }

        elif state in ('red', 'blue'):
            game.set_score_for(state)
            response = {
                'type': 'win',
                'winner': state,
                'pos': pos,
                'mark': mark,
                'red': game.get_score('red'),
                'blue': game.get_score('blue')
            }
        elif state == 'draw':
            response = {
                'type': 'draw'
            }
        elif state == 'clear':
            response = {
                'type': 'exception',
                'description': 'Field is clear'
            }

        for sock in connections:
            await sock.send_json(response)


@router.websocket('/ws/game')
async def init(ws: WebSocket):
    await ws.accept()
    try:
        event = await ws.receive_json()
        if 'join' in event:
            ''' Присоединяется '''
            key = event['join']
            game, connections = JOIN[key]
            mark = game.get_mark()
            game.set_mark('blue', mark)
            connections.add(ws)

            response = {
                'type': 'join',
                'player': 'blue',
                'mark': mark
            }

            logger.info(f'Player join to {key} room')
            await ws.send_json(response)
            await get_map(game, ws)
            await start_game(game, ws, connections)
        else:
            ''' Хост '''
            game = Game()
            game.set_current_player()

            connections = {ws}
            key = secrets.token_urlsafe(12)
            mark = game.get_mark()

            game.set_mark('red', mark)

            JOIN[key] = game, connections

            response = {
                'type': 'init',
                'join': key,
                'mark': mark
            }

            logger.info(f'Game {key} created')
            await ws.send_json(response)
            await start_game(game, ws, connections)

    except WebSocketDisconnect:
        _, connections = JOIN[key]
        connections = list(connections)
        connections.remove(ws)

        logger.info(f'Player {ws.client} left game')
        for socket in connections:
            await socket.send_text('Client left')

    finally:
        del JOIN[key]
        logger.info(f'Game {key} delete')
