from ipaddress import ip_address

from flask import Flask, jsonify, request
from game_manager import GameManager
from flask_cors import CORS, cross_origin
import os
import traceback

import argparse
import qi
import threading
from behaviors.collaborative_behavior import CollaborativeBehavior
from behaviors.competitive_behavior import CompetitiveBehavior

from transcriber import load_model

session = None
print("Agg mis a Noneeeeee")

if session is None:
    print("Sono entrato nella session!!!!!!!!!!!")
    load_model()
    active_behavior = None
    data_file = GameManager.get_from_json_file("pepper_config.json")
    ROBOT_IP = data_file['ip']
    PORT = data_file['port']
    print("ip Robot: ", ROBOT_IP)
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", type=str, default="pepper", help="Robot you want to use: pepper or nao.")
    parser.add_argument("--nao_version", type=str, default="v6", help="Version of nao you wish to use.")
    parser.add_argument("--ip", type=str, default=ROBOT_IP, help="Robot IP address.")
    parser.add_argument("--sock", type=str, default="server", help="Robot socket side: server or client.")
    parser.add_argument("--coop", action="store_true", help="If set, robot is cooperative")  # flag booleano
    args = parser.parse_args()
    coop_mode = args.coop

    try:
        port = str(PORT)
        PATH = '/Users/lucarag/work/unina'
        PATH = PATH + '/'
        trial = 10

        session = None
        session = qi.Session()
        try:
            session.connect("tcp://" + args.ip + ":" + port)
        except RuntimeError:
            print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(port) + ".\n"
                                                                                            "Please check your script arguments. Run with -h option for help.")
            exit(1)


        if coop_mode:
            active_behavior = CollaborativeBehavior(session, args.ip, args, port)
        else:
            active_behavior = CompetitiveBehavior(session, args.ip, args, port)

        if active_behavior.autonomus.getState != "disabled":
            active_behavior.autonomus.setState("disabled")
        active_behavior.stand_up()
        tracking_thread = threading.Thread(
            target=active_behavior.start_tracking,
            args=(False,),  # Argomenti da passare a _tracking_loop
            daemon=True
        )

        # Avviamo il thread. Questo NON blocca.
        tracking_thread.start()

    except RuntimeError:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(port) + ".\n" + "Please check your script arguments. Run with -h option for help.")



#######################################################################################################################

# read ip from config file
data_file = GameManager.get_from_json_file("config.json")
ip_address = data_file['ip']
port = data_file['port']#


app = Flask(__name__)
cors = CORS(app)

# Inizializza il gestore di gioco
# Essendo un Singleton, questo ci darà sempre la stessa istanza
game_manager = GameManager()
# game_manager = None

@app.route("/", methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    # Un semplice endpoint per verificare che il server sia attivo
    return "Server Aste Bot Attivo!"

@app.route("/game/start", methods=["GET"])
def start_game():
    """
    Inizia una nuova partita.
    JSON Input: {"cooperative": bool, "hobbies": [str, ...]}
    """
    #data = request.json
    #coop_mode = data.get("cooperative", False)
    #hobbies = data.get("hobbies", ["Videogiochi", "Cucina"])

    hobbies = game_manager.get_hobbies(active_behavior)
    try:
        initial_state = game_manager.start_new_game(coop_mode, hobbies, active_behavior)
        if "error" in initial_state:
            return jsonify(initial_state), 400
        
        return jsonify(initial_state), 201 # 201 Created
    except Exception as e:
        return jsonify({"error": f"Errore critico nell'avvio: {str(e)}"}), 500

@app.route("/game/state", methods=["GET"])
def get_game_state():
    """
    Restituisce lo stato attuale della partita.
    """
    if not game_manager.is_game_active():
        return jsonify({"game_active": False, "message": "Nessuna partita attiva. Avviala con POST /game/start"}), 404
        
    return jsonify(game_manager.get_game_state())

@app.route("/game/action", methods=["GET"])
def player_action():
    """
    Gestisce l'azione di un giocatore (offerta o passo).
    JSON Input: {"action": "bid", "amount": 100} 
    o 
    JSON Input: {"action": "pass"}
    """
    if not game_manager.is_game_active():
        return jsonify({"error": "Nessuna partita attiva."}), 404

    #data = request.json
    #action = data.get("action")
    #amount = data.get("amount", 0)

    try:
        # Tutta la logica (azione umana + risposta IA) è incapsulata qui
        game_state = game_manager.handle_player_action()
        
        if "error" in game_state:
            return jsonify(game_state), 400
            
        return jsonify(game_state), 200
        
    except Exception as e:
        # Gestisce errori imprevisti durante il turno
        print(traceback.format_exc())
        return jsonify({"error": f"Errore critico nel turno: {str(e)}"}), 500


if __name__ == '__main__':
    # Usa la porta definita nell'ambiente, o 5000 come default
    #port = int(os.environ.get('PORT', 500)) 
    port = 5000
    # 'debug=True' ricarica il server ad ogni modifica
    app.run(host=ip_address, port=port)