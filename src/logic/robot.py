from card import *
from logic.game_manager import GameManager
from player import Player
from behaviors.collaborative_behavior import CollaborativeBehavior
from behaviors.competitive_behavior import CompetitiveBehavior

import argparse
import qi

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

        data_file = GameManager.get_from_json_file("pepper_config.json")
        ROBOT_IP = data_file['ip'] 
        PORT = data_file['port']

        parser = argparse.ArgumentParser()
        parser.add_argument("--robot", type=str, default="pepper", help="Robot you want to use: pepper or nao.")
        parser.add_argument("--nao_version", type=str, default="v6", help="Version of nao you wish to use.")
        parser.add_argument("--ip", type=str, default=ROBOT_IP, help="Robot IP address.")
        parser.add_argument("--sock", type=str, default="server", help="Robot socket side: server or client.")
        args = parser.parse_args()


        port = str(PORT)
        PATH = ''
        PATH = PATH + '/'
        trial = 10

        session = None
        session = qi.Session()
        try:
            session.connect("tcp://" + args.ip + ":" + port)
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(port) +".\n"
                   "Please check your script arguments. Run with -h option for help.")
            exit(1)

        self.active_behavior=None

        if type_R:
            self.active_behavior = CollaborativeBehavior(session, args.ip, args, port)

        else:
            self.active_behavior = CompetitiveBehavior(session, args.ip, args, port)



    def __repr__(self):
        return (f"Robot('{self.player_id}', Tipologia='{self.type_R}', "
                f"budget={self.budget}, Arte={len(self.cards[Category.ART])}, "
                f"Tecnologia={len(self.cards[Category.TECHNOLOGY])}, "
                f"Reliquie={len(self.cards[Category.RELIC])})")