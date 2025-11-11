import re
from google import genai
from logic.prompt_gen import *
import json
import time

class Gemini:
    def __init__(self, model, auction):
        with open("src/util/token.txt") as f:
            self.token = f.readline()
        self.client = genai.Client(api_key=self.token)
        self.model = model
        self.chat = self.client.chats.create(model=self.model)
        self.auction = auction
        self.personalita = "cooperativo e amichevole" if self.auction.modalita_cooperativa else "competitivo e sarcastico e cattivo"

    def presentation(self):
        # TODO
        response = self.chat.send_message(dialogo_conoscitivo())
        print(response.text)
        while True:
            asd = input("RISPOSTA: ")
            response = self.chat.send_message(asd)
            print(response.text)

    def bid(self, hobbies, retries=3):
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
            hobby_utente=hobbies
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
                time.sleep(1)
                return self.bid(hobbies, retries - 1)
            else:
                print("Errore persistente, ritorno None")
                return None

        except Exception as e:  # cattura errori generici (es. ServerError)
            print(f"Errore durante la comunicazione col modello: {e}")
            if retries > 0:
                print(f"Riprovo... ({retries} tentativi rimasti)")
                time.sleep(2)
                return self.bid(hobbies, retries - 1)
            else:
                print("Errore persistente, ritorno None")
                return None

    # def bid(self, hobbies):
    #     prompt_turno = generate_prompt_turno(
    #         tipo_oggetto=self.auction.deck.current_card.category_name,
    #         valore_pv=self.auction.deck.current_card.victory_points,
    #         descrizione=self.auction.deck.current_card.card_name,
    #         offerta_corrente=self.auction.current_bid,
    #         offerente=self.auction.human.player_id,
    #         base_asta=self.auction.deck.current_card.starting_bid,
    #         carte_rimanenti=len(self.auction.deck),
    #         monete_bot=self.auction.robot.budget,
    #         collezioni_bot=self.auction.robot.cards,
    #         monete_umano=self.auction.human.budget,
    #         collezioni_umano=self.auction.human.cards,
    #         personalita=self.personalita,
    #         hobby_utente=hobbies
    #     )
    #     try:
    #         response = self.chat.send_message(prompt_turno)
    #     except "ServerError":
    #         # return self.bid(hobbies)
    #
    #     match = re.search(r"{.*}", response.text, re.DOTALL)
    #     print(response.text)
    #     try:
    #         json_res = json.loads(match.group())
    #         return json_res
    #     except "JSONDecodeError":
    #         response = self.chat.send_message("Fix your previous answer" + prompt_turno)
    #         match = re.search(r"{.*}", response.text, re.DOTALL)
    #         print(response.text)
    #         json_res = json.loads(match.group())
    #         return json_res


    def turn_result(self, winner, hobbies):
        print(f"The winner is {winner}")
        prompt_fine_turno = crea_prompt_fine_asta(
            winner,
            self.auction.current_bid,
            self.personalita,
            hobbies)
        response = self.chat.send_message(prompt_fine_turno)
        #match = re.search(r"{.*}", response.text, re.DOTALL)
        #json_str = match.group()
        # Rimuove eventuale trailing comma
        #json_str = re.sub(r",\s*}", "}", json_str)
        dialogo = estrai_dialogo(response.text)
        print(response.text)
        return {"Dialogo": dialogo}
