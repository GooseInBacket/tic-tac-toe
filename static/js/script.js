let PLAYER;

let linkField = document.getElementsByTagName('input')[0];
let buttons = document.querySelectorAll('.btn');
let ws = new WebSocket('ws://localhost:8000/ws/game');

buttons.forEach(button => {
    button.addEventListener('click', () => {
        if (button.innerText){
            throw new Error('this cell is busy');
        };
        let mark = PLAYER == 'red' ? 'X' : 'O';
        let event = {'type': 'game'};

        // button.innerText = mark;

        event.pos = button.value
        event.player = PLAYER;
        event.mark = mark;

        ws.send(JSON.stringify(event));
    })
});


ws.onopen = function(){
    let params = new URLSearchParams(window.location.search);
    let event = {'type': 'init'};
    if (params.has('join')){
        event.join = params.get('join')
    }
    ws.send(JSON.stringify(event));
}

ws.onmessage = function(e){
    let pos;
    let mark;
    let player;
    let cell;
    let winner;
    let data = JSON.parse(e.data);
    let event = {};
    console.log(data);
    switch (data.type){
        case 'init':
            event.type = 'ok'
            linkField.value = window.location.href + `?join=${data.join}`;
            PLAYER = data.player;
            console.log(data.join);
            
            ws.send(JSON.stringify(event));
            break;

        case 'join':
            linkField.style.display = 'none';

            event.type = 'ok'
            PLAYER = data.player;

            ws.send(JSON.stringify(event));
            break;
        
        case 'mapping':
            let map = new Map(Object.entries(data.map))
            console.log(map.keys);
            for (key of map.keys){
                buttons[Number(key)].innerText(map.get(key));
            }

            break;

        case 'player':
            let currentPlayer = data.current;
            if (currentPlayer != PLAYER){
                buttons.forEach(btn => {
                    btn.disabled = true;
                })
            }
            break;

        case 'game':
            pos = data.pos;
            mark = data.mark;
            player = data.player;

            buttons.forEach(btn => {
                if (player == PLAYER){
                    btn.disabled = false;
                }
                else{
                    btn.disabled = true;
                }
                
            })

            cell = document.querySelector(`.btn[value="${pos}"]`);
            cell.innerText = mark;
            break;
        
        case 'win':
            winner = data.winner;
            player = data.player;
            pos = data.pos;
            mark = data.mark;

            cell = document.querySelector(`.btn[value="${pos}"]`);
            cell.innerText = mark;
            
            buttons.forEach(btn => {
                btn.disabled = true;
            })

            console.log(winner);
            
            break

        case 'exception':
            let desc = data.description;
            throw new Error(desc);
    }
}