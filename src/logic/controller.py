from logic.deck import Deck
from logic.player import Player
from logic.robot import Robot


def start_game():

    #Crea i giocatori
    player = Player("Umano", 0 , 1000)
    robot = Robot("Robot", 0 , 1000, "competitive")

    #Carica il mazzo dal JSON
    deck = Deck.load_from_json("deck_1.json")
    #Mescola il mazzo
    deck.shuffle()

    #Inizia il gioco (round dopo round)
    round_num = 1
    while len(deck) > 0:
        print(f"\n--- ROUND {round_num} ---")
        card = deck.draw()
        print(f" Carta scoperta: {card.card_name} ({card.category_color}) - Valore: {card.victory_points} PV")
  
        

    #Fine partita: calcolo dei punti
    print("\n🎯 FINE PARTITA!")
    print(f"{player.player_id} ha {player.calculate_victory_points()} PV")
    print(f"{robot.robot_id} ha {robot.calculate_victory_points()} PV")

    if player.calculate_victory_points() > robot.calculate_victory_points():
        print("✨ Hai vinto!")
    elif player.calculate_victory_points() < robot.calculate_victory_points():
        print("🤖 Il robot vince!")
    else:
        print("⚖️ Pareggio!")
