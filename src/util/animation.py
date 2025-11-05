import base64
import time

def show_modal_video_fade(video_path, duration=4, background_opacity=0.7, video_width=400):
    """
    Mostra un modale con un video centrale e animazioni di fade in/out.
    """
    placeholder = st.empty()

    # Codifica il video in base64 per l'embed diretto
    with open(video_path, "rb") as f:
        data_url = f"data:video/mp4;base64,{base64.b64encode(f.read()).decode()}"

    modal_html = f"""
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    @keyframes fadeOut {{
        from {{ opacity: 1; }}
        to {{ opacity: 0; }}
    }}
    .fade-in {{
        animation: fadeIn 0.8s ease-in forwards;
    }}
    .fade-out {{
        animation: fadeOut 0.8s ease-out forwards;
    }}
    </style>

    <div id="custom-modal" class="fade-in" style="
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, {background_opacity});
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    ">
        <video width="{video_width}" autoplay loop muted playsinline>
            <source src="{data_url}" type="video/webm">
        </video>
    </div>

    <script>
    // Dopo tot secondi, attiva la fade-out
    setTimeout(() => {{
        const modal = document.getElementById("custom-modal");
        if (modal) {{
            modal.classList.remove("fade-in");
            modal.classList.add("fade-out");
            setTimeout(() => modal.remove(), 800); // rimuove dopo la transizione
        }}
    }}, {int(duration * 1000)});
    </script>
    """

    placeholder.markdown(modal_html, unsafe_allow_html=True)
    time.sleep(duration + 1)  # attende la durata + fade-out
    placeholder.empty()

def show_modal_animation_local(st,gif_path, duration=3, background_opacity=0.6, gif_width=250):
    """
    Mostra una GIF locale centrata su sfondo scuro trasparente.
    
    gif_path: percorso al file .gif (locale)
    duration: durata in secondi prima che sparisca
    background_opacity: livello di trasparenza dello sfondo (0–1)
    gif_width: larghezza della gif in pixel
    """
    placeholder = st.empty()

    # Legge il file GIF e lo converte in base64
    with open(gif_path, "rb") as f:
        data_url = f"data:image/gif;base64,{base64.b64encode(f.read()).decode()}"

    # HTML del modale
    modal_html = f"""
    <div style="
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, {background_opacity});
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    ">
        <img src="{data_url}" width="{gif_width}">
    </div>
    """

    # Mostra la GIF
    placeholder.markdown(modal_html, unsafe_allow_html=True)
    time.sleep(duration)
    placeholder.empty()



# if st.button("🔄 Nuova Asta"):
#    show_modal_video_fade(
#         video_path="src/output.webm",  # metti qui il tuo file
#         duration=2,                   # quanto resta visibile
#         background_opacity=0,       # quanto scuro è lo sfondo
#         video_width=1080               # dimensione video
#     )

#st.title("Esempio GIF locale come overlay")

#if st.button("Mostra GIF"):
#    show_modal_animation_local("win.gif", duration=1.6, gif_width=2060)


import base64
import uuid

def show_gif_modal(st, gif_path: str, duration: float = 3, width: str = "1024px"):
    """
    Mostra una GIF locale come popup modale trasparente in Streamlit,
    che scompare automaticamente dopo 'duration' secondi.
    Riutilizzabile più volte (forza sempre il ri-render dell’animazione).

    Args:
        gif_path (str): Percorso locale della GIF (trasparente).
        duration (float): Durata di visualizzazione in secondi.
        width (str): Larghezza della GIF (es. '200px' o '30%').
    """

    # Chiave univoca per forzare nuovo render ad ogni chiamata
    unique_key = str(uuid.uuid4()).replace("-", "")

    # Legge la GIF e la converte in base64
    with open(gif_path, "rb") as f:
        gif_data = f.read()
    gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    # CSS + HTML con key univoca
    modal_style = f"""
    <style>
    .modal-bg-{unique_key} {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.35);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut-{unique_key} {duration}s forwards;
    }}
    @keyframes fadeOut-{unique_key} {{
        0% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """

    modal_html = f"""
    <div class="modal-bg-{unique_key}">
        <img src="data:image/gif;base64,{gif_base64}" width="{width}" />
    </div>
    """

    st.markdown(modal_style + modal_html, unsafe_allow_html=True)




def show_gif_modal_2(st, gif_path: str, duration: float = 3, size: str = "250px", overlay_opacity: float = 0.35):
    """
    Mostra una GIF locale come popup modale trasparente in Streamlit,
    che scompare automaticamente dopo 'duration' secondi.
    Ottimizzata per scaling fluido (senza lag).

    Args:
        gif_path (str): Percorso locale della GIF (trasparente).
        duration (float): Durata in secondi prima che scompaia.
        size (str): Dimensione massima della GIF (es. '200px', '40%').
        overlay_opacity (float): Opacità dello sfondo (0 = trasparente, 1 = nero pieno).
    """

    unique_key = str(uuid.uuid4()).replace("-", "")

    # Legge la GIF e la converte in base64
    with open(gif_path, "rb") as f:
        gif_data = f.read()
    gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    # CSS con animazione e scaling fluido
    modal_style = f"""
    <style>
    .modal-bg-{unique_key} {{
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, {overlay_opacity});
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut-{unique_key} {duration}s forwards;
        pointer-events: none;
    }}
    .gif-wrapper-{unique_key} {{
        max-width: {size};
        max-height: {size};
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .gif-wrapper-{unique_key} img {{
        width: 100%;
        height: auto;
        image-rendering: smooth;
        will-change: transform;
    }}
    @keyframes fadeOut-{unique_key} {{
        0% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """

    modal_html = f"""
    <div class="modal-bg-{unique_key}">
        <div class="gif-wrapper-{unique_key}">
            <img src="data:image/gif;base64,{gif_base64}" alt="popup gif" />
        </div>
    </div>
    """

    st.markdown(modal_style + modal_html, unsafe_allow_html=True)




def show_gif_modal_online(st, gif_url: str, duration: float = 3, size: str = "250px", overlay_opacity: float = 0.35):
    """
    Mostra una GIF hostata online come popup modale trasparente in Streamlit.
    ✅ Playback sempre fluido (gestito dal browser)
    ✅ Scompare automaticamente dopo `duration` secondi

    Args:
        gif_url (str): URL pubblico della GIF (es. da Giphy o CDN).
        duration (float): Durata visibile in secondi.
        size (str): Dimensione massima (es. '250px' o '40%').
        overlay_opacity (float): Opacità dello sfondo (0 = trasparente, 1 = nero pieno).
    """
    unique_key = str(uuid.uuid4()).replace("-", "")

    modal_style = f"""
    <style>
    .modal-bg-{unique_key} {{
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, {overlay_opacity});
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut-{unique_key} {duration}s forwards;
        pointer-events: none;
    }}
    .gif-wrapper-{unique_key} {{
        max-width: {size};
        max-height: {size};
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .gif-wrapper-{unique_key} img {{
        width: 100%;
        height: auto;
        image-rendering: smooth;
        will-change: transform;
    }}
    @keyframes fadeOut-{unique_key} {{
        0% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """

    modal_html = f"""
    <div class="modal-bg-{unique_key}">
        <div class="gif-wrapper-{unique_key}">
            <img src="{gif_url}?cachebust={unique_key}" alt="popup gif" />
        </div>
    </div>
    """

    st.markdown(modal_style + modal_html, unsafe_allow_html=True)





def show_gif_modal_super(st, gif_path: str, duration: float = 3, size: str = "250px", overlay_opacity: float = 0.35):
    """
    Mostra una GIF locale in Streamlit come popup modale trasparente e temporanea.
    ✅ La GIF riparte sempre da capo e non lagga.
    ✅ Scompare automaticamente dopo `duration` secondi.

    Args:
        gif_path (str): Percorso locale della GIF.
        duration (float): Durata visibile in secondi.
        size (str): Dimensione massima (es. '250px' o '30%').
        overlay_opacity (float): Opacità sfondo (0=trasparente, 1=nero pieno).
    """
    unique_key = str(uuid.uuid4()).replace("-", "")

    # Legge la GIF
    with open(gif_path, "rb") as f:
        gif_data = f.read()
    gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    # CSS
    modal_style = f"""
    <style>
    .modal-bg-{unique_key} {{
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, {overlay_opacity});
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut-{unique_key} {duration}s forwards;
        pointer-events: none;
    }}
    .gif-wrapper-{unique_key} {{
        max-width: {size};
        max-height: {size};
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    @keyframes fadeOut-{unique_key} {{
        0% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """

    # HTML + JS: ricrea la GIF come blob, così riparte da zero ogni volta
    modal_html = f"""
    <div class="modal-bg-{unique_key}">
        <div class="gif-wrapper-{unique_key}">
            <img id="gif-{unique_key}" alt="popup gif" />
        </div>
    </div>
    <script>
    const byteCharacters_{unique_key} = atob("{gif_base64}");
    const byteNumbers_{unique_key} = new Array(byteCharacters_{unique_key}.length);
    for (let i = 0; i < byteCharacters_{unique_key}.length; i++) {{
        byteNumbers_{unique_key}[i] = byteCharacters_{unique_key}.charCodeAt(i);
    }}
    const byteArray_{unique_key} = new Uint8Array(byteNumbers_{unique_key});
    const blob_{unique_key} = new Blob([byteArray_{unique_key}], {{ type: 'image/gif' }});
    const url_{unique_key} = URL.createObjectURL(blob_{unique_key});
    document.getElementById("gif-{unique_key}").src = url_{unique_key};

    setTimeout(() => {{
        URL.revokeObjectURL(url_{unique_key});
        const modal = document.querySelector(".modal-bg-{unique_key}");
        if (modal) modal.remove();
    }}, {int(duration * 1000)});
    </script>
    """

    st.markdown(modal_style + modal_html, unsafe_allow_html=True)




def show_gif_off(st, components,gif_path: str, duration: float = 3, size: str = "250px", overlay_opacity: float = 0.35):
    unique_key = str(uuid.uuid4()).replace("-", "")

    # Legge e codifica la GIF in base64
    with open(gif_path, "rb") as f:
        gif_data = f.read()
    gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    html_code = f"""
    <html>
    <head>
        <style>
        @keyframes fadeInOut-{unique_key} {{
            0% {{ opacity: 0; }}
            10% {{ opacity: 1; }}
            90% {{ opacity: 1; }}
            100% {{ opacity: 0; visibility: hidden; }}
        }}
        .popup-{unique_key} {{
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background-color: rgba(0, 0, 0, {overlay_opacity});
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeInOut-{unique_key} {duration}s forwards;
        }}
        .popup-{unique_key} img {{
            max-width: {size};
            height: auto;
            display: block;
        }}
        </style>
    </head>
    <body>
        <div class="popup-{unique_key}">
            <img src="data:image/gif;base64,{gif_base64}?{unique_key}" alt="popup gif"/>
        </div>
    </body>
    </html>
    """

    # Questo rende l’HTML vero, non isolato dentro il layout di Streamlit
    components.html(html_code, height=0, width=0)




def show_popup_gif_bro(st, gif_path, auto_close_seconds=2.5):
    """
    Mostra una GIF come popup modale.
    
    Args:
        gif_path (str): Percorso del file GIF
        auto_close_seconds (int, optional): Secondi dopo i quali il popup si chiude automaticamente
    """
    # Genera un ID unico per questo popup
        # Genera un ID unico per questo popup
    popup_id = f"popup_{uuid.uuid4().hex[:8]}"
    
    # Leggi la GIF
    with open(gif_path, "rb") as file_:
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
    
    # Converti i secondi in millisecondi
    auto_close_ms = int(auto_close_seconds * 1000)
    
    # Crea il popup
    st.markdown(
        f"""
        <style>
        .popup-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeIn 0.3s;
            transition: opacity 0.3s ease-out;
        }}
        
        .popup-content {{
            position: relative;
            max-width: 90%;
            max-height: 90%;
            animation: scaleIn 0.3s;
        }}
        
        .popup-content img {{
            max-width: 100%;
            max-height: 90vh;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
        }}
        
        .close-btn {{
            position: absolute;
            top: -40px;
            right: 0;
            color: white;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
            background: none;
            border: none;
            transition: transform 0.2s;
        }}
        
        .close-btn:hover {{
            transform: scale(1.2);
            color: #ff6b6b;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes scaleIn {{
            from {{ transform: scale(0.7); }}
            to {{ transform: scale(1); }}
        }}
        </style>
        
        <div class="popup-overlay" id="{popup_id}">
            <div class="popup-content">
                <button class="close-btn" onclick="closePopup_{popup_id}()">&times;</button>
                <img src="data:image/gif;base64,{data_url}" alt="popup gif">
            </div>
        </div>
        
        <script>
        // Attendi che il DOM sia pronto
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initPopup_{popup_id});
        }} else {{
            initPopup_{popup_id}();
        }}
        
        function initPopup_{popup_id}() {{
            var popupElement = document.getElementById('{popup_id}');
            
            if (!popupElement) {{
                console.error('Popup element not found: {popup_id}');
                return;
            }}
            
            function closePopup_{popup_id}() {{
                if (popupElement && popupElement.style.display !== 'none') {{
                    popupElement.style.opacity = '0';
                    setTimeout(function() {{
                        popupElement.style.display = 'none';
                    }}, 300);
                }}
            }}
            
            // Rendi la funzione globale per il bottone
            window.closePopup_{popup_id} = closePopup_{popup_id};
            
            // Chiudi il popup cliccando fuori dall'immagine
            popupElement.addEventListener('click', function(e) {{
                if (e.target.id === '{popup_id}') {{
                    closePopup_{popup_id}();
                }}
            }});
            
            // Chiudi il popup con il tasto ESC
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape' || e.key === 'Esc') {{
                    closePopup_{popup_id}();
                }}
            }});
            
            // Auto-chiusura dopo {auto_close_seconds} secondi
            console.log('Setting timeout for {auto_close_ms}ms');
            setTimeout(function() {{
                console.log('Auto-closing popup {popup_id}');
                closePopup_{popup_id}();
            }}, {auto_close_ms});
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )



import streamlit.components.v1 as components
if st.button("Mostra GIF", 5):
    show_popup_gif_bro(st, "src/util/gif/Burned_opt.gif")
    #show_modal_animation_local(st,"anime.gif", duration=2.5, gif_width=2060)
    #show_modal_animation_local(st,"src/util/gif/Burned_opt.gif", duration=2.5, gif_width=1080)
    #show_gif_modal_2(st, "src/util/gif/Burned_opt.gif", duration=3, size="128px")
    #show_gif_off(st, components,"src/util/gif/Burned_opt.gif", duration=3, size="128px")
    #show_gif_modal_online(st, ,duration=3, size="128px")


"""### gif from local file"""
# file_ = open("src/util/gif/Burned_opt.gif", "rb")
# contents = file_.read()
# data_url = base64.b64encode(contents).decode("utf-8")
# file_.close()

# st.markdown(
#     f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
#     unsafe_allow_html=True,
# )


import base64
import time

def show_gif_popupa(gif_path, width="300px", duration=3):
    """
    Visualizza una GIF locale come pop-up su Streamlit (senza sfondo)
    Si chiude automaticamente dopo tot secondi (timer parte subito)
    
    Args:
        gif_path: percorso locale della GIF (es: "src/util/gif/Burned_opt.gif")
        width: larghezza della GIF (default: "300px")
        duration: secondi prima di chiudersi automaticamente (default: 3)
    """
    
    # Genera un ID univoco per ogni chiamata (evita cache)
    popup_id = str(uuid.uuid4())
    
    # Registra il tempo di inizio PRIMA di mostrare la GIF
    start_time = time.time()
    
    # Carica e codifica la GIF
    with open(gif_path, "rb") as file_:
        contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    
    # CSS per il pop-up overlay
    popup_html = f"""
    <style>
        .gif-popup-overlay-{popup_id} {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }}
        .gif-popup-container-{popup_id} {{
            position: relative;
            background-color: transparent;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .gif-popup-container-{popup_id} img {{
            max-width: {width};
            height: auto;
        }}
    </style>
    
    <div class="gif-popup-overlay-{popup_id}" id="gif-overlay-{popup_id}">
        <div class="gif-popup-container-{popup_id}">
            <img src="data:image/gif;base64,{data_url}" alt="popup gif">
        </div>
    </div>
    """
    
    placeholder = st.empty()
    placeholder.markdown(popup_html, unsafe_allow_html=True)
    
    # Calcola il tempo rimanente e attendi (il timer è già partito!)
    elapsed = time.time() - start_time
    remaining = duration - elapsed
    
    if remaining > 0:
        time.sleep(remaining)
    
    placeholder.empty()

# ============ UTILIZZO ============


def showa(gif_path, width="300px", duration=3):
    """
    Visualizza una GIF locale come pop-up su Streamlit (senza sfondo)
    Si chiude automaticamente dopo tot secondi
    
    Args:
        gif_path: percorso locale della GIF (es: "src/util/gif/Burned_opt.gif")
        width: larghezza della GIF (default: "300px")
        duration: secondi prima di chiudersi automaticamente (default: 3)
    """
    
    # Crea un ID univoco per questo pop-up
    popup_id = str(uuid.uuid4())
    
    # Salva il timestamp di inizio SOLO la prima volta
    session_key = f"gif_start_{popup_id}"
    if session_key not in st.session_state:
        st.session_state[session_key] = time.time()
    
    start_time = st.session_state[session_key]
    elapsed = time.time() - start_time
    
    # Se non è passato il tempo, mostra la GIF
    if elapsed < duration:
        # Carica la GIF
        with open(gif_path, "rb") as file_:
            contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        
        # HTML/CSS
        popup_html = f"""
        <style>
            .gif-popup-overlay-{popup_id} {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }}
            .gif-popup-container-{popup_id} {{
                position: relative;
                background-color: transparent;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .gif-popup-container-{popup_id} img {{
                max-width: {width};
                height: auto;
            }}
        </style>
        
        <div class="gif-popup-overlay-{popup_id}">
            <div class="gif-popup-container-{popup_id}">
                <img src="data:image/gif;base64,{data_url}" alt="popup gif">
            </div>
        </div>
        """
        
        st.markdown(popup_html, unsafe_allow_html=True)
        
        # Piccolo sleep per non sovraccaricare
        time.sleep(2.5)
        st.rerun()

import streamlit as st

def show_css(gif_base64: str, titolo: str = "Notifica", testo: str = ""):
    """Mostra un pop-up con una GIF animata."""
    popup_html = f"""
    <style>
    .popup {{
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background-color: rgba(0,0,0,0.6);
      display: flex; justify-content: center; align-items: center;
      z-index: 9999;
    }}
    .popup-content {{
      background-color: white;
      border-radius: 20px;
      padding: 20px 30px;
      text-align: center;
      box-shadow: 0 0 20px rgba(0,0,0,0.4);
      animation: fadeIn 0.3s;
    }}
    .popup-content h3 {{
      margin-top: 15px;
      color: #333;
    }}
    .popup-content p {{
      color: #555;
    }}
    @keyframes fadeIn {{
      from {{opacity: 0; transform: scale(0.9);}}
      to {{opacity: 1; transform: scale(1);}}
    }}
    </style>

    <div class="popup">
      <div class="popup-content">
        <img src="data:image/gif;base64,{gif_base64}" width="250"><br>
        <h3>{titolo}</h3>
        <p>{testo}</p>
      </div>
    </div>
    """
    st.markdown(popup_html, unsafe_allow_html=True)


def show_temp_gif(container, gif_url, seconds=3, align="center", width="300px"):
    """
    Mostra una GIF animata temporaneamente in un contenitore specifico.
    
    Args:
        container: dove mostrare la GIF (es. st, col1, st.sidebar, ecc.)
        gif_url: URL (o path relativo) della GIF
        seconds: durata in secondi
        align: "left", "center" o "right"
        width: larghezza (es. "200px", "50%")
    """
    placeholder = container.empty()
    with placeholder.container():
        st.markdown(
            f"""
            <div style='text-align:{align};'>
                <img src="{gif_url}" width="{width}">
            </div>
            """,
            unsafe_allow_html=True
        )
    time.sleep(seconds)
    placeholder.empty()


def show_temp_local_gif(placeholder, path, seconds=3, width="200px"):
    """Mostra una GIF locale temporaneamente in un placeholder."""
    with open(path, "rb") as f:
        data_url = base64.b64encode(f.read()).decode("utf-8")
    
    html = f"""
    <div style='text-align:center;'>
        <img src="data:image/gif;base64,{data_url}" width="{width}">
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)
    time.sleep(seconds)
    placeholder.empty()



import random
def show_temp_local_gif_2(placeholder, path, seconds=2.5, width="200px"):
    """Mostra una GIF locale (che parte sempre da zero) per un tempo limitato."""
    with open(path, "rb") as f:
        data_url = base64.b64encode(f.read()).decode("utf-8")
    
    # Crea un ID univoco per forzare un nuovo elemento <img> ad ogni chiamata
    unique_id = f"gif_{random.randint(0, 999999)}"

    html = f"""
    <div id="{unique_id}" style='text-align:center;'>
        <img src="data:image/gif;base64,{data_url}" width="{width}">
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)
    time.sleep(seconds)
    placeholder.empty()
    placeholder = st.empty()

if st.button("GIFFFFO"):    
    # La GIF scomparirà dopo 3 secondi
    # showa(
    #     gif_path="src/util/gif/Burned_opt.gif",
    #     width="400px",
    #     duration=2  # ⏰ Cambia questo valore per aumentare/diminuire i secondi
    # )
    #show_temp_gif(st, "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif", seconds=3)
    #show_temp_local_gif_2(gif_placeholder, "src/util/gif/Burned_opt.gif")
    dialog_show("Hai vinto i soldiiiiiiiii", "src/util/gif/burned_hd.gif")
    