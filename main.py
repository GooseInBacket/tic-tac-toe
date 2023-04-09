from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import game

app = FastAPI()

app.include_router(game.router)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
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
