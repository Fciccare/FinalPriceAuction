# server.py
from flask import Flask, jsonify, request
from logic.game_manager import GameManager
import os

# read ip from config file
data_file = GameManager.get_from_json_file("config.json")
ip_address = data_file['ip']   


app = Flask(__name__)

# Inizializza il gestore di gioco
# Essendo un Singleton, questo ci darà sempre la stessa istanza
game_manager = GameManager()

@app.route("/", methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    # Un semplice endpoint per verificare che il server sia attivo
    return "Server Aste Bot Attivo!"

@app.route("/game/start", methods=["POST"])
def start_game():
    """
    Inizia una nuova partita.
    JSON Input: {"cooperative": bool, "hobbies": [str, ...]}
    """
    data = request.json
    coop_mode = data.get("cooperative", False)
    hobbies = data.get("hobbies", ["Videogiochi", "Cucina"])
    
    try:
        initial_state = game_manager.start_new_game(coop_mode, hobbies)
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

@app.route("/game/action", methods=["POST"])
def player_action():
    """
    Gestisce l'azione di un giocatore (offerta o passo).
    JSON Input: {"action": "bid", "amount": 100} 
    o 
    JSON Input: {"action": "pass"}
    """
    if not game_manager.is_game_active():
        return jsonify({"error": "Nessuna partita attiva."}), 404

    data = request.json
    action = data.get("action")
    amount = data.get("amount", 0)

    try:
        # Tutta la logica (azione umana + risposta IA) è incapsulata qui
        game_state = game_manager.handle_player_action()
        
        if "error" in game_state:
            return jsonify(game_state), 400
            
        return jsonify(game_state), 200
        
    except Exception as e:
        # Gestisce errori imprevisti durante il turno
        return jsonify({"error": f"Errore critico nel turno: {str(e)}"}), 500


if __name__ == '__main__':
    # Usa la porta definita nell'ambiente, o 5000 come default
    port = int(os.environ.get('PORT', 500)) 
    # 'debug=True' ricarica il server ad ogni modifica
    app.run(host=ip_address, port=port, debug=True)