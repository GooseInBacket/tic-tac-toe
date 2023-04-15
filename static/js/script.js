let PLAYER;
let MARK;

let buttons = document.querySelectorAll('.btn');
let ws = new WebSocket('ws://localhost:8000/ws/game');
let linkField = document.getElementsByTagName('input')[0];
let copyBtn = document.getElementsByClassName('copy-btn')[0];
let ctrlBtn = document.getElementsByClassName('popUp-ctrl-btn');


function btnDisabled(state = false){
    buttons.forEach(btn => {
        btn.disabled = state;
    })
}

function switchCurrentPlayer(currentPlayer){
    let symbolRed = (currentPlayer == PLAYER) ? MARK : (MARK == 'X') ? 'O' : 'X' 
    let symbolBlue = (symbolRed == 'X') ? 'O' : 'X';

    document.getElementById(symbolRed).classList.add('current-player');
    document.getElementById(symbolBlue).classList.remove('current-player');
}

ctrlBtn[0].addEventListener('click', () => {
    // переход в следующий раунд
    let event = {
        'type': 'await',
        'player': PLAYER
    }

    ws.send(JSON.stringify(event))
});

ctrlBtn[1].addEventListener('click', () =>{
    // выход из игры
    let event = {
        'type': 'exit',
        'player': PLAYER
    }

    ws.send(JSON.stringify(event));
})

copyBtn.addEventListener('click', () => {
    linkField.select();
    document.execCommand('copy');
    copyBtn.classList.add('copyed');
})

copyBtn.addEventListener('animationend', () => {
    copyBtn.classList.remove('copyed');
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
    let player;
    let currentPlayer;
    let data = JSON.parse(e.data);
    let event = {};

    console.log(data);
    switch (data.type){
        case 'init':
            PLAYER = 'red';

            event.type = 'await';
            event.player = PLAYER;

            linkField.value = window.location.href + `?join=${data.join}`;
            
            ws.send(JSON.stringify(event));
            break;

        case 'join':
            PLAYER = 'blue';

            document.getElementsByClassName('link-box')[0].style.display = 'none';

            event.type = 'await';
            event.player = PLAYER;

            ws.send(JSON.stringify(event));
            break;
        
        case 'game':
            player = data.next;
            buttons.forEach(btn => {btn.disabled = !(player == PLAYER);});
            document.querySelector(`.btn[value="${data.pos}"]`).innerText = data.mark;
            switchCurrentPlayer(player);

            break;
        
        case 'win':
            document.getElementsByClassName('left')[0].innerText = data.red;
            document.getElementsByClassName('right')[0].innerText = data.blue;
            document.querySelector(`.btn[value="${data.pos}"]`).innerText = data.mark;
            document.getElementsByClassName('pop-up-container')[0].style.display = 'grid';

            btnDisabled(true);
            
            let resultBox = document.getElementById('result-baner');
            let span = document.createElement('span');

            span.innerText = (data.winner == 'red') ? 'красным' : 'синим';
            span.style.color = (data.winner == 'red') ? 'var(--palyer-one)' : 'var(--player-two)';

            resultBox.innerText = 'Победа за ';
            resultBox.style.color = 'var(--bg-2)';
            resultBox.appendChild(span);

            break;
        
        case 'draw':
            document.querySelector(`.btn[value="${data.pos}"]`).innerText = data.mark;
            document.getElementsByClassName('pop-up-container')[0].style.display = 'grid';

            btnDisabled(true);

            result = document.getElementById('result-baner');
            result.innerText = 'Ничья';
            result.style.color = 'var(--draw-color)';

            break;

        case 'ready':
            MARK = data.mark;
            document.getElementsByClassName('pop-up-container')[0].style.display = 'none';
            btnDisabled(true);

            break;

        case 'all_ready':
            document.getElementsByClassName('pop-up-container')[0].style.display = 'none';

            currentPlayer = data.player;
            buttons.forEach(btn => {
                btn.innerText = '';
                btn.disabled = !(currentPlayer === PLAYER);
            })

            switchCurrentPlayer(currentPlayer);
            break;

        case 'exception':
            throw new Error(data.description);
    }
}