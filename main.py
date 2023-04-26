import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from loguru import logger

from routers import game

app = FastAPI()

app.include_router(game.router)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

logger.add(sys.stderr, format='{time} {level} {message}', filter='my_module', level='INFO')


@app.get('/coop', response_class=HTMLResponse)
async def index(request: Request):
    event, *key = request.url.query.split('=')
    query = {
        'name': 'index.html',
        'status_code': 200,
        'context': {'request': request}
    }
    if event == 'join' and not game.JOIN.get(*key):
        query['name'] = 'room_error.html'
        query['status_code'] = 404
    response = templates.TemplateResponse(**query)
    return response


@app.get('/', response_class=HTMLResponse)
async def main_menu(request: Request):
    query = {
        'name': 'mainmenu.html',
        'status_code': 200,
        'context': {'request': request}
    }
    response = templates.TemplateResponse(**query)
    return response
