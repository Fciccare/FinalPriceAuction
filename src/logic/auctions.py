import pandas as pd
import os

from .robot import Robot
from .player import Player
from .deck import Deck
from .card import *

class Auctions:
    def __init__(self, budget_umano=1000, budget_robot=1000, modalita_cooperativa=False):

        # Setup players
        self.human = Player("Umano", 0 , budget_umano)
        self.robot =  Robot("Mirokai", 0 , budget_robot, "competitive")

        # Setup deck
        self.deck = Deck.load_from_json("deck_1.json")
        self.deck.shuffle()

        #Setup Game
        self.current_player = self.human
        self.current_bid = 0
        self.highest_bidder = None

        # --- LOGGING SETUP ---
        self.turn_number = 1
        self.log_entry_counter = 0
        self.log_data = []

    def start_game(self):

        # Start the single auction
        self.manage_auction()

        # Reset who starts the next auction (Rule 1 only says who starts the *game*)
        # You could alternate who makes the first offer, for example:
        # self.current_player = self.robot if self.current_player == self.human else self.human

        # End of 'while' loop, the game is over
        result = self.calculate_final_score()

        self._log_game_state(None, result, 0, None, None)


        self._save_log_to_excel()


    def is_bidding_possible(self, card: Card):
        """
        Controlla se almeno un giocatore può fare un'offerta sulla prossima carta.
        Questo implementa la logica per la Regola 8b e 8c.
        La partita termina (restituisce False) solo se NESSUNO può puntare.
        """
        # Se non ci sono più carte, il "bidding" non è possibile
        if not self.deck:
            return False

        # Controlliamo la base d'asta della *prossima* carta (senza estrarla)
        next_card_starting_bid = card.starting_bid # o .base_asta

        human_can_bid = self.human.budget >= next_card_starting_bid
        robot_can_bid = self.robot.budget >= next_card_starting_bid

        # Il gioco continua se l'umano PUO' O il robot PUO'
        # Ritorna True se almeno uno dei due può fare un'offerta
        return human_can_bid or robot_can_bid

    def manage_auction(self, card: Card, action):
        # Resetta lo stato "passato" dei giocatori
        active_player = self.current_player
        turn_log = ""

        if action == "pass":
            active_player.has_passed = True
            turn_log = "Pass (Volontario)"
            self._log_game_state(card, turn_log, self.current_bid, self.highest_bidder, active_player)
            self.current_player = self.robot if active_player == self.human else self.human
            if self.current_bid == 0 and not self.current_player.has_passed:
                return False
        else:  # The action is a bid (a number)
            if (action >= card.starting_bid) and (action > self.current_bid):
                if active_player.can_bid(action):
                    self.current_bid = action
                    self.highest_bidder = active_player
                    print(f"{active_player.player_id} bids ${self.current_bid}")
                    turn_log = f"Puntata ${self.current_bid}"
                    print(active_player.player_id + " - "+ turn_log)
                else:
                    print("Cant'Bid for ammount: " + active_player.player_id)
                    return False
            else:
                print("Cant'Bid: " + active_player.player_id)
                return False

        self._log_game_state(card, turn_log, self.current_bid, self.highest_bidder, active_player)
        self.current_player = self.robot if active_player == self.human else self.human
        return True

    def can_bid(self, active_player, card, current_bid):
           if (active_player.budget >= card.starting_bid) and (active_player.budget > current_bid):
                return True
           else:
               print(f"{active_player.player_id} doesn't have enough funds and passes.")
               active_player.has_passed = True
               turn_log = "Pass (Fondi Insuff.)"
               self._log_game_state(card, turn_log, current_bid, self.highest_bidder, active_player)
               self.current_player = self.robot if active_player == self.human else self.human
               return False

    def resolve_auction(self, card, winner, winning_bid):
        # Case 1: Nobody bid (e.g., both pass immediately)
        if winner is None:
            print(f"No bids. The card {card.card_name} is burned.")
            #self.burned_cards.append(card)
            self._log_game_state(card, "Bruciata (Nessuna Offerta)", winning_bid, winner, None)
            self.current_bid=0
            self.highest_bidder = None
            self.turn_number += 1
            return False
        # Case 2: There is a winner, check the hidden threshold (Rule 3)
        if winning_bid >= card.heat_requirement:
            # Success! The threshold is met
            print(f"{winner.player_id} wins {card.card_name} for ${winning_bid}!")
            winner.win_card(card, winning_bid)
            self._log_game_state(card, "Vinta", winning_bid, winner, None)
            self.current_bid=0
            self.highest_bidder = None
            self.turn_number += 1
            return True
        else:
            # Failure! Threshold not met
            print(f"{winner.player_id}'s bid (${winning_bid}) did not meet the heat requirement!")
            print(f"The card {card.card_name} is burned. The budget is not subtracted.")
            #self.burned_cards.append(card)
            self._log_game_state(card, "Bruciata (Soglia Non Raggiunta)", winning_bid, winner, None)
            self.current_bid=0
            self.highest_bidder = None
            self.turn_number += 1
            return False

    def calculate_final_score(self):
        if self.calculate_cooperative_victory():
            self._log_game_state(None, "Cooperative WIN", 0, None, None)
            self._save_log_to_excel()
            return "Cooperative WIN"

        else:
            winner = self.calculate_competitive_victory()
            self._log_game_state(None, winner, 0, None, None)
            self._save_log_to_excel()
            return  winner

    def calculate_cooperative_victory(self):
        print("\n--- Calculating Cooperative Victory (Rule 7) ---")

        counts = {} # e.g.: {Category.ART: {"Human": 2, "Robot": 2}, ...}

        # Initialize counts
        for cat in Category:
            counts[cat] = {self.human.player_id: 0, self.robot.player_id: 0}

        # Count players' cards
        for player in [self.human, self.robot]:
            for cat, card_list in player.cards.items():
                counts[cat][player.player_id] = len(card_list)

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
        winner=None
        if human_score > robot_score:
            winner="Umano"
            print("The Human wins!")
        elif robot_score > human_score:
            winner="Robot"
            print("The Robot wins!")
        else:
            winner = "Pareggio"
            print("It's a draw!")
        return winner


    def _log_game_state(self, card: Card, azione: str, current_bid: int, highest_bidder: Player, player_che_agisce: Player):
        """
        Raccoglie lo stato attuale del gioco e lo aggiunge a self.log_data.
        Questa funzione ora registra OGNI mossa.
        """
        self.log_entry_counter += 1

        human_cards = self.human.count_by_category()
        robot_cards = self.robot.count_by_category()

        # Crea un dizionario (una "riga" del nostro Excel)
        log_row = {
            "Log_ID": self.log_entry_counter,
            "Asta_Num": self.turn_number,
            "Carta_Asta": card.card_name if card else "Nessuna" ,
            "Categoria": card.category_name.value if card else "Nessuna",
            "Player_Azione": player_che_agisce.player_id if player_che_agisce else "Sistema",
            "Azione": azione,
            "Offerta_Corrente": current_bid,
            "Miglior_Offerente": highest_bidder.player_id if highest_bidder else "Nessuno",
            "Budget_Umano": self.human.budget,
            "Budget_Robot": self.robot.budget,
            "Umano_Passato": self.human.has_passed,
            "Robot_Passato": self.robot.has_passed,
            "Arte_Umano": human_cards.get(Category.ART, 0),
            "Tecnologia_Umano": human_cards.get(Category.TECHNOLOGY, 0),
            "Reliquie_Umano": human_cards.get(Category.RELIC, 0),
            "Punti_Umano": self.human.calculate_victory_points(),
            "Arte_Robot": robot_cards.get(Category.ART, 0),
            "Tecnologia_Robot": robot_cards.get(Category.TECHNOLOGY, 0),
            "Reliquie_Robot": robot_cards.get(Category.RELIC, 0),
            "Punti_Robot": self.robot.calculate_victory_points(),
            "Carte_Mazzo": len(self.deck)
        }

        self.log_data.append(log_row)

    def _save_log_to_excel(self):
        """
        Converte self.log_data in un DataFrame e lo salva in un file Excel.
        """
        print(f"\nSalvataggio log di partita in 'game_log_dettagliato.xlsx'...")
        if not self.log_data:
            print("Nessun dato da loggare.")
            return

        base_dir = os.path.dirname(__file__)
        full_path = os.path.join(base_dir, "..", "util", "user_number.txt")
        full_path = os.path.abspath(full_path)
        print(full_path)
        self.run_number = self.get_current_run_number(full_path)
        # Formatta il numero con zeri (es. 1 -> "001", 12 -> "012")
        run_number_str = str(self.run_number).zfill(3)
        # Questo sarà il nome della cartella (es. "Partita_001")
        self.output_folder = f"plot/Partita_{run_number_str}"

        try:
            os.makedirs(self.output_folder, exist_ok=True)
            print(f"Log salvati in: {self.output_folder}")
        except OSError as e:
            print(f"ERRORE: Impossibile creare la cartella {self.output_folder}: {e}")
            # Se non può creare la cartella, salva nella cartella principale
            self.output_folder = "."

        full_excel_path = os.path.join(self.output_folder)

        # 4. INCREMENTA IL COUNTER PER LA PROSSIMA VOLTA
        self.increment_run_number(full_path, self.run_number)

        try:
            df = pd.DataFrame(self.log_data)

            # Imposta le colonne nell'ordine desiderato
            colonne_ordinate = [
                "Log_ID", "Asta_Num", "Carta_Asta", "Categoria", "Player_Azione", "Azione",
                "Offerta_Corrente", "Miglior_Offerente", "Budget_Umano", "Budget_Robot",
                "Umano_Passato", "Robot_Passato",
                "Arte_Umano", "Tecnologia_Umano", "Reliquie_Umano", "Punti_Umano",
                "Arte_Robot", "Tecnologia_Robot", "Reliquie_Robot", "Punti_Robot",
                "Carte_Mazzo"
            ]
            # Aggiungi eventuali colonne mancanti (sebbene non dovrebbe succedere)
            for col in colonne_ordinate:
                if col not in df.columns:
                    df[col] = None

            df = df[colonne_ordinate] # Riordina

            df.to_excel(full_excel_path+"/game_log_dettagliato.xlsx", index=False, sheet_name="Log Aste Dettagliato")
            print("Log salvato con successo.")
        except Exception as e:
            print(f"Errore durante il salvataggio del log: {e}")


    def get_current_run_number(self, file_path):
        """Legge il numero di run attuale dal file counter."""
        try:
            with open(file_path, "r") as f:
                content = f.read().strip() # .strip() rimuove spazi/a capo
                if content:
                    return int(content)
                return 1 # Il file è vuoto, inizia da 1
        except (FileNotFoundError, ValueError):
            # File non trovato o contenuto non valido (es. "abc")
            return 1 # Inizia da 1

    def increment_run_number(self, file_path, current_number):
        """Incrementa e salva il numero per la prossima run."""
        next_number = current_number + 1
        try:
            with open(file_path, "w") as f:
                f.write(str(next_number))
        except IOError as e:
            # Gestisce errori se il file è bloccato, ecc.
            print(f"ATTENZIONE: Impossibile aggiornare il file counter {file_path}: {e}")