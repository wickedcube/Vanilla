from random import shuffle
import itertools
unq_card_list = ['r', 'p', 's', 'w', 'x']
deck = list(itertools.chain(['r']*8, ['p']*8, ['s']*8, ['w']*4, ['x']*4))

shuffle(deck)
first_player_hand = deck[0:5]
second_player_hand = deck[5:10]
remaining = deck[10:]
player1_score = 0
player2_score = 0
beating_list = ['p', 's', 'r']
round_card_count = 0
def modify_hands():
  global first_player_hand, second_player_hand, remaining
  if (len(remaining) <= 0) :
    return
  new_number = min(2, len(remaining) // 2)
  first_player_hand += remaining[:new_number]
  second_player_hand += remaining[new_number: 2*new_number]
  remaining = remaining[2*new_number:]

def common_win(): 
  global round_card_count, player1_score, player2_score
  print(f'player1_score :{player1_score}, player2 score : {player2_score}')
  round_card_count = 0
  modify_hands()
def player1_win():
  global player1_score, round_card_count
  player1_score += round_card_count
  common_win()


def player2_win():
  global player2_score, round_card_count
  player2_score += round_card_count
  common_win()

while(len(remaining) > 0 or len(first_player_hand) > 0):
  print('player 1 cards ' + ' '.join(first_player_hand))
  print('player 2 cards ' + ' '.join(second_player_hand))
  player1_value = None
  player2_value = None
  while(player1_value not in first_player_hand):
    player1_value = input("Please enter player1 input:\n")
  while(player2_value not in second_player_hand):
    player2_value = input("Please enter player2 input:\n")
  first_player_hand.remove(player1_value)
  second_player_hand.remove(player2_value)
  round_card_count += 2
  if (player1_value == player2_value or player1_value == 'x' or player2_value == 'x'): 
    if (len(first_player_hand) <= 0) :
      modify_hands()
    continue
  if (player1_value == 'w'): 
    player1_win()
    continue
  if (player2_value == 'w'): 
    player2_win()
    continue

  if (beating_list[unq_card_list.index(player1_value)] == player2_value): 
    player2_win()
  else: player1_win()


  

