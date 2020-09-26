username = ''
socket = null
function lobby_click() {
    const value = document.getElementById('NameInput').value
    if(!value) return
    username = value
    socket = io.connect(location.origin, { transports: ["websocket"], query: `username=${username}`});
    socket.emit('connected')
    socket.on("game_starting", (response) => {
        if (response instanceof Object && response.player_hand) {
            GameIni(response)
        }
    })
    
    socket.on("other_move", (response) => {
        if (response instanceof Object && typeof response.move === 'string') {
            UpdateState(response)
        }
    })
    
    socket.on("score_update", (response) => {
        console.log(response);

        if (response instanceof Object && typeof response.score === 'number') {
            UpdateScores(response)
        }
    })

}

let name = document.getElementById('playerName');
let otherName = document.getElementById('otherPlayerName');
let score = document.getElementById('playerScore');
let otherScore = document.getElementById('otherPlayerScore');
let openCard = document.getElementById('openCard');
let otherOpenCard = document.getElementById('otherOpenCard');
let cardStack = document.getElementById('cardStackContainer');
let otherCardStack = document.getElementById('otherCardStackContainer');


function cardClick(e) {
    e = e || window.event;
    const target = e.target || e.srcElement
    if(socket) {
        openCard.innerHTML = "<div class='card'>"+ target.innerHTML +"</div>"
        socket.emit('game_move', target.innerHTML)
        target.remove()
    }
}

function updateStacks(hand) {
    cardStack.innerHTML = "";
    otherCardStack.innerHTML = "";
    for(var card of hand)
    {
        cardStack.innerHTML += "<div class='card' onclick='cardClick()'>"+ card +"</div>"
        otherCardStack.innerHTML += "<div class='card'></div>"
    }
}


/**
 * Initialises game UI elements with Initial State from server
 */
function GameIni(response)
{
    name.innerHTML = username;
    otherName.innerHTML = response.other_player_name;
    score.innerHTML = 0;
    otherScore.innerHTML = 0;

    //Empty open cards
    openCard.innerHTML = "";
    otherOpenCard.innerHTML = "";
    document.getElementById('Game').style.display = 'block'
    document.getElementById('RegisterContainer').style.display = 'none'
    updateStacks(response.player_hand)
}

function UpdateScores(response)
{
    score.innerHTML = response.score;
    otherScore.innerHTML = response.other_score;
}


function UpdateState(response)
{
    otherOpenCard.innerHTML = "<div class='card'>"+ response.move +"</div>"
    updateStacks(response.player_hand)
}