from collections import defaultdict
from .card import Card
from typing import List

class Robot:

    def __init__(self, robot_id, victory_points, starting_budget, type_R, cards_list=None):
        """
        Inizializza un nuovo giocatore.

        Args:
            player_id (str): L'id del giocatore.
            victory_points (int): Quanti punti vittoria vale questa carta.
            starting_bid (int): Il costo base o l'offerta minima per l'asta.
            heat_requirement (int): Il livello minimo di 'calore' richiesto 
                                    per ottenere questa carta.
        """
        self.robot_id = robot_id
        self.victory_points = victory_points
        self.budget = starting_budget
        self.cards: List[Card] = list(cards_list) if cards_list else []
        self.type_R = type_R

    def can_bid(self, amount):
        """Verifica se il giocatore può fare un'offerta."""
        return amount <= self.budget

    def win_card(self, card, cost):
        """
        Aggiorna lo stato del giocatore dopo aver vinto una carta.
        """
        if(card.heat_requirement <= cost):
            self.budget -= cost
            self.cards.append(card)
            return True
        else:
            return False

    #  CALCOLO PUNTEGGIO FINALE
    def calculate_victory_points(self):
        """
        Calcola i punti vittoria totali (solo punti base delle carte).
        """
        return sum(card.victory_points for card in self.cards)

    def count_by_color(self):
        """
        Conta quante carte per colore possiede.
        Assumendo che `card.card_name` contenga una parola che identifica il tipo.
        """
        counts = defaultdict(int)
        for c in self.cards:
            if "Arte" in c.card_name or "Rosso" in c.card_name:
                counts["Rosso"] += 1
            elif "Tecnologia" in c.card_name or "Blu" in c.card_name:
                counts["Blu"] += 1
            elif "Reliquia" in c.card_name or "Verde" in c.card_name:
                counts["Verde"] += 1
        return counts

    def __repr__(self):
        return f"Robot('{self.robot_id}', budget={self.budget}, carte={len(self.cards)})"