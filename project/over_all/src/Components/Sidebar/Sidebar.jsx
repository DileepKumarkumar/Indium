import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaTachometerAlt, FaProjectDiagram, FaRobot, FaClipboardList, FaTasks, FaBug, FaCogs, FaNetworkWired } from 'react-icons/fa'; // Importing icons
import './Sidebar.css'; // Import the CSS file

const Sidebar = () => {
  // State for managing dropdown visibility
  const [isIntegrationsOpen, setIsIntegrationsOpen] = useState(false);
  const [isAgentsOpen, setIsAgentsOpen] = useState(false);
  const [isUseCasesOpen, setIsUseCasesOpen] = useState(false);

  // Toggle functions for each dropdown
  const toggleIntegrations = () => setIsIntegrationsOpen(!isIntegrationsOpen);
  const toggleAgents = () => setIsAgentsOpen(!isAgentsOpen);
  const toggleUseCases = () => setIsUseCasesOpen(!isUseCasesOpen);

  return (
    <div className="sidebar">
      <h2>Projects</h2>
      <ul className="sidebarLinks">
        
        <li>
          <Link to="/dashboard" className="sidebarLink">
            <FaTachometerAlt /> Dashboard
          </Link>
        </li>

        {/* Integrations Dropdown */}
        <li>
          <div className="sidebarLink" onClick={toggleIntegrations}>
            <FaCogs /> Integrations
          </div>
          {isIntegrationsOpen && (
            <ul className="submenu">
              <li><Link to="/project-integration" className="sidebarLink">Project Integration</Link></li>
              <li><Link to="/model-integration" className="sidebarLink">Model Integration</Link></li>
              <li><Link to="/pipeline-integration" className="sidebarLink">Pipeline Integration</Link></li>
            </ul>
          )}
        </li>

        {/* Agents Dropdown */}
        <li>
          <div className="sidebarLink" onClick={toggleAgents}>
            <FaRobot /> Agents
          </div>
          {isAgentsOpen && (
            <ul className="submenu">
              <li><Link to="/langchain" className="sidebarLink">Langchain</Link></li>
            </ul>
          )}
        </li>

        {/* Use Cases Dropdown */}
        <li>
          <div className="sidebarLink" onClick={toggleUseCases}>
            <FaClipboardList /> Use Cases
          </div>
          {isUseCasesOpen && (
            <ul className="submenu">
              <li><Link to="/aiqgenapp" className="sidebarLink">AIQGen App</Link></li>
              <li><Link to="/Test-Case-Generation" className="sidebarLink">Test Case Generation</Link></li>
              <li><Link to="/AItcgen" className="sidebarLink">AI TCGen</Link></li>
              <li><Link to="/ticket-classification" className="sidebarLink">Ticket Classification</Link></li>
              <li><Link to="/ticket-triage-ai" className="sidebarLink">Ticket Triage AI</Link></li>
            </ul>
          )}
        </li>

        {/* Additional links can be added here */}
      </ul>
    </div>
  );
};

export default Sidebar;
