import streamlit as st
import asyncio
import nest_asyncio
from logic.transcriber import capture_audio

nest_asyncio.apply()  # Patch per poter usare run_until_complete in Streamlit

@st.dialog("FinalPriceAuction", dismissible=False)
async def final_dialog_async(text: str, webm: str = ""):
    st.write(f"# {text}")
    if webm:
        st.video(webm, loop=True, autoplay=True)
    await asyncio.sleep(8)  # sleep asincrono

st.markdown("-------")

if st.button("Test Bloccante"):
    with st.spinner("Dialog in corso..."):
        # Ottieni l'event loop di Streamlit
        loop = asyncio.get_event_loop()
        try:
            # Esegui la coroutine asincrona
            loop.run_until_complete(final_dialog_async("Parla ora dopo il beep!", "src/util/webm/burned.webm"))
        except Exception as e:
            st.error(f"Errore nel dialog asincrono: {e}")

    # Dopo il dialog, cattura l'audio (sincrono)
    value = capture_audio()
    st.write(f"Sono state puntate {value} monete")
