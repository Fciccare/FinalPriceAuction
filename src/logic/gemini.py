from google import genai
from prompt_gen import *
import json

class Gemini:
    def __init__(self, model, auction):
        with open("./token.txt") as f:
            self.token = f.readline()
        self.client = genai.Client(api_key=self.token)
        self.model = model
        self.chat = self.client.chats.create(model=self.model)
        self.auction = auction
        self.personalita = "cooperativo e amichevole" if self.auction.modalita_cooperativa else "competitivo e sarcastico"

    def presentation(self):
        # TODO
        response = self.chat.send_message(dialogo_conoscitivo())
        print(response.text)
        while True:
            asd = input("RISPOSTA: ")
            response = self.chat.send_message(asd)
            print(response.text)

    def bid(self, hobbies):
        prompt_turno = generate_prompt_turno(
            tipo_oggetto=self.auction.deck.current_card.category_name,
            valore_pv=self.auction.deck.current_card.victory_points,
            descrizione=self.auction.deck.current_card.card_name,
            offerta_corrente=self.auction.deck.current_bid,
            offerente=self.auction.deck.current_player.player_id,
            base_asta=self.auction.deck.current_card.starting_bid,
            carte_rimanenti=len(self.auction.deck),
            monete_bot=self.auction.robot.budget,
            collezioni_bot=self.auction.robot.cards,
            monete_umano=self.auction.human.budget,
            collezioni_umano=self.auction.human.cards,
            personalita=self.personalita,
            hobby_utente=hobbies
        )
        response = self.chat.send_message(prompt_turno)
        return json.loads(response.text)