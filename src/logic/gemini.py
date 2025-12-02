import re
from google import genai
from prompt_gen import *
import json
import time
import os
import threading  # Aggiunto per thread-safety


class Gemini:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                # Double-checked locking
                if not cls._instance:
                    cls._instance = super(Gemini, cls).__new__(cls)
        return cls._instance

    def __init__(self, model, auction):
        """
        Inizializza l'istanza solo se non è già stata inizializzata.
        """
        if getattr(self, "_initialized", False):
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(script_dir, "..", "util", "token.txt")

        with open(token_path) as f:
            self.token = f.readline()
        self.client = genai.Client(api_key=self.token)
        self.model = model
        self.chat = self.client.chats.create(model=self.model)
        self.auction = auction
        self.personalita = None
        # Segna l'istanza come inizializzata
        self._initialized = True

    # def presentation(self, message = None):
    #     if message is None:
    #         response = self.chat.send_message(dialogo_conoscitivo())
    #     else:
    #         response = self.chat.send_message(message)

    #     return response

    def set_auction(self, auction):
        self.auction = auction
        self.personalita = "cooperativo e amichevole" if self.auction.modalita_cooperativa else "competitivo e sarcastico e cattivo"

    def name_hobbies(self, name, hobbies, retries=10):
        try:
            response = self.chat.send_message(extract_name_hobbies(name, hobbies))
            match = re.search(r"{.*}", response.text, re.DOTALL)
            if not match:
                raise ValueError("Nessun JSON trovato nella risposta")
            json_res = json.loads(match.group())
            return json_res
        except Exception as e:
            print(f"Errore durante la comunicazione col modello: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(3)
                return self.name_hobbies(name, hobbies, retries - 1)
            else:
                print("Errore persistente, ritorno None")
                return None

    def get_robot_endgame_prompts(self, winner, retries=10):
        try:
            response = self.chat.send_message(get_robot_endgame_prompts(winner, self.personalita))
            match = re.search(r"{.*}", response.text, re.DOTALL)
            if not match:
                raise ValueError("Nessun JSON trovato nella risposta")
            json_res = json.loads(match.group())
            return json_res
        except Exception as e:
            print(f"Errore durante la comunicazione col modello: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(3)
                return self.get_robot_endgame_prompts(winner, retries - 1)
            else:
                print("Errore persistente, ritorno None")
                return None

    def bid(self, hobbies, name, user_messages, retries=10):
        prompt_turno = generate_prompt_turno(
            tipo_oggetto=self.auction.deck.current_card.category_name,
            valore_pv=self.auction.deck.current_card.victory_points,
            descrizione=self.auction.deck.current_card.card_name,
            offerta_corrente=self.auction.current_bid,
            offerente=self.auction.human.player_id,
            base_asta=self.auction.deck.current_card.starting_bid,
            carte_rimanenti=len(self.auction.deck),
            monete_bot=self.auction.robot.budget,
            collezioni_bot=self.auction.robot.cards,
            monete_umano=self.auction.human.budget,
            collezioni_umano=self.auction.human.cards,
            personalita=self.personalita,
            hobby_utente=hobbies,
            user_name=name,
            user_message=user_messages
        )

        try:
            response = self.chat.send_message(prompt_turno)
            print("Risposta del modello:", response.text)

            match = re.search(r"{.*}", response.text, re.DOTALL)
            if not match:
                raise ValueError("Nessun JSON trovato nella risposta")

            json_res = json.loads(match.group())
            return json_res

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Errore JSON o risposta non valida: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(3)
                return self.bid(hobbies, name, user_messages,
                                retries - 1)  # Corretto: aggiunti argomenti mancanti nella ricorsione
            else:
                print("Errore persistente, ritorno None")
                return None

        except Exception as e:
            print(f"Errore durante la comunicazione col modello: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(3)
                return self.bid(hobbies, name, user_messages,
                                retries - 1)  # Corretto: aggiunti argomenti mancanti nella ricorsione
            else:
                print("Errore persistente, ritorno None")
                return None

    def turn_result(self, winner, hobbies, retries=10):
        try:
            print(f"The winner is {winner}")
            prompt_fine_turno = crea_prompt_fine_asta(
                winner,
                self.auction.current_bid,
                self.personalita,
                hobbies)
            response = self.chat.send_message(prompt_fine_turno)

            dialogo = estrai_dialogo(response.text)
            print(response.text)
            return {"Dialogo": dialogo}
        except Exception as e:
            print(f"Errore durante la comunicazione col modello: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(3)
                return self.turn_result(winner, hobbies, retries - 1)  # Corretto: chiamata ricorsiva al metodo giusto
            else:
                print("Errore persistente, ritorno None")
                return None