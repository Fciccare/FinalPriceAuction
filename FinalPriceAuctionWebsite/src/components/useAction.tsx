import { useEffect, useState } from "react";

export interface AuctionState {
  gameActive: boolean;
  gameOver: boolean;
  winner: string | null;

  currentBid: number;
  highestBidder: "human" | "robot" | null;
  currentPlayerTurn: "human" | "robot";

  cardsRemaining: number;

  currentCard: {
    name: string;
    image: string;
    category: string;
    color: string;
    vp: number;
    startingBid: number;
  } | null;

  players: {
    human: PlayerUI;
    robot: PlayerUI;
  };

  aiDialogue: string;
  lastAuctionResult: string | null;
}

export interface PlayerUI {
  budget: number;
  vp: number;
  cards: Record<string, number>;
  hasPassed: boolean;
}

/* ---------------------------------------------------
   🧠 Mapping JSON {backend} → {frontend / Typescript}
--------------------------------------------------- */
function mapBackendToFrontend(data: any): AuctionState {
  return {
    gameActive: data.game_active,
    gameOver: data.game_over,
    winner: data.winner,

    currentBid: data.current_bid,
    highestBidder: data.highest_bidder,
    currentPlayerTurn: data.current_player_turn,

    cardsRemaining: data.cards_remaining,

    currentCard: data.current_card
      ? {
          name: data.current_card.name,
          image: data.current_card.img_url,
          category: data.current_card.category,
          color: data.current_card.color,
          vp: data.current_card.vp,
          startingBid: data.current_card.starting_bid
        }
      : null,

    players: {
      human: {
        budget: data.human.budget,
        vp: data.human.vp,
        cards: data.human.cards,
        hasPassed: data.human.has_passed
      },
      robot: {
        budget: data.robot.budget,
        vp: data.robot.vp,
        cards: data.robot.cards,
        hasPassed: data.robot.has_passed
      }
    },

    aiDialogue: data.ai_dialogue,
    lastAuctionResult: data.last_auction_result
  };
}

/* ---------------------------------------------------
   🎮  Hook principale: useAuction()
--------------------------------------------------- */
export default function useAuction() {
  const [state, setState] = useState<AuctionState | null>(null);
//   const [loading, setLoading] = useState<boolean>(true);

  /* 🔄 Fetch iniziale */
  const fetchState = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/game/start");
      const data = await res.json();
      console.log(data);
      setState(mapBackendToFrontend(data));
    } catch (err) {
      console.error("Errore nel fetch dello stato:", err);
    // } finally {
    //   setLoading(false);
    // }
    }
  };


  const actionGame = async (): Promise<String> => {
    try {
      const res = await fetch("http://127.0.0.1:5000/game/action");
      //console.log(res);
      if (!res.ok){
        const data = await res.json();
        return data["error"];
      }else{
        const data = await res.json();
        setState(mapBackendToFrontend(data));
        return "";  // tutto ok
      }
    } catch (err: Error | any) {
      console.error("Errore nel fetch dello stato:", err);
      return err.toString();
    // } finally {
    //   setLoading(false);
    // }
    }
  };

  const getCurrentState = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/game/state");
      const data = await res.json();
      setState(mapBackendToFrontend(data));
    } catch (err) {
      console.error("Errore nel fetch dello stato:", err);
    // } finally {
    //   setLoading(false);
    // }
    }
  }; 

//   /* 💰 Puntata */
//   const placeBid = async (player: "human" | "robot", amount: number) => {
//     try {
//       const res = await fetch("http://localhost:5000/bid", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ player, amount })
//       });

//       const data = await res.json();
//       setState(mapBackendToFrontend(data));
//     } catch (err) {
//       console.error("Errore durante la puntata:", err);
//     }
//   };

//   /* ✋ Passa il turno */
//   const passTurn = async (player: "human" | "robot") => {
//     try {
//       const res = await fetch("http://localhost:5000/pass", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ player })
//       });

//       const data = await res.json();
//       setState(mapBackendToFrontend(data));
//     } catch (err) {
//       console.error("Errore passaggio turno:", err);
//     }
//   };

//   /* 🔄 Forza il server ad andare alla carta successiva */
//   const nextCard = async () => {
//     try {
//       const res = await fetch("http://localhost:5000/next-card", {
//         method: "POST"
//       });
//       const data = await res.json();
//       setState(mapBackendToFrontend(data));
//     } catch (err) {
//       console.error("Errore durante next-card:", err);
//     }
//   };

//   /* 📌 Aggiorna automaticamente all’avvio */
//   useEffect(() => {
//     fetchState();
//   }, []);

  return {
    state, fetchState, actionGame, getCurrentState
    // ,loading,
    // fetchState,
    // placeBid,
    // passTurn,
    // nextCard
  };
}
