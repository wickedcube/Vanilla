from flask import Flask, request
import os
from flask_socketio import SocketIO
from random import shuffle
import itertools
unq_card_list = ['r', 'p', 's', 'w', 'x']
beating_list = ['p', 's', 'r']
def init_game(player1, player2):
  deck = list(itertools.chain(['r']*8, ['p']*8, ['s']*8, ['w']*4, ['x']*4))
  shuffle(deck)
  first_player_hand = deck[0:5]
  second_player_hand = deck[5:10]
  remaining = deck[10:]
  player1_score = 0
  player2_score = 0
  round_card_count = 0
  return {player1: player2, player2: player1, player1 + '_hand' : first_player_hand, player2 + '_hand' :second_player_hand, 'remaining': remaining, player1 + '_score' : player1_score, player2 + '_score': player2_score, 'round_card_count': round_card_count}

def modify_hands(gid, player1, player2):
  if (len(GAME_INFO[gid]['remaining']) <= 0) :
    return
  new_number = min(2, len(GAME_INFO[gid]['remaining']) // 2)
  GAME_INFO[gid][player1 + '_hand'] += GAME_INFO[gid]['remaining'][:new_number]
  GAME_INFO[gid][player2 + '_hand'] += GAME_INFO[gid]['remaining'][new_number: 2*new_number]
  GAME_INFO[gid]['remaining'] = GAME_INFO[gid]['remaining'][2*new_number:]

def player_win(gid, player1):
  GAME_INFO[gid][player1 + '_score'] += GAME_INFO[gid]['round_card_count']
  GAME_INFO[gid]['round_card_count'] = 0
  player2 = GAME_INFO[gid][player1]
  socketio.emit('score_update', {'score': GAME_INFO[gid][player1 + '_score'], 'other_score': GAME_INFO[gid][player2 + '_score']},  room=player1)
  socketio.emit('score_update', {'score': GAME_INFO[gid][player2 + '_score'], 'other_score': GAME_INFO[gid][player1 + '_score']}, room=player2)
  modify_hands(gid, player1, player2)


app = Flask(__name__)

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

GAME_SESSIONS = {}
sid_to_username = {}
GAME_INFO = {}

waiting_users = []

@app.route('/')
def echo():
  return app.send_static_file('index.html')

@socketio.on('connect')
def socket_init():
    """
    Store the socketid of the client once it is connected and link it to appropriate token.
    """
    if request.args.get('username') is None: return
    GAME_SESSIONS[request.args.get('username')] = {'sid':request.sid}
    sid_to_username[request.sid] = request.args.get('username')

@socketio.on('connected')
def initial_greeting():
  username = sid_to_username[request.sid]
  game_partner = None
  global waiting_users
  if (len(waiting_users) >= 1):
    game_partner = waiting_users[0]
    waiting_users = waiting_users[1:]
    min_id = min(GAME_SESSIONS[username]['sid'], GAME_SESSIONS[game_partner]['sid'])
    max_id = max(GAME_SESSIONS[username]['sid'], GAME_SESSIONS[game_partner]['sid'])
    game_id = min_id + '_' + max_id
    GAME_SESSIONS[username]['game_id'] = game_id
    GAME_SESSIONS[game_partner]['game_id'] = game_id
    GAME_INFO[game_id] = init_game(min_id, max_id)
    socketio.emit('game_starting', { 'player_hand': GAME_INFO[game_id][min_id+'_hand'], 'other_player_name': sid_to_username[max_id] },  room=min_id)
    socketio.emit('game_starting', { 'player_hand': GAME_INFO[game_id][max_id+'_hand'], 'other_player_name': sid_to_username[min_id] }, room=max_id)
  else:
    waiting_users.append(username)

@socketio.on('game_move')
def game_move(card):
  sid = request.sid
  sess = GAME_SESSIONS[sid_to_username[sid]]
  gid = sess['game_id']
  g_sess = GAME_INFO[gid]
  if card not in g_sess[sid + '_hand']:
    return
  other_sid = g_sess[sid]
  GAME_INFO[gid][sid + '_hand'].remove(card)
  GAME_INFO[gid][sid+'_move'] = card
  if g_sess.get(other_sid + '_move'):
    GAME_INFO[gid]['round_card_count'] += 2
    min_sid = min(sid, other_sid)
    max_sid = max(sid, other_sid)
    player1_value = GAME_INFO[gid][min_sid + '_move']
    player2_value = GAME_INFO[gid][max_sid + '_move']
    socketio.emit('other_move',{'move': GAME_INFO[gid][other_sid + '_move'], 'player_hand': GAME_INFO[gid][sid+'_hand']}, room=sid)
    socketio.emit('other_move',{'move': GAME_INFO[gid][sid + '_move'], 'player_hand': GAME_INFO[gid][other_sid+'_hand']}, room=g_sess[sid])
    GAME_INFO[gid][other_sid+'_move'] = None
    GAME_INFO[gid][sid+'_move'] = None
    
    if (player1_value == player2_value or player1_value == 'x' or player2_value == 'x'): 
      if (len(g_sess[min_sid + '_hand']) <= 0) :
        modify_hands(gid, min_sid, max_sid)
      return
    if (player1_value == 'w'): 
      player_win(gid, min_sid)
      return
    if (player2_value == 'w'): 
      player_win(gid, max_sid)
      return

    if (beating_list[unq_card_list.index(player1_value)] == player2_value): 
      player_win(gid, max_sid)
    else: player_win(gid, min_sid)
  else:
    GAME_INFO[gid][sid + '_move'] = card
    socketio.emit('other_move',{'move': '', 'player_hand': GAME_INFO[gid][other_sid+'_hand']}, room=g_sess[sid])



  




if __name__ == '__main__':
  socketio.run(app, host="0.0.0.0", port="8000", log_output=True)