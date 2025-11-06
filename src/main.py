import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

from logic.deck import Deck
from logic.player import Player
from logic.robot import Robot

from logic.card import *

#st.title('Uber pickups in NYC')

#filename="main.py"
#import os
#import subprocess
#subprocess.Popen(["streamlit", "run", filename, os.devnull])
import streamlit as st
import streamlit_shadcn_ui as ui

from logic.auctions import Auctions

# --- CONFIGURAZIONE BASE ---
st.set_page_config(page_title="Asta tra due utenti", layout="wide")


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
    
        #print(winner)
        #final_dialog(winner)
        #st.write(f"# {winner}")


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


@st.dialog("FinalPriceAuction", dismissible=False)
def final_dialog(text, gif_path="", timer=2.5):
    st.write(f"# {text}")
    if not gif_path == "":
        st.image(gif_path)



# st.markdown("""
#     <style>
#     /* Sfondo principale della pagina */
#     .stApp {
#         background-color: #F2F2F7;  /* grigio neutro chiaro */
#     }

#     /* Box e container interni */
#     [data-testid="stVerticalBlock"] {
#         background-color: transparent !important;
#     }

#     /* Testo sempre visibile su sfondo neutro */
#     h1, h2, h3, h4, h5, h6, p, span, div {
#         color: #1E1E1E !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

#st.title("🃏 Asta per una Carta")


if "initialized" not in st.session_state:
    st.session_state.initialized = True

    if "auction" not in st.session_state:
        st.session_state.auction = Auctions()

    if "player" not in st.session_state:
        # st.session_state.player = Player("Umano", 0 , 1000)
        st.session_state.human = st.session_state.auction.human

    if "robot" not in st.session_state:
        # st.session_state.robot = Robot("Robot", 0 , 1000, "competitive")
        st.session_state.robot = st.session_state.auction.robot

    if "deck" not in st.session_state:
        # deck = Deck.load_from_json("deck_1.json")
        # deck.shuffle()
        # st.session_state.deck = deck
        # st.session_state.deck.draw()
        st.session_state.deck = st.session_state.auction.deck
        st.session_state.deck.draw()

    if "card" not in st.session_state:
        st.session_state.card = st.session_state.deck.current_card
        st.session_state.auction._log_game_state(st.session_state.card, "Inizio Asta", 0, None, None)
        if not st.session_state.auction.is_bidding_possible(st.session_state.card):
            print(st.session_state.auction.calculate_final_score())
            #TODO ANIMAZIONI

    print(st.session_state.deck.current_card)
    #start_game()

print({st.session_state.human.count_by_category()[Category.ART]})

# --- INIZIALIZZAZIONE DELLO STATO ---

if "winner" in st.session_state:
    final_dialog("Vittoria di qualcuno")

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

    img = Image.open(f"src/util/{st.session_state.deck.current_card.img_url}")

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


# st.markdown(
#         f"""
#         <style>
#         .player-box {{
#             background-color: var(--background-color-secondary);
#             color: var(--text-color);
#             padding: 15px;
#             border-radius: 10px;
#             margin-bottom: 10px;
#             box-shadow: 0 0 8px rgba(0,0,0,0.15);
#         }}
#         .stat-line {{
#             margin: 3px 0;
#         }}
#         </style>

#         <div class="player-box">
#             <h4 style="margin: 0;">Puntata Corrente: {5}💰</h4>
#         </div>""",
#         unsafe_allow_html=True,
#     )

st.markdown("---")

# --- SEZIONE UTENTE 1 ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("👤 Utente 1")
    if not st.session_state.auction.can_bid(st.session_state.human, st.session_state.card, st.session_state.asta_current):
        pass #can bid is false # TODO STUT O PULSANT BUCCHI
    else:
        offerta1 = st.number_input("Inserisci la tua offerta (€)", min_value=0, key="input1")
        if st.button("Offri come Utente 1", 1):
            if st.session_state.auction.manage_auction(st.session_state.card, offerta1):
                st.session_state.offerta_utente1 = offerta1
                st.session_state.asta_current = offerta1
                st.success(f"Hai offerto €{offerta1}")
                st.rerun()
            else:
                # st.error("L'offerta deve essere superiore al minimo e all'altra offerta.")
                st.warning("L'offerta non è valida", icon="⚠️")

    if st.button("Passa Utente 1", 2):
        if st.session_state.auction.manage_auction(st.session_state.card, "pass"):
            if st.session_state.auction.resolve_auction(st.session_state.card, st.session_state.robot, st.session_state.offerta_utente2):
                # TODO CHIAMARE POP VITTORIA
              # TODO CHIAMARE POP VITTORIA
                dialog_show("Carta Vinta", "src/util/gif/robot_win.gif")
                #pass
            else:
                # TODO CHIAMARE POP BRUCIATA
                dialog_show("Carta Bruciata", "src/util/gif/burned.gif")
                #pass

        # st.session_state.deck.draw()
        # st.session_state.card = st.session_state.deck.current_card
        # st.session_state.carte_rimaste = len(st.session_state.deck)
        # st.session_state.asta_current = 0
        # st.session_state.robot.has_passed = False
        # st.session_state.human.has_passed = False
        # st.session_state.auction.current_player = st.session_state.human
        # if not st.session_state.auction.is_bidding_possible(st.session_state.card):
        #      print(st.session_state.auction.calculate_final_score())
        #     # TODO ANIMAZIONI

        # st.rerun()
        #print(st.session_state.card)


# --- SEZIONE UTENTE 2 ---
with col2:
    st.subheader("👤 Utente 2")
    if not st.session_state.auction.can_bid(st.session_state.robot, st.session_state.card,
                                            st.session_state.asta_current):
        pass  # can bid is false # TODO STUT O PULSANT BUCCHI
    else:
        offerta2 = st.number_input("Inserisci la tua offerta (€)", min_value=0, key="input2")
        if st.button("Offri come Utente 2", 3):
            if st.session_state.auction.manage_auction(st.session_state.card, offerta2):
                st.session_state.offerta_utente2 = offerta2
                st.session_state.asta_current = offerta2
                st.success(f"Hai offerto €{offerta2}")
                st.rerun()
            else:
                # st.error("L'offerta deve essere superiore al minimo e all'altra offerta.")
                st.warning("L'offerta non è valida", icon="⚠️")

    if st.button("Passa Utente 2", 4):
        if st.session_state.auction.manage_auction(st.session_state.card, "pass"):
            if st.session_state.auction.resolve_auction(st.session_state.card, st.session_state.human,
                                                        st.session_state.offerta_utente1):
                # TODO CHIAMARE POP VITTORIA
                dialog_show("Carta Vinta", "src/util/gif/player_win.gif")
                #pass
            else:
                # TODO CHIAMARE POP BRUCIATA
                dialog_show("Carta Bruciata", "src/util/gif/burned.gif")
                #pass

        # st.session_state.deck.draw()
        # st.session_state.card = st.session_state.deck.current_card
        # st.session_state.carte_rimaste = len(st.session_state.deck)
        # st.session_state.asta_current = 0
        # st.session_state.robot.has_passed = False
        # st.session_state.human.has_passed = False
        # st.session_state.auction.current_player = st.session_state.human
        # if not st.session_state.auction.is_bidding_possible(st.session_state.card):
        #     print(st.session_state.auction.calculate_final_score())
        # TODO ANIMAZIONI
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAa")
        #st.rerun()



    #     if offerta2 >= st.session_state.deck.current_card.starting_bid  and offerta2 > st.session_state.asta_current and st.session_state.robot.can_bid(offerta2):
    #         st.session_state.offerta_utente2 = offerta2
    #         st.session_state.asta_current = offerta2
    #         st.success(f"Hai offerto €{offerta2}")
    #         st.rerun()  # 👈 forza Streamlit a ridisegnare tutto
    #     else:
    #         #st.error("L'offerta deve essere superiore al minimo e all'altra offerta.")
    #         st.warning("L'offerta non è valida", icon="⚠️")
    #
    # if st.button("Passa Utente 2", 4):
    #     if(st.session_state.human.win_card(st.session_state.deck.current_card, st.session_state.offerta_utente1)):
    #         st.success("Utente 1 hai vinto la card", icon="🎉")
    #         #if st.button("Mostra GIF"):
    #         show_modal_animation_local("anime.gif", duration=2.5, gif_width=2060)
    #     else:
    #         st.warning("Carta bruciata", icon="🔥")
    #     st.session_state.deck.draw()
    #     st.session_state.carte_rimaste = len(st.session_state.deck)
    #     st.session_state.asta_current=0
    #     st.rerun()

st.markdown("---")


