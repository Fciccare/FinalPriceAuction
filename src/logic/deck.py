import random # Necessario per mescolare il mazzo
from .card import Card 
import os
import json
from typing import List

# --- Assumiamo che la classe Card definita prima sia presente ---
# class Card:
#     def __init__(self, card_name, victory_points, starting_bid, heat_requirement):
#         ...
#
#     @classmethod
#     def load_from_json(cls, filepath):
#         ...
# ----------------------------------------------------------------

class Deck:
    """
    Rappresenta un mazzo di carte (oggetti Card).
    Gestisce il mescolamento, la pesca e il conteggio delle carte.
    """
    
    def __init__(self, cards_list: List[Card] = None):
        """
        Inizializza il mazzo.

        Args:
            cards_list (list[Card], optional): 
                Una lista di oggetti Card con cui popolare il mazzo.
                Se None, il mazzo inizia vuoto.
        """
        # Copia difensiva per evitare modifiche esterne
        self.cards: List[Card] = list(cards_list) if cards_list else []

    def __repr__(self) -> str:
        """Rappresentazione testuale del mazzo."""
        return f"<Deck: {len(self.cards)} carte rimanenti>"

    def __len__(self) -> int:
        """Permette di usare len(mio_mazzo)."""
        return len(self.cards)

    def shuffle(self) -> None:
        """Mescola le carte nel mazzo in modo casuale."""
        random.shuffle(self.cards)
        print("Il mazzo è stato mescolato.")

    def draw(self) -> Card:
        """
        Pesca una carta dalla cima del mazzo (ultima della lista).

        Returns:
            Card | None: La carta pescata o None se il mazzo è vuoto.
        """
        if not self.cards:
            print("Il mazzo è vuoto! Impossibile pescare.")
            return None
        return self.cards.pop()

    def add_card(self, card: Card) -> None:
        """
        Aggiunge una singola carta in cima al mazzo.

        Args:
            card (Card): La carta da aggiungere.
        """
        if not isinstance(card, Card):
            raise TypeError("Si possono aggiungere solo oggetti 'Card'.")
        self.cards.append(card)

    @classmethod
    def load_from_json(self, json_name):
        """
        Legge il file JSON e crea oggetti Card.
        """
        deck = Deck()

        base_dir = os.path.dirname(__file__)
        full_path = os.path.join(base_dir, "..", "util", json_name)
        full_path = os.path.abspath(full_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for card_data in data:
                card = Card(
                    card_name=card_data["card_name"],
                    category_name = card_data["category_name"],
                    img_url = card_data["img_url"],
                    category_color = card_data["category_color"],
                    victory_points=card_data["victory_points"],
                    starting_bid=card_data["starting_bid"],
                    heat_requirement=card_data["heat_requirement"]
                )
                deck.cards.append(card)

            return deck
        except FileNotFoundError:
            print(f"Errore: il file '{json_path}' non è stato trovato.")
        except KeyError as e:
            print(f"Errore: manca la chiave {e} nel JSON.")
        except json.JSONDecodeError:
            print(f"Errore: il file '{json_path}' non è un JSON valido.")
