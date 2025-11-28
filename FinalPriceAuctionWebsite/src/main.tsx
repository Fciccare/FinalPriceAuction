import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import Start from './Start.tsx'
import Auction from './Auction.tsx'


import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

export const cases = 2;

const router = createBrowserRouter([
  {
    path: "/",
    element: <Start />,
  },
  {
    path: "/auction",
    element: <Auction />,
  }
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
