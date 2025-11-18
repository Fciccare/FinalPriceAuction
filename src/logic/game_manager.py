import json
import os

from auctions import Auctions
from gemini import Gemini
from card import Card, Category
from typing import Dict, Any, Optional
from transcriber import capture_audio

class GameManager:
    """
    Classe Singleton per gestire lo stato di un'unica partita sul server.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Inizializza solo se non è già stato fatto
        if not hasattr(self, 'initialized'):
            self.auction: Optional[Auctions] = None
            self.gemini: Optional[Gemini] = None
            self.hobbies: list[str] = ["Videogiochi", "Cucina"] # Default
            self.current_card: Optional[Card] = None
            self.game_active: bool = False
            self.initialized: bool = True
            self.current_offer: int = 0
            self.ai_dialogue: str = ""
            self.last_auction_result: str = ""
            self.llm_turn: bool = False
            self.human_offer= None
            self.robot_offer= None 

    def start_new_game(self, cooperative: bool = False, user_hobbies: list[str] = None):
        """Inizia una nuova partita, sovrascrivendo quella vecchia."""
        self.auction = Auctions(modalita_cooperativa=cooperative)
        
        # NOTA: gemini.py usa un modello non standard. 
        # Assicurati che "gemini-2.5-flash-lite" sia corretto o sostituiscilo
        # con un modello valido come "gemini-1.5-flash".
        self.gemini = Gemini("gemini-2.5-flash", self.auction) 
        
        self.hobbies = user_hobbies if user_hobbies else self.hobbies
        
        # Pesca la prima carta
        self.auction.deck.draw()
        self.current_card = self.auction.deck.current_card
        
        if self.current_card:
            # Logga l'inizio della prima asta
            self.auction._log_game_state(self.current_card, "Inizio Asta", 0, None, None)
            self.game_active = True
            return self.get_game_state()
        else:
            self.game_active = False
            return {"error": "Mazzo vuoto, impossibile iniziare la partita."}


    def start_new_turn(self):
        """Inizia un nuovo turno pescando una nuova carta."""
        if not self.is_game_active():
            return {"error": "Nessuna partita attiva."}
        
        if self.auction.deck.draw():
            self.current_card = self.auction.deck.current_card
            
            if not self.auction.is_bidding_possible(self.current_card):
                return self._end_game("", "", "Fondi insufficienti per continuare.")
        
            if not self.current_card:
                return {"error": "Mazzo vuoto, impossibile iniziare un nuovo turno."}
            
            # Resetta lo stato per il nuovo turno
            self.auction.human.has_passed = False
            self.auction.robot.has_passed = False
            self.auction.current_player = self.auction.human
            self.auction.current_bid = 0
            self.auction.highest_bidder = None
            
            # Logga l'inizio della nuova asta
            self.auction._log_game_state(self.current_card, "Inizio Turno", 0, None, None)
        else:
            return self._end_game("", "", "Carte terminate.")

    def is_game_active(self) -> bool:
        return self.game_active and self.auction is not None

    def _end_game(self, ai_dialogue: str, auction_result: str, end_message: str = "Partita Terminata.") -> Dict[str, Any]:
        """Funzione helper per terminare la partita e loggare i punteggi."""
        winner = self.auction.calculate_final_score()
        #TODO call Gemini function for end Auction
        final_state = self.get_game_state({
            "message": end_message,
            "ai_dialogue": ai_dialogue,
            "last_auction_result": auction_result,
            "game_over": True,
            "winner": winner
        })
        
        
        return self.get_game_state()

    def player_action(self):
        value = capture_audio()
        if value is None:
            print("TOCCA AL PLAYYERRRR")
            return "Error" , {"error": f"Offerta non valida: Puoi ripetere per favore?"}
        elif value == "PASSO":
            print("PASSOOOOOOOOOO")
            if self.auction.manage_auction(self.current_card, "pass"):
                if self.auction.resolve_auction(self.current_card, self.auction.robot,self.robot_offer):
                    dialogo_robot = self.gemini.turn_result(self.auction.robot.player_id, hobbies=self.hobbies)
                    self.ai_dialogue = dialogo_robot["Dialogo"]
                    self.last_auction_result = f"Vincitore: {self.auction.robot.player_id}"
                    self.start_new_turn()
                    return "", self.get_game_state()
                else:
                    dialogo_robot = self.gemini.turn_result("Burned", hobbies=self.hobbies)
                    self.ai_dialogue = dialogo_robot["Dialogo"]
                    self.last_auction_result = "Carta Bruciata."
                    self.start_new_turn()
                    return "", self.get_game_state()
            else:
                self.llm_turn = True
                return "Robot", self.get_game_state()
        else:
            if not self.auction.can_bid(self.auction.human, self.current_card,self.current_offer):
                return "Error", {"error": "Fondi insufficienti per questa offerta."}
            else:
                if self.auction.manage_auction(self.current_card, value):
                    self.human_offer = value
                    self.current_offer = value
                    self.llm_turn = True
                    return "Robot", self.get_game_state()
                else:
                    return "Error" , {"error": f"Offerta non valida: {value}. Deve essere maggiore di {self.auction.current_bid}."}
                
    def robot_action(self):    
        bid_json = self.gemini.bid(hobbies=self.hobbies)
        self.ai_dialogue = bid_json.get("Dialogo", "...")
        ai_action = bid_json.get("Azione", "PASSO")

        if ai_action == "PASSO":
            if self.auction.manage_auction(self.current_card, "pass"):
                if self.auction.resolve_auction(self.current_card, self.auction.human,self.human_offer):
                    dialogo_robot = self.gemini.turn_result(self.auction.human.player_id, hobbies=self.hobbies)
                    #TODO aggiusta il dialogo
                    self.last_auction_result = f"Vincitore: {self.auction.human.player_id}"
                    self.start_new_turn()
                    return "", self.get_game_state()
                else:
                    dialogo_robot = self.gemini.turn_result("Burned", hobbies=self.hobbies)
                    self.last_auction_result = "Carta Bruciata."
                    self.start_new_turn()
                    return "", self.get_game_state()
        else:
            print(f"Offerta del robot precast: {ai_action}")
            value_bid = int(ai_action)
            print(f"Offerta del robot: {value_bid}")
            if self.auction.manage_auction(self.current_card, value_bid):
                    self.robot_offer = value_bid
                    self.current_offer = value_bid
                    self.llm_turn = False
                    if self.auction.human.has_passed:
                        if self.auction.resolve_auction(self.current_card, self.auction.robot, self.robot_offer):
                            dialogo_robot = self.gemini.turn_result(self.auction.robot.player_id, hobbies=self.hobbies)
                            self.ai_dialogue = dialogo_robot["Dialogo"]
                            self.last_auction_result = f"Vincitore: {self.auction.robot.player_id}"
                            self.start_new_turn()
                            return "", self.get_game_state()
                        else:
                            dialogo_robot = self.gemini.turn_result("Burned", hobbies=self.hobbies)
                            self.ai_dialogue = dialogo_robot["Dialogo"]
                            self.last_auction_result = "Carta Bruciata."
                            self.start_new_turn()
                            return "", self.get_game_state()
                    return "Player", self.get_game_state()
            else:
                return "Error" , {"error": f"Offerta non valida: {value_bid}. Deve essere maggiore di {self.auction.current_bid}."}

    def handle_player_action(self) -> Dict[str, Any]:
        """
        Processa l'azione del giocatore e fa agire l'IA di conseguenza.
        Questa è la logica centrale del turno.
        """
        if not self.is_game_active() or self.auction.current_player != self.auction.human:
            return {"error": "Azione non valida o non è il tuo turno."}

        self.last_auction_result = ""
        self.llm_turn = False
        
        # --- 1. Azione dell'UMANO ---
        state, message = self.player_action()
        if(state == "Error"):
            return message
        elif (state == "Robot"):
            # --- 2. Azione del ROBOT ---
            state_robot , message = self.robot_action()
            if(state_robot == "Error"):
                return message
            elif (state_robot == "Player"):
                return message
            else:
                return message
        else:
            return message
        
    # Helper per convertire le chiavi Enum in stringhe
    def serialize_counts(self, counts_dict):
        return {k.value: v for k, v in counts_dict.items()}


    def get_game_state(self, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Serializza lo stato attuale del gioco in un dizionario JSON-friendly."""
        if not self.is_game_active():
            return {"game_active": False}
        
        state = {
            "game_active": True,
            "game_over": False,
            "winner": None,
            "current_bid": self.auction.current_bid,
            "highest_bidder": self.auction.highest_bidder.player_id if self.auction.highest_bidder else None,
            "current_player_turn": self.auction.current_player.player_id,
            "cards_remaining": len(self.auction.deck),
            "current_card": {
                "name": self.current_card.card_name,
                "img_url": self.current_card.img_url,
                "category": self.current_card.category_name.value,
                "color": self.current_card.category_color,
                "vp": self.current_card.victory_points,
                "starting_bid": self.current_card.starting_bid
            } if self.current_card else None,
            "human": {
                "budget": self.auction.human.budget,
                "vp": self.auction.human.calculate_victory_points(),
                "cards": self.serialize_counts(self.auction.human.count_by_category()),
                "has_passed": self.auction.human.has_passed
            },
            "robot": {
                "budget": self.auction.robot.budget,
                "vp": self.auction.robot.calculate_victory_points(),
                "cards": self.serialize_counts(self.auction.robot.count_by_category()),
                "has_passed": self.auction.robot.has_passed
            },
            "ai_dialogue": self.ai_dialogue,
            "last_auction_result": self.last_auction_result
        }

        if extra_data:
            state.update(extra_data)
            
        return state
    

    @staticmethod
    def get_from_json_file(filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "..", "util", filename)) as configfile:
            data_file = json.load(configfile)

        return data_file