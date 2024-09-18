import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../Navbar/Navebar'  // Adjusted the import path
import Sidebar from '../Sidebar/Sidebar'; // Adjusted the import path
import './Home.css'; // Import the CSS file for layout

function Home() {
  return (
    <div className="home-container">
      <Navbar />
      <Sidebar />
      <div className="content">
        <Outlet /> {/* This is where different components like Dashboard, etc., will render */}
      </div>
    </div>
  );
}

export default Home;
