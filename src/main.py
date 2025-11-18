from PIL import Image
from streamlit import session_state
from torchaudio.io import play_audio

from logic.gemini import *
import streamlit as st
from logic.card import *
from logic.auctions import Auctions
from logic.transcriber import *

import os 
import nest_asyncio

nest_asyncio.apply()

# --- CONFIGURAZIONE BASE ---
st.set_page_config(page_title="Asta tra due utenti", layout="wide")

#capture_audio()

# def run_async(coro):
#     try:
#         loop = asyncio.get_running_loop()
#         # Siamo già dentro un event loop → usiamo create_task
#         return loop.create_task(coro)
#     except RuntimeError:
#         # Nessun event loop attivo → creiamone uno temporaneo
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         return loop.run_until_complete(coro)

st.html('''
<style>
video::-webkit-media-controls {
    display: none !important;
}
video::-webkit-media-controls-panel {
    display: none !important;
}
video::-webkit-media-controls-play-button {
    display: none !important;
}
</style>
''')

def final_round():
    if not st.session_state.auction.is_bidding_possible(st.session_state.card):
        st.session_state.winner = st.session_state.auction.calculate_final_score()
        
    st.session_state.deck.draw()
    st.session_state.card = st.session_state.deck.current_card
    st.session_state.carte_rimaste = len(st.session_state.deck)
    st.session_state.asta_current = 0
    st.session_state.robot.has_passed = False
    st.session_state.human.has_passed = False
    st.session_state.auction.current_player = st.session_state.human
    st.session_state.auction.current_bid = 0
    st.session_state.auction.highest_bidder = None
    st.session_state.offerta_utente1=0
    st.session_state.offerta_utente2=0


import time
@st.dialog("FinalPriceAuction")
def dialog_show(text, gif_path="", timer=2.5):
    st.write(f"# {text}")
    if not gif_path == "":
        st.image(gif_path)
        time.sleep(timer)
        final_round()
        st.rerun()
    else:
        if st.button("ok"):
            final_round()
            st.rerun()


@st.dialog("FinalPriceAuction")
def dialog_show_webm(text, webm="", timer=2.5):
    st.write(f"# {text}")
    if not webm == "":
        st.video(webm, loop=True, autoplay=True)
        time.sleep(timer)
        final_round()
        st.rerun()
    else:
        if st.button("ok"):
            final_round()
            st.rerun()

@st.dialog("FinalPriceAuction", dismissible=False)
def final_dialog(text, webm=""):
    st.write(f"# {text}")
    if not webm == "":
        st.video(webm, loop=True, autoplay=True)

def player_play():
    #result = asyncio.create_task(test_async())
    #dialog_show_webm("Parla ora dopo il beep!", "src/util/webm/burned.webm" ,timer=8)
    
    with st.spinner("Wait for it...", show_time=True):        
        value = capture_audio()
    print(f"Sono state puntate {value} monete")

    if value is None:
        print("Ripeti")
        #player_play()
    elif value == "PASSO":
        if st.session_state.auction.manage_auction(st.session_state.card, "pass"):
            if st.session_state.auction.resolve_auction(st.session_state.card, st.session_state.robot,
                                                        st.session_state.offerta_utente2):
                dialogo_robot = st.session_state.gemini.turn_result(st.session_state.auction.robot.player_id,
                                                                    hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("Il Robot ha vinto una carta", "src/util/webm/robot_win.webm")

            else:
                dialogo_robot = st.session_state.gemini.turn_result("Burned", hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("La Carta è stata bruciata", "src/util/webm/burned.webm")
    else:
        if not st.session_state.auction.can_bid(st.session_state.human, st.session_state.card,
                                                st.session_state.asta_current):
            print("NON PUOI BIDDARE QUESTA CIFRA")
        else:
            offerta1 = value
            if st.session_state.auction.manage_auction(st.session_state.card, offerta1):
                st.session_state.offerta_utente1 = offerta1
                st.session_state.asta_current = offerta1
                st.success(f"Hai offerto €{offerta1}")
                st.session_state.llm_turn = True
                st.rerun()
            else:
                st.warning("L'offerta non è valida", icon="⚠️")


if "winner" in st.session_state:
    winner = st.session_state.winner
    if winner=="Cooperative WIN":
        final_dialog("Avete vinto entambi collaborando", "src/util/webm/both_winner.webm")
    elif winner=="Pareggio":
        final_dialog("Avete pareggiato")
    elif winner=="Umano":
        final_dialog("Hai vinto la partita", "src/util/webm/player_winner.webm")
    elif winner=="Robot":
        final_dialog("Ha vinto il robot", "src/util/webm/robot_winner.webm")

if "initialized" not in st.session_state:
    st.session_state.initialized = True

    if "player_start" not in st.session_state:
        st.session_state.player_start = False

    if "testo_robot" not in session_state:
        st.session_state.testo_robot = "Ma che bel testolino marcodirondondello🤣🤣🤣"

    if "auction" not in st.session_state:
        st.session_state.auction = Auctions(modalita_cooperativa=False)

    if "llm_turn" not in st.session_state:
        st.session_state.llm_turn = False

    if "gemini" not in st.session_state:
        st.session_state.gemini = Gemini("gemini-2.5-flash-lite", st.session_state.auction)

    if "player" not in st.session_state:
        st.session_state.human = st.session_state.auction.human

    if "robot" not in st.session_state:
        st.session_state.robot = st.session_state.auction.robot

    if "deck" not in st.session_state:
        st.session_state.deck = st.session_state.auction.deck
        st.session_state.deck.draw()

    if "hobbies" not in st.session_state:
        st.session_state.hobbies = ["Pokemon", "Judo", "MMA", "Brainrot"]

    if "card" not in st.session_state:
        st.session_state.card = st.session_state.deck.current_card
        st.session_state.auction._log_game_state(st.session_state.card, "Inizio Asta", 0, None, None)
        if not st.session_state.auction.is_bidding_possible(st.session_state.card):
            print(st.session_state.auction.calculate_final_score())
            #TODO ANIMAZIONI


    print(st.session_state.deck.current_card)


# --- INIZIALIZZAZIONE DELLO STATO ---



if "offerta_utente1" not in st.session_state:
    st.session_state.offerta_utente1 = 0
if "offerta_utente2" not in st.session_state:
    st.session_state.offerta_utente2 = 0
if "vincitore" not in st.session_state:
    st.session_state.vincitore = None

if "minimo_asta" not in st.session_state:
    st.session_state.minimo_asta = st.session_state.deck.current_card.starting_bid  # base d'asta

if "asta_current" not in st.session_state:
    st.session_state.asta_current = 0

if "carte_rimaste" not in st.session_state:
    st.session_state.carte_rimaste = len(st.session_state.deck)
if "crediti_utente1" not in st.session_state:
    st.session_state.crediti_utente1 = st.session_state.human.budget
if "crediti_utente2" not in st.session_state:
    st.session_state.crediti_utente2 = st.session_state.robot.budget

#TODO: Passare a current_player?
if st.session_state.llm_turn:
    print("LLM TURN ATTIVO")
    st.session_state.llm_turn = False

    bid = st.session_state.gemini.bid(hobbies=st.session_state.hobbies)
    st.session_state.testo_robot = bid["Dialogo"]
    if bid["Azione"] == "PASSO":
        if st.session_state.auction.manage_auction(st.session_state.card, "pass"):
            if st.session_state.auction.resolve_auction(st.session_state.card, st.session_state.human,
                                                        st.session_state.offerta_utente1):
                # TODO CHIAMARE POP VITTORIA
                dialogo_robot = st.session_state.gemini.turn_result(st.session_state.auction.human.player_id, hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("Hai vinto una carta", "src/util/webm/player_win.webm")
                #pass
            else:
                # TODO CHIAMARE POP BRUCIATA
                dialogo_robot = st.session_state.gemini.turn_result("Burned", hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("La Carta è stata bruciata", "src/util/webm/burned.webm")
                #pass
    else:
        value_bid = int(bid["Azione"])
        if st.session_state.auction.manage_auction(st.session_state.card, value_bid):
                st.session_state.offerta_utente2 = value_bid
                st.session_state.asta_current = value_bid
                st.success(f"Hai offerto €{value_bid}")
    st.rerun()
# elif st.session_state.player_start:
#     run_async(player_play())


#print(st.session_state.player_start)

# --- LAYOUT A TRE COLONNE ---
col1, col2, col3 = st.columns([1, 2, 1])

# --- COLONNA SINISTRA: MAZZO DI CARTE ---
with col1:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h3>🂠 Carte rimaste: {st.session_state.carte_rimaste}</h3>
            <img src="https://i.ibb.co/x9PZS8W/back-card.png"
                 width="200" style="margin-top: 10px;">
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- COLONNA CENTRALE: CARTA IN ASTA ---
# --- COLONNA CENTRALE: CARTA IN ASTA + BOX ASTA CORRENTE ---
with col2:
    st.markdown(
        """
        <style>
        .card-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .card-box {
            width: 300px; /* stessa larghezza dell'immagine */
            text-align: center;
            background-color: var(--background-color-secondary);
            color: var(--text-color);
            padding: 12px;
            border-radius: 10px;
            box-shadow: 0 0 8px rgba(0,0,0,0.15);
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img = Image.open(os.path.join(script_dir, "util", st.session_state.deck.current_card.img_url.lstrip('/\\')))

    #img = Image.open(f"src/util/{st.session_state.deck.current_card.img_url}")

    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.image(img, width=380, caption=st.session_state.deck.current_card.card_name)
    st.markdown(
        f"""
        <div class="card-box">
            <h4 style="margin: 0;">💰 Puntata Minima: {st.session_state.deck.current_card.starting_bid}</h4>
            <h4 style="margin: 0;">💰 Puntata Corrente: {st.session_state.asta_current}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLONNA DESTRA: INFO ASTA ---
with col3:
    st.markdown("### 👥 Giocatori")

    st.markdown(
        f"""
        <style>
        .player-box {{
            background-color: var(--background-color-secondary);
            color: var(--text-color);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 0 8px rgba(0,0,0,0.15);
        }}
        .player-header {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .stats-container {{
            display: flex;
            justify-content: space-around;
            text-align: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .stat-block {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .stat-value {{
            font-size: 1.6rem;
            font-weight: bold;
            line-height: 1.2;
        }}
        .stat-label {{
            font-size: 0.85rem;
            opacity: 0.8;
        }}
        .cards-container {{
            display: flex;
            justify-content: space-around;
            text-align: center;
            gap: 8px;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 8px;
        }}
        .card-block {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .card-value {{
            font-size: 1.2rem;
            font-weight: bold;
            line-height: 1.1;
        }}
        .card-label {{
            font-size: 0.8rem;
            opacity: 0.7;
        }}
        </style>

        <div class="player-box">
            <div class="player-header">🧍 Giocatore 1</div>
            <div class="stats-container">
                <div class="stat-block">
                    <div class="stat-value">€{st.session_state.human.budget}</div>
                    <div class="stat-label">Crediti</div>
                </div>
                <div class="stat-block">
                    <div class="stat-value">{st.session_state.human.calculate_victory_points()}</div>
                    <div class="stat-label">Punteggio</div>
                </div>
            </div>
            <div class="cards-container">
                <div class="card-block">
                    <div class="card-value">{st.session_state.human.count_by_category()[Category.ART]}</div>
                    <div class="card-label">Arte</div>
                </div>
                <div class="card-block">
                    <div class="card-value">{st.session_state.human.count_by_category()[Category.RELIC]}</div>
                    <div class="card-label">Reliquia</div>
                </div>
                <div class="card-block">
                    <div class="card-value">{st.session_state.human.count_by_category()[Category.TECHNOLOGY]}</div>
                    <div class="card-label">Tecnologia</div>
                </div>
            </div>
        </div>

        <div class="player-box">
            <div class="player-header">🤖 Robot</div>
            <div class="stats-container">
                <div class="stat-block">
                    <div class="stat-value">€{st.session_state.robot.budget}</div>
                    <div class="stat-label">Crediti</div>
                </div>
                <div class="stat-block">
                    <div class="stat-value">{st.session_state.robot.calculate_victory_points()}</div>
                    <div class="stat-label">Punteggio</div>
                </div>
            </div>
            <div class="cards-container">
                <div class="card-block">
                    <div class="card-value">{st.session_state.robot.count_by_category()[Category.ART]}</div>
                    <div class="card-label">Arte</div>
                </div>
                <div class="card-block">
                    <div class="card-value">{st.session_state.robot.count_by_category()[Category.RELIC]}</div>
                    <div class="card-label">Reliquia</div>
                </div>
                <div class="card-block">
                    <div class="card-value">{st.session_state.robot.count_by_category()[Category.TECHNOLOGY]}</div>
                    <div class="card-label">Tecnologia</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




# st.markdown("---")
# if st.button("Start a game"):
#     st.session_state.player_start = True
#     #run_async(player_play())

# --- SEZIONE UTENTE 1 ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("👤 Utente 1")
    if not st.session_state.auction.can_bid(st.session_state.human, st.session_state.card, st.session_state.asta_current):
        pass 
    else:
        offerta1 = st.number_input("Inserisci la tua offerta (€)", min_value=0, key="input1")
        if st.button("Offri come Utente 1", 1):
            if st.session_state.auction.manage_auction(st.session_state.card, offerta1):
                st.session_state.offerta_utente1 = offerta1
                st.session_state.asta_current = offerta1
                st.success(f"Hai offerto €{offerta1}")
                st.session_state.llm_turn = True
                st.rerun()
            else:
                st.warning("L'offerta non è valida", icon="⚠️")

    if st.button("Passa Utente 1", 2):
        if st.session_state.auction.manage_auction(st.session_state.card, "pass"):
            if st.session_state.auction.resolve_auction(st.session_state.card, st.session_state.robot, st.session_state.offerta_utente2):
                dialogo_robot=st.session_state.gemini.turn_result(st.session_state.auction.robot.player_id, hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("Il Robot ha vinto una carta", "src/util/webm/robot_win.webm")
                
            else:
                dialogo_robot=st.session_state.gemini.turn_result("Burned", hobbies=st.session_state.hobbies)
                st.session_state.testo_robot = dialogo_robot["Dialogo"]
                dialog_show_webm("La Carta è stata bruciata", "src/util/webm/burned.webm")
                


with col2:
    st.subheader("🤖Robot")
    st.header(st.session_state.testo_robot)



st.markdown("---")

import streamlit as st

st.markdown("""
    <style>
    .big-button {
        display: block;
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 20px 40px;
        font-size: 24px;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        text-align: center;
        transition: 0.3s;
    }
    .big-button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Crea il bottone con HTML
# if st.markdown('<button class="big-button">🎤Premi per parlare</button>', unsafe_allow_html=True):
#     st.session_state.player_start = True
#     player_play()


if st.button("🎤Premi per parlare"):
    player_play()

