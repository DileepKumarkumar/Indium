import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';
import logo from './logo_fixed.png';

const Navbar = ({ onLogout }) => {
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleLogoutClick = () => {
    console.log('Logout clicked');
    if (onLogout) {
      onLogout(); // Call the passed logout function
    }
    navigate('/signin'); // Navigate to the sign-in page
  };

  return (
    <nav className="navbar">
      <img
        src={logo}
        alt="Logo"
        className="logo"
        onClick={handleLogoClick} // Navigate to homepage on logo click
      />
      <ul className="navLinks">
        <li><a href="#">Profile</a></li>
        <li><a href="#">Settings</a></li>
        <li id = "logout"
          onClick={handleLogoutClick} // Trigger logout and navigate when this item is clicked
          style={{ cursor: 'pointer' }}
        >
          Log Out
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
