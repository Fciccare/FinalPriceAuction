from .card import *
from .player import Player

class Robot(Player):

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
        super().__init__(robot_id, victory_points, starting_budget, cards_list)
        self.type_R = type_R


    def __repr__(self):
        return (f"Robot('{self.player_id}', Tipologia='{self.type_R}', "
                f"budget={self.budget}, Arte={len(self.cards[Category.ART])}, "
                f"Tecnologia={len(self.cards[Category.TECHNOLOGY])}, "
                f"Reliquie={len(self.cards[Category.RELIC])})")