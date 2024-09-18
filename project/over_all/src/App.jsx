import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Components/Home/Home';
import Dashboard from './Components/Dashbord';
import CodeGeneration from './Components/Dashbord/codegeneration/Codegeneration';
import SelfHealing from './Components/Dashbord/SelfHealing/Selfhealing';
import TicketClassification from './Components/Dashbord/TicketClassification/TicketClassification';
import Aiqgenapp from './Components/Dashbord/AIQGen/Aiqgenapp';
import Tickettriageai from './Components/Dashbord/TicketTriageAI/Tickettriageai';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="aiqgenapp" element={<Aiqgenapp />} />
          <Route path="code-generation" element={<CodeGeneration />} />
          <Route path="self-healing" element={<SelfHealing />} />
          <Route path="ticket-classification" element={<TicketClassification />} />
          <Route path='ticket-triage-ai' element={<Tickettriageai/>} />
          {/* Add more routes as needed */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
