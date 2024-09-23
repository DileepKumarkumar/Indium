import React, { useState } from 'react';
import './TestCaseGeneration.css'; // Ensure you have the CSS file

const TestCaseGeneration = () => {
  const [selectedOrganization, setSelectedOrganization] = useState('revathyb');
  const [selectedApiVersion, setSelectedApiVersion] = useState('7.1');
  const [selectedProjectName, setSelectedProjectName] = useState('IndiumSeleniumDemo');
  const [selectedUserStory, setSelectedUserStory] = useState('userstory1');
  const [selectedModel, setSelectedModel] = useState('OpenAI');
  const [creativity, setCreativity] = useState(0.0);
  const [selectedTestScenario, setSelectedTestScenario] = useState('Functional');
  const [selectedFormat, setSelectedFormat] = useState('Format 1');
  const [showAdditionalButtons, setShowAdditionalButtons] = useState(false);

  const getCreativityLevel = (temp) => {
    if (temp === 0.0) return "Less Creativity";
    if (temp <= 0.1) return "Very Low Creativity";
    if (temp <= 0.2) return "Low Creativity";
    if (temp <= 0.3) return "Slightly Low Creativity";
    if (temp <= 0.4) return "Moderate Creativity";
    if (temp <= 0.5) return "Average Creativity";
    if (temp <= 0.6) return "Above Average Creativity";
    if (temp <= 0.7) return "Slightly High Creativity";
    if (temp <= 0.8) return "High Creativity";
    if (temp <= 0.9) return "Very High Creativity";
    if (temp === 1.0) return "Max Creativity";
  };

  const handleCreativityChange = (change) => {
    setCreativity(prev => Math.min(1.0, Math.max(0.0, prev + change)));
  };

  const handleFetchAcceptanceCriteria = () => {
    setShowAdditionalButtons(true);
  };

  return (
    <div className="testcase-generation">
      <div className="sidebar">
        <p>Select The Organization:</p>
        <select value={selectedOrganization} onChange={(e) => setSelectedOrganization(e.target.value)}>
          <option value="revathyb">revathyb</option>
        </select>

        <p>API Version:</p>
        <select value={selectedApiVersion} onChange={(e) => setSelectedApiVersion(e.target.value)}>
          <option value="7.1">api-version=7.1</option>
        </select>

        <p>Project Name:</p>
        <select value={selectedProjectName} onChange={(e) => setSelectedProjectName(e.target.value)}>
          <option value="IndiumSeleniumDemo">IndiumSeleniumDemo</option>
        </select>

        <p>Select the User Story:</p>
        <select value={selectedUserStory} onChange={(e) => setSelectedUserStory(e.target.value)}>
          <option value="userstory1">userstory1</option>
        </select>

        <p>Select the Model:</p>
        <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
          <option value="OpenAI">OpenAI</option>
          <option value="llama3">llama3</option>
          <option value="misteral">misteral</option>
        </select>

        {/* Creativity Adjustment */}
        <p>Select The Creativity:</p>
        <div className="creativity-adjust">
          <button onClick={() => handleCreativityChange(-0.01)}>-</button>
          <span className="creativity-value">{creativity.toFixed(2)}</span>
          <button onClick={() => handleCreativityChange(0.01)}>+</button>
        </div>
        <p>Creativity Level: {getCreativityLevel(creativity)}</p>
        <p>Select the Test Scenarios:</p>
        
        <select value={selectedTestScenario} onChange={(e) => setSelectedTestScenario(e.target.value)}>
          <option value="Functional">Functional</option>
        </select>

        <p>Select the Format for Update:</p>
        <select value={selectedFormat} onChange={(e) => setSelectedFormat(e.target.value)}>
          <option value="Format 1">Format 1</option>
          <option value="Format 2">Format 2</option>
        </select>
      </div>

      <div className="content">
        <h1>Test Case Generation</h1>



        {/* Fetch Acceptance Criteria Button */}
        <button onClick={handleFetchAcceptanceCriteria} className="fetch-acceptance-btn">
          Fetch Acceptance Criteria
        </button>

        {/* Conditionally Rendered Buttons */}
        {showAdditionalButtons && (
          <div className="additional-buttons">
            <button className="generate-test-btn">Generate Test Cases</button>
            <button className="update-ado-btn">Update ADO</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestCaseGeneration;
