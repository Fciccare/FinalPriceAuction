import React from 'react';
import { useNavigate } from 'react-router';

import useActionsData from "./components/useAction";
import Swal from 'sweetalert2';

function Start(){

    const navigate = useNavigate();
    const { state, fetchState, actionGame, getCurrentState } = useActionsData();
   
    function handleSubmit(e: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
        e.preventDefault();
        console.log("Inizio il gioco e vado alla pagina dell'asta");
        //loading scrren alert swal with circle spinner
        Swal.fire({title: 'Init auction in progress...',allowOutsideClick: false, didOpen: () => { Swal.showLoading();}});
        fetchState().then(() => {
            Swal.close();
            navigate("/auction");
        });
    }

    return (
        <div className="relative flex flex-col items-center mt-6 text-gray-700 bg-white shadow-lg rounded-xl w-96 overflow-hidden">
        <div className="p-8 w-full">
          <h2 className="text-2xl font-semibold mb-4 text-center">FinalPriceAuction</h2>
          <img 
            src={new URL("deck/images/back-card_clean.png", import.meta.url).href}
            width={200}
            className="mx-auto mt-2 shadow-lg rounded-lg"
          />
          <button
            onClick={(e) => handleSubmit(e)}
            className="mt-6 w-full py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400">
            Press to start the game
           </button>
        </div>
      </div>
      
    );
};

export default Start;