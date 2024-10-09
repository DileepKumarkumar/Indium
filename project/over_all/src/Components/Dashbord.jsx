import React from 'react';
import './Dashboard.css'; // Import the CSS file
import './icon.jpg'; // Adjust the path to your image

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <img src="icon.jpg" alt="Indium Software Logo" className="logo" />
      <p>Hi, Welcome To Indium AI-Led Assurance!!</p>
    </div>
  );
};

export default Dashboard;
