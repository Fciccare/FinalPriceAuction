from .card import Card, Category
from typing import List,Dict


class Player:

    def __init__(self, player_id, victory_points, starting_budget, cards_list=None):
        """
        Inizializza un nuovo giocatore.

        Args:
            player_id (str): L'id del giocatore.
            victory_points (int): Quanti punti vittoria vale questa carta.
            starting_bid (int): Il costo base o l'offerta minima per l'asta.
            heat_requirement (int): Il livello minimo di 'calore' richiesto 
                                    per ottenere questa carta.
        """
        self.player_id = player_id
        self.victory_points = victory_points
        self.budget = starting_budget
        self.has_passed = False
        if cards_list:
            self.cards: Dict[str, List[Card]] = cards_list
        else:
            self.cards = {
                Category.ART: [],
                Category.TECHNOLOGY: [],
                Category.RELIC: []
            }

    def can_bid(self, amount):
        """Verifica se il giocatore può fare un'offerta."""
        return amount <= self.budget

    def win_card(self, card : Card, cost):
        """
        Aggiorna lo stato del giocatore dopo aver vinto una carta.
        """
        self.budget -= cost

        if Category.ART == card.category_name:
            self.cards[Category.ART].append(card)
        elif Category.TECHNOLOGY == card.category_name :
            self.cards[Category.TECHNOLOGY].append(card)
        elif Category.RELIC == card.category_name:
                self.cards[Category.RELIC].append(card)

    #  CALCOLO PUNTEGGIO FINALE
    def calculate_victory_points(self):
        """
        Calcola i punti vittoria totali (solo punti base delle carte).
        """
        total = 0
        for group in self.cards.values():
            total += sum(card.victory_points for card in group)
        return total
    
    def count_by_category(self):
        """
        Conta quante carte per colore possiede.
        Assumendo che `card.card_name` contenga una parola che identifica il tipo.
        """
        return {k: len(v) for k, v in self.cards.items()}

    def __repr__(self):
        return (f"Player('{self.player_id}', budget={self.budget}, "
                f"Arte={len(self.cards[Category.ART])}, "
                f"Tecnologia={len(self.cards[Category.TECHNOLOGY])}, "
                f"Reliquie={len(self.cards[Category.RELIC])})")
    