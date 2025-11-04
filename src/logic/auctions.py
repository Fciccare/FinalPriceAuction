from .robot import Robot
from .player import Player
from .deck import Deck
from .card import *

class Auctions:
    def __init__(self, budget_umano, budget_robot, modalita_cooperativa=False):
        # Setup players
        self.human = Player("Umano", 0 , 1000)
        self.robot =  Robot("Mirokai", 0 , 1000, "competitive")
        
        # Setup deck
        self.deck = Deck.load_from_json("deck_1.json")
        self.deck.shuffle()
        
        #Setup Game
        self.current_player = self.human

    def start_game(self):
        print(f"The game begins in {self.mode} mode")
        
        # The game continues as long as the deck is not empty (Rule 8a)
        while len(self.deck) > 0:
            
            # Check end condition (Rule 8b)
            if not self.is_bidding_possible():
                print("Both players can no longer make bids.")
                break # Exits the while loop

            current_card = self.deck.pop(0) # Draw the first card
            
            # Start the single auction
            self.manage_auction(current_card)
            
            # Reset who starts the next auction (Rule 1 only says who starts the *game*)
            # You could alternate who makes the first offer, for example:
            # self.current_player = self.robot if self.current_player == self.human else self.human

        # End of 'while' loop, the game is over
        self.calculate_final_score()


    def is_bidding_possible(self):
        """
        Controlla se almeno un giocatore può fare un'offerta sulla prossima carta.
        Questo implementa la logica per la Regola 8b e 8c.
        La partita termina (restituisce False) solo se NESSUNO può puntare.
        """
        # Se non ci sono più carte, il "bidding" non è possibile
        if not self.deck:
            return False
            
        # Controlliamo la base d'asta della *prossima* carta (senza estrarla)
        next_card_starting_bid = self.deck[0].starting_bid # o .base_asta

        human_can_bid = self.human.budget >= next_card_starting_bid
        robot_can_bid = self.robot.budget >= next_card_starting_bid
        
        # Il gioco continua se l'umano PUO' O il robot PUO'
        # Ritorna True se almeno uno dei due può fare un'offerta
        return human_can_bid or robot_can_bid

    def manage_auction(self, card: Card):

        # Resetta lo stato "passato" dei giocatori
        self.player.has_passed = False
        self.robot.has_passed = False

        current_bid = 0
        highest_bidder = None
        # The auction continues until one of them has passed
        while not (self.human.has_passed or self.robot.has_passed):
            
            active_player = self.current_player
            
            # Check if the player can bid (budget >= starting_bid AND budget > current_bid)
            can_bid = (active_player.budget >= card.starting_bid) and \
                    (active_player.budget > current_bid)

            if not can_bid:
                print(f"{active_player.player_id} doesn't have enough funds and passes.")
                active_player.has_passed = True
            else:
                # Get the action (bid or pass)
                action = self.get_player_action(active_player, card.starting_bid, current_bid)
                
                if action == "pass":
                    active_player.has_passed = True
                else: # The action is a bid (a number)
                    current_bid = action
                    highest_bidder = active_player
                    print(f"{active_player.player_id} bids ${current_bid}")

            # Change turn (Rule 2)
            self.current_player = self.robot if active_player == self.human else self.human

        # --- End of while loop: Auction finished ---
        self.resolve_auction(card, highest_bidder, current_bid)


    def resolve_auction(self, card, winner, winning_bid):
        # Case 1: Nobody bid (e.g., both pass immediately)
        if winner is None:
            print(f"No bids. The card {card.card_name} is burned.")
            #self.burned_cards.append(card)
            return

        # Case 2: There is a winner, check the hidden threshold (Rule 3)
        if winning_bid >= card.hidden_threshold:
            # Success! The threshold is met
            print(f"{winner.player_id} wins {card.card_name} for ${winning_bid}!")
            winner.win_card(card, winning_bid)
        else:
            # Failure! Threshold not met
            print(f"{winner.player_id}'s bid (${winning_bid}) did not meet the hidden threshold!")
            print(f"The card {card.card_name} is burned. The budget is not subtracted.")
            #self.burned_cards.append(card)

    def calculate_final_score(self):
        if self.calculate_cooperative_victory():
            print("Cooperative")
        else:
            self.calculate_competitive_victory() 

    def calculate_cooperative_victory(self):
        print("\n--- Calculating Cooperative Victory (Rule 7) ---")
        
        counts = {} # e.g.: {Category.ART: {"Human": 2, "Robot": 2}, ...}
        
        # Initialize counts
        for cat in Category:
            counts[cat] = {self.human.player_id: 0, self.robot.player_id: 0}

        # Count players' cards
        for player in [self.human, self.robot]:
            for card in player.cards:
                counts[card.category][player.player_id] = len(self.player.cards[card.category])
                
        # Check the condition
        victory = True
        for cat in Category:
            count_human = counts[cat][self.human.player_id]
            count_robot = counts[cat][self.robot.player_id]
            print(f"Category {cat.value}: Human {count_human}, Robot {count_robot}")
            if count_human != count_robot:
                victory = False

        if victory:
            return True
        else:
            return False


    # Inside the Game class
def calculate_competitive_victory(self):
    print("\n--- Calculating Competitive Score (Rules 5 & 6) ---")
    
    human_score = 0
    robot_score = 0

    # 1. Sum VP from cards (Rule 6) - NESTED LOOP
    # Iterate through the dictionary's values (which are lists of cards)
    for card_list_human in self.human.cards.values():
        for card in card_list_human:
            human_score += card.victory_points
            
    for card_list_robot in self.robot.cards.values():
        for card in card_list_robot:
            robot_score += card.victory_points

    # 2. Calculate category bonuses (Rule 5) - NOW MUCH SIMPLER
    for cat in Category:
        # The count is now direct, no loop needed
        human_has = len(self.human.cards[cat])
        robot_has = len(self.robot.cards[cat])

        # Check for +20 bonus (Rule 5b)
        if human_has == 4:
            print(f"Human gets +20 VP (all {cat.value} cards)")
            human_score += 20
        elif robot_has == 4:
            print(f"Robot gets +20 VP (all {cat.value} cards)")
            robot_score += 20
        
        # Otherwise, check for +5 bonus (Rule 5a)
        elif human_has > robot_has:
            print(f"Human gets +5 VP (majority of {cat.value})")
            human_score += 5
        elif robot_has > human_has:
            print(f"Robot gets +5 VP (majority of {cat.value})")
            robot_score += 5

    # 3. Final result (unchanged)
    print("\n--- FINAL SCORE ---")
    print(f"Human: {human_score} VP")
    print(f"Robot: {robot_score} VP")
    
    if human_score > robot_score:
        print("The Human wins!")
    elif robot_score > human_score:
        print("The Robot wins!")
    else:
        print("It's a draw!")