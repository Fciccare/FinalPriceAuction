import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

from logic.deck import Deck
from logic.player import Player
from logic.robot import Robot


#st.title('Uber pickups in NYC')

#filename="main.py"
#import os
#import subprocess
#subprocess.Popen(["streamlit", "run", filename, os.devnull])
import streamlit as st
import streamlit_shadcn_ui as ui

# --- CONFIGURAZIONE BASE ---
st.set_page_config(page_title="Asta tra due utenti", layout="wide")

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

    if "player" not in st.session_state:
        st.session_state.player = Player("Umano", 0 , 1000)

    if "robot" not in st.session_state:
        st.session_state.robot = Robot("Robot", 0 , 1000, "competitive")

    if "deck" not in st.session_state:
        deck = Deck.load_from_json("deck_1.json")
        deck.shuffle()
        st.session_state.deck=deck
        st.session_state.deck.draw()

    #if "card" not in st.session_state:
        #st.session_state.card = st.session_state.deck.current_card


    print(st.session_state.deck.current_card)
    #start_game()


# --- INIZIALIZZAZIONE DELLO STATO ---
if "offerta_utente1" not in st.session_state:
    st.session_state.offerta_utente1 = 0
if "offerta_utente2" not in st.session_state:
    st.session_state.offerta_utente2 = 0
if "vincitore" not in st.session_state:
    st.session_state.vincitore = None

if "minimo_asta" not in st.session_state:
    st.session_state.minimo_asta = st.session_state.deck.current_card.starting_bid  # base d'asta

if "asta_corrent" not in st.session_state:
    st.session_state.asta_corrent = 0

if "carte_rimaste" not in st.session_state:
    st.session_state.carte_rimaste = len(st.session_state.deck)
if "crediti_utente1" not in st.session_state:
    st.session_state.crediti_utente1 = st.session_state.player.budget
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
            <h4 style="margin: 0;">💰 Puntata Corrente: {st.session_state.asta_corrent}</h4>
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
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 0 8px rgba(0,0,0,0.15);
        }}
        .stat-line {{
            margin: 3px 0;
        }}
        </style>

        <div class="player-box">
            <h4 style="margin: 0;">🧍 Giocatore 1</h4>
            <p class="stat-line">💰 Crediti: €{st.session_state.player.budget}</p>
            <p class="stat-line">📊 Punteggio: {st.session_state.player.victory_points}</p>
            <p class="stat-line">🎨 Carte Vinte: {len(st.session_state.player.cards)}</p>
        </div>

        <div class="player-box">
            <h4 style="margin: 0;">🧍 Giocatore 2</h4>
            <p class="stat-line">💰 Crediti: €{st.session_state.robot.budget}</p>
            <p class="stat-line">📊 Punteggio: {st.session_state.robot.victory_points}</p>
            <p class="stat-line">🎨 Carte Vinte: {len(st.session_state.robot.cards)}</p>
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
    offerta1 = st.number_input("Inserisci la tua offerta (€)", min_value=0, key="input1")
    if st.button("Offri come Utente 1", 1):
        if offerta1 >= st.session_state.deck.current_card.starting_bid  and offerta1 > st.session_state.asta_corrent and st.session_state.player.can_bid(offerta1):
            st.session_state.offerta_utente1 = offerta1
            st.session_state.asta_corrent = offerta1
            st.success(f"Hai offerto €{offerta1}")
            st.rerun()  # 👈 forza Streamlit a ridisegnare tutto
        else:
            #st.error("L'offerta deve essere superiore al minimo e all'altra offerta.")
            st.warning("L'offerta non è valida", icon="⚠️")

    if st.button("Passa Utente 1", 2):
        if(st.session_state.robot.win_card(st.session_state.deck.current_card, st.session_state.offerta_utente2)):
            st.success("Utente 2 hai vinto la card", icon="🎉")
        else:
            st.warning("Carta bruciata", icon="🔥")
        st.session_state.deck.draw()
        st.session_state.carte_rimaste = len(st.session_state.deck)
        st.session_state.asta_corrent=0
        #print(st.session_state.card)
        st.rerun()


# --- SEZIONE UTENTE 2 ---
with col2:
    st.subheader("👤 Utente 2")
    offerta2 = st.number_input("Inserisci la tua offerta (€)", min_value=0, key="input2")
    if st.button("Offri come Utente 2", 3):
        if offerta2 >= st.session_state.deck.current_card.starting_bid  and offerta2 > st.session_state.asta_corrent and st.session_state.robot.can_bid(offerta2):
            st.session_state.offerta_utente2 = offerta2
            st.session_state.asta_corrent = offerta2
            st.success(f"Hai offerto €{offerta2}")
            st.rerun()  # 👈 forza Streamlit a ridisegnare tutto
        else:
            #st.error("L'offerta deve essere superiore al minimo e all'altra offerta.")
            st.warning("L'offerta non è valida", icon="⚠️")

    if st.button("Passa Utente 2", 4):
        if(st.session_state.player.win_card(st.session_state.deck.current_card, st.session_state.offerta_utente1)):
            st.success("Utente 1 hai vinto la card", icon="🎉")
        else:
            st.warning("Carta bruciata", icon="🔥")
        st.session_state.deck.draw()
        st.session_state.carte_rimaste = len(st.session_state.deck)
        st.session_state.asta_corrent=0
        st.rerun()

st.markdown("---")









# # --- CHIUSURA ASTA ---
# if st.button("🔔 Chiudi Asta"):
#     if st.session_state.offerta_utente1 > st.session_state.offerta_utente2:
#         st.session_state.vincitore = "Utente 1"
#     elif st.session_state.offerta_utente2 > st.session_state.offerta_utente1:
#         st.session_state.vincitore = "Utente 2"
#     else:
#         st.session_state.vincitore = "Pareggio"

# # --- RISULTATO ---
# if st.session_state.vincitore:
#     st.markdown("## 🏆 Risultato dell'Asta:")
#     st.write(f"Offerta Utente 1: €{st.session_state.offerta_utente1}")
#     st.write(f"Offerta Utente 2: €{st.session_state.offerta_utente2}")
#     if st.session_state.vincitore == "Pareggio":
#         st.warning("⚖️ L'asta è finita in pareggio!")
#     else:
#         st.success(f"🎉 Il vincitore è **{st.session_state.vincitore}**!")

# # --- RESET ---
# if st.button("🔄 Nuova Asta"):
#     for key in ["offerta_utente1", "offerta_utente2", "vincitore"]:
#         st.session_state[key] = 0 if "offerta" in key else None
#     st.experimental_rerun()

