import React, { useState, useEffect } from "react";
import deckData from "./deck/deck_1.json";
import Swal from "sweetalert2";
import burnVideo from "./deck/animation/burned.webm"; // <--- IMPORT VITE!
import winCardHuman from "./deck/animation/player_win.webm";
import winCardRobot from "./deck/animation/robot_win.webm";
import humanWinner from "./deck/animation/player_winner.webm";
import robotWinner from "./deck/animation/robot_winner.webm";
import cooperativeWinner from "./deck/animation/both_win.webm";
import mic from "./deck/animation/mic.webm";
import useActionsData from "./components/useAction";

function Auction() {

const [deck, setDeck] = useState<any[]>([]);
const [currentCard, setCurrentCard] = useState<any | null>(null);

const { state, fetchState, actionGame, getCurrentState } = useActionsData();

const [variabile, setVariable] = useState(0)


useEffect(() => {
    console.log("Variabile aggiornata:", state);
}, [state]);

const [currentCardImage, setCurrentCardImage] = useState<string>("");

// Log ogni volta che currentCardImage cambia
// useEffect(() => {
//     console.log("currentCardImage:", currentCardImage);
// }, [currentCardImage]);


function alertVideo(webm_video, loop = false){
    Swal.fire({
  html: `
    <video id="myVideo" autoplay muted playsinline ${loop ? 'loop' : ''}>
      <source src=${webm_video} type="video/webm">
    </video>
  `,
  showConfirmButton: false,
  didOpen: () => {
    const vid = document.getElementById('myVideo');
    if (vid instanceof HTMLVideoElement) {
      vid.onended = () => Swal.close();
    }
  }
});
}


useEffect(() => {
    // Carica direttamente il JSON
    setDeck(deckData);

    // Imposta la prima carta come corrente
    if (deckData.length > 0) {
      setCurrentCard(deckData[0]);
    }
  }, []);

  
useEffect(() => {
  console.log("Deck aggiornato:", deck);
  console.log("Carta corrente:", currentCard);
}, [deck, currentCard]);


//Use effect starting page
useEffect(() => {
    // Fetch iniziale dello stato del gioco
    getCurrentState();
}, []);


useEffect(() => {
    if(state?.lastAuctionResult == "Vincitore: Umano"){
        alertVideo(winCardHuman);
    }else if (state?.lastAuctionResult == "Vincitore: Pepper"){
        alertVideo(winCardRobot);
    }else if (state?.lastAuctionResult == "Carta Bruciata."){
        alertVideo(burnVideo);
    }
}, [state]);



useEffect(() => {
    if(state?.winner == "Cooperative WIN"){
        alertVideo(cooperativeWinner, true);
    }else if (state?.winner == "Umano"){
        alertVideo(humanWinner, true);
    }else if (state?.winner == "Robot"){
        alertVideo(robotWinner, true);
    }else if (state?.winner == "Pareggio"){
        alertVideo(cooperativeWinner, true);
    }
}, [state?.winner]);


return (
        <div className="p-4 min-h-screen">
            <div className="grid grid-cols-3 gap-6">

                {/* --- COLONNA SINISTRA: MAZZO DI CARTE --- */}
                <div className="text-center">
                    <h3 className="text-xl font-semibold mb-3">🂠 Remaining Cards: <span className="font-bold">{state?.cardsRemaining}</span></h3>
                    <img
                        //src={"https://i.ibb.co/x9PZS8W/back-card.png"}
                        src={new URL("deck/images/back-card_clean.png", import.meta.url).href}
                        width={200}
                        alt="Mazzo di carte"
                        className="mx-auto mt-2 shadow-lg rounded-lg"
                    />
                </div>

                {/* --- COLONNA CENTRALE: CARTA IN ASTA + BOX ASTA CORRENTE --- */}
                <div className="flex flex-col items-center">
                    {/* Immagine della Carta */}
                    <img
                        src={new URL("deck/images/deck1/chip_ai.png", import.meta.url).href}
                        width={380}
                        alt={"Carta in asta"}
                        className="rounded-xl shadow-2xl border-4 border-yellow-400"
                    />
                    <div className="text-center mt-2 font-medium text-lg">Chip AI</div>

                    {/* Box Puntata */}
                    <div className="w-[380px] text-center bg-white border border-gray-200 text-gray-800 p-3 rounded-xl shadow-lg mt-4">
                        <h4 className="m-0 text-lg">💰 Minimum Bid: <span className="font-bold text-green-600">42€</span></h4>
                        <h4 className="m-0 text-lg">💰 Current Bid: <span className="font-bold text-red-600">56€</span></h4>
                    </div>
                </div>

                {/* --- COLONNA DESTRA: INFO ASTA / GIOCATORI --- */}
                <div>
                    <h3 className="text-xl font-semibold mb-4">👥 Players</h3>

                    {/* Funzione per renderizzare il box del giocatore */}
                    {/* ===== Giocatore ===== */}
                    <div className="bg-white p-4 rounded-xl shadow-lg mb-4 border border-gray-100">
                        <div className="text-lg font-bold mb-3 border-b pb-2 text-blue-600">🧍 Player</div>

                        {/* Statistiche principali */}
                        <div className="flex justify-around text-center mb-3">
                        <div className="stat-block">
                            <div className="text-2xl font-extrabold text-blue-600">
                            {state?.players?.human?.budget ?? 600}€
                            </div>
                            <div className="text-xs text-gray-500">Coins</div>
                        </div>
                        <div className="stat-block">
                            <div className="text-2xl font-extrabold text-purple-600">
                            {state?.players?.human?.vp ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Score</div>
                        </div>
                        </div>

                        {/* Categorie fisse */}
                        <div className="flex justify-around text-center border-t pt-3">
                        <div className="card-block">
                            <div className="text-lg font-bold text-purple-600">
                            {state?.players?.human?.cards["Reliquia"] ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Reliquie</div>
                        </div>

                        <div className="card-block">
                            <div className="text-lg font-bold text-purple-600">
                            {state?.players?.human?.cards["Tecnologia"] ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Technologies</div>
                        </div>
                        </div>
                    </div>



                    {/* ===== Robot ===== */}
                    <div className="bg-white p-4 rounded-xl shadow-lg mb-4 border border-gray-100">
                        <div className="text-lg font-bold mb-3 border-b pb-2 text-blue-600">🤖 Robot</div>

                        {/* Statistiche principali */}
                        <div className="flex justify-around text-center mb-3">
                        <div className="stat-block">
                            <div className="text-2xl font-extrabold text-blue-600">
                            {state?.players?.robot?.budget ?? 600}€
                            </div>
                            <div className="text-xs text-gray-500">Coins</div>
                        </div>
                        <div className="stat-block">
                            <div className="text-2xl font-extrabold text-purple-600">
                            {state?.players?.robot?.vp ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Score</div>
                        </div>
                        </div>

                        {/* Categorie fisse */}
                        <div className="flex justify-around text-center border-t pt-3">

                        <div className="card-block">
                            <div className="text-lg font-bold text-purple-600">
                            {state?.players?.robot?.cards["Reliquia"] ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Reliquie</div>
                        </div>

                        <div className="card-block">
                            <div className="text-lg font-bold text-purple-600">
                            {state?.players?.robot?.cards["Tecnologia"] ?? 0}
                            </div>
                            <div className="text-xs text-gray-500">Technologies</div>
                        </div>
                        </div>
                    </div>
                </div>

            </div>

            <hr className="my-8 border-t border-gray-300" />

            
            {/* Bottone "Premi per parlare" */}
            {/* <button
            onClick={async () => fetchState()}
            className="mt-8 w-full bg-blue-600 hover:bg-blue-700 text-white p-5 rounded-xl text-2xl font-bold shadow-xl transition transform hover:scale-[1.01]"
            >
            🎤 Premi per parlare
            </button> */}

            <button
                 onClick={async () => {
                // Assicurati che fetchState() ritorni sempre un booleano
                // Swal.fire({title: "Loading...", allowOutsideClick: false,  // Non permette la chiusura cliccando fuori dal pop-up
                //     allowEscapeKey: false,
                //     //remove confirm button
                //     showConfirmButton: false
                // });
                //alertVideo(mic, true);
                /* Swal.fire({title: 'Talk with the robot and wait...',allowOutsideClick: false, didOpen: () => { Swal.showLoading();}});
                const ok = await actionGame();
                Swal.close();
                if (ok != ""){ 
                    Swal.fire({title: ok});
                }  */
                alertVideo(humanWinner, true)

            }}
                className="mt-8 w-full bg-blue-600 hover:bg-blue-700 text-white p-5 rounded-xl text-2xl font-bold shadow-xl transition transform hover:scale-[1.01]"
            >
               🎤 Press to Talk
            </button>
        </div>
    );
}
export default Auction;
