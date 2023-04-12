let PLAYER;
let MARK;

let linkField = document.getElementsByTagName('input')[0];
let buttons = document.querySelectorAll('.btn');
let ws = new WebSocket('ws://localhost:8000/ws/game');
let copyBtn = document.getElementsByClassName('copy-btn')[0];


function switchCurrentPlayer(currentPlayer){
    let currentSelecter = document.getElementsByClassName('selecter');
    if (currentPlayer == 'red'){
        currentSelecter[0].classList.add('current-player');
        currentSelecter[1].classList.remove('current-player');
    }else{
        currentSelecter[0].classList.remove('current-player');
        currentSelecter[1].classList.add('current-player');
    }
}

copyBtn.addEventListener('click', () => {
    linkField.select();
    document.execCommand('copy');
    copyBtn.classList.add('copyed');
    copyBtn.innerText = 'done';
})

buttons.forEach(button => {
    button.addEventListener('click', () => {
        if (button.innerText){
            throw new Error('this cell is busy');
        };
        let event = {'type': 'game'};

        event.pos = button.value
        event.player = PLAYER;
        event.mark = MARK;

        ws.send(JSON.stringify(event));
    })
});


ws.onopen = function(){
    let params = new URLSearchParams(window.location.search);
    let event = {'type': 'init'};
    if (params.has('join')){
        event.join = params.get('join');
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
            PLAYER = 'red';

            event.type = 'ok';
            linkField.value = window.location.href + `?join=${data.join}`;
            MARK = data.mark;
            console.log(data.join);
            
            ws.send(JSON.stringify(event));
            break;

        case 'join':
            PLAYER = 'blue';

            let linkBox = document.getElementsByClassName('link-box')[0];
            linkBox.style.display = 'none';

            event.type = 'ok'
            MARK = data.mark;

            ws.send(JSON.stringify(event));
            break;
        
        case 'mapping':
            let map = data.map
            let keys = Object.keys(map);
            keys.forEach(key => {
                buttons[Number(key)].innerText = map[key];
            })
            
            break;

        case 'player':
            let currentPlayer = data.current;
            switchCurrentPlayer(currentPlayer);

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

            switchCurrentPlayer(player);
            break;
        
        case 'win':
            winner = data.winner;
            pos = data.pos;
            mark = data.mark;
            let redScore = data.red;
            let blueScore = data.blue; 

            cell = document.querySelector(`.btn[value="${pos}"]`);
            cell.innerText = mark;
            
            buttons.forEach(btn => {
                btn.disabled = true;
            })

            alert(`Winner is ${winner}\nScore: red - ${redScore} blue - ${blueScore}`);
            
            break

        case 'exception':
            let desc = data.description;
            throw new Error(desc);
    }
}