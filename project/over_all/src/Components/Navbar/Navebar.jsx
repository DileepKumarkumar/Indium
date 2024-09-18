import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css'; // Correct the filename if needed
import logo from './logo_fixed.png';

const Navbar = () => {
  const navigate = useNavigate(); // Hook to navigate programmatically

  // Function to handle logo click and navigate to homepage
  const handleLogoClick = () => {
    navigate('/'); // Navigate to the homepage
  };

  return (
    <nav className="navbar">
      <img
        src={logo}
        alt="Sales Analytics Logo"
        className="logo"
        onClick={handleLogoClick} // Attach the click handler
      />
      <ul className="navLinks">
        <li><a href="#">Dashboard</a></li>
        <li><a href="#">Reports</a></li>
        <li><a href="#">Settings</a></li>
      </ul>
    </nav>
  );
};

export default Navbar;
