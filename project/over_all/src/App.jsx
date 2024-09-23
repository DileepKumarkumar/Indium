import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './Components/Home/Home';
import Dashboard from './Components/Dashbord';
import TestCaseGeneration from './Components/Dashbord/Testcasegeneration/TestCaseGeneration';
import AITCGen from './Components/Dashbord/AITCGen/Aitcgen';
import TicketClassification from './Components/Dashbord/TicketClassification/TicketClassification';
import Aiqgenapp from './Components/Dashbord/AIQGen/Aiqgenapp';
import Tickettriageai from './Components/Dashbord/TicketTriageAI/Tickettriageai';
import SignUp from './Components/Login/signup/signup';
import Signin from './Components/Login/signin/signin';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
    // Optionally store in localStorage or sessionStorage
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    // Optionally clear any storage or state related to authentication
    localStorage.removeItem('isAuthenticated');
  };

  return (
    <Router>
      <Routes>
        {!isAuthenticated ? (
          <>
            <Route path="/signin" element={<Signin onLogin={handleLogin} />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="*" element={<Navigate to="/signin" />} />
          </>
        ) : (
          <>
            <Route path="/" element={<Home onLogout={handleLogout} />}>
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="aiqgenapp" element={<Aiqgenapp />} />
              <Route path="Test-Case-Generation" element={<TestCaseGeneration />} />
              <Route path="AItcgen" element={<AITCGen />} />
              <Route path="ticket-classification" element={<TicketClassification />} />
              <Route path="ticket-triage-ai" element={<Tickettriageai />} />
              <Route path="*" element={<Navigate to="/dashboard" />} />
            </Route>
          </>
        )}
      </Routes>
    </Router>
  );
}

export default App;
