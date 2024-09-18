import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css'; // Import the CSS file

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2>Projects</h2>
      <ul className="sidebarLinks">
        <li><Link to="/dashboard" className="sidebarLink">Dashboard</Link></li>
        <li><Link to="/aiqgenapp" className="sidebarLink">AIQGen App</Link></li>
        <li><Link to="/code-generation" className="sidebarLink">Code Generation</Link></li>
        <li><Link to="/self-healing" className="sidebarLink">Self Healing</Link></li>
        <li><Link to="/ticket-classification" className="sidebarLink">Ticket Classification</Link></li>
        <li><Link to="/ticket-triage-ai" className="sidebarLink">Ticket Triage AI</Link></li>

        {/* Add more links or sections as needed */}
      </ul>
    </div>
  );
};

export default Sidebar;
