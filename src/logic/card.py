from enum import Enum

class Category(Enum):
    ART = "Arte"
    TECHNOLOGY = "Tecnologia"
    RELIC = "Reliquia"

class Card:

    """
    Rappresenta una singola carta da gioco con attributi per
    il gameplay, aste e requisiti.
    """
    
    def __init__(self, card_name, img_url, category_name, category_color, victory_points, starting_bid, heat_requirement):
        """
        Inizializza una nuova carta.

        Args:
            card_name (str): Il nome della carta (usato anche per trovare l'immagine).
            victory_points (int): Quanti punti vittoria vale questa carta.
            starting_bid (int): Il costo base o l'offerta minima per l'asta.
            heat_requirement (int): Il livello minimo di 'calore' richiesto 
                                    per ottenere questa carta.
        """
        self.card_name = card_name
        self.img_url = img_url
        self.category_name = category_name
        self.category_color = category_color
        self.victory_points = victory_points
        self.starting_bid = starting_bid
        self.heat_requirement = heat_requirement

    def __repr__(self):
        """
        Fornisce una rappresentazione chiara dell'oggetto
        quando viene stampato (print).
        """
        return (f"Card(name='{self.card_name}', "
                f"category={self.category_name}, "
                f"color={self.category_color}, "
                f"vp={self.victory_points}, "
                f"bid={self.starting_bid}, "
                f"heat_req={self.heat_requirement})")

   