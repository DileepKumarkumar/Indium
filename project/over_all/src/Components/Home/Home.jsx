import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../Navbar/Navebar'  // Adjusted the import path
import Sidebar from '../Sidebar/Sidebar'; // Adjusted the import path
import './Home.css'; // Import the CSS file for layout

function Home({ onLogout }) {
  console.log('Home onLogout:', onLogout); // Check if the function is received
  return (
    <div className="home-container">
      <Navbar onLogout={onLogout} />
      <Sidebar />
      <div className="content">
        <Outlet />
      </div>
    </div>
  );
}

export default Home;
