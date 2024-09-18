import React, { useState } from 'react';
import './Tickettriageai.css'; // Import your CSS file

const Tickettriageai = () => {
  const [selectedModel, setSelectedModel] = useState('mistral');
  const [creativity, setCreativity] = useState(0.0);
  const [selectedOption, setSelectedOption] = useState('TicketTriageAgent');
  const [emailContent, setEmailContent] = useState(''); // Changed email to emailContent for multi-line

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

  const handleAcknowledgement = () => {
    alert('Acknowledgement Submitted!');
  };

  return (
    <div className='tickettriageai'>
      <div className='sidebar'>
        <p>Navigation</p>

        {/* Radio Buttons */}
        <div>
          <label>
            <input
              type="radio"
              value="TicketTriageAgent"
              checked={selectedOption === 'TicketTriageAgent'}
              onChange={() => setSelectedOption('TicketTriageAgent')}
            />
            TicketTriageAgent
          </label>
        </div>

        <div>
          <label>
            <input
              type="radio"
              value="Report"
              checked={selectedOption === 'Report'}
              onChange={() => setSelectedOption('Report')}
            />
            Report
          </label>
        </div>

        {/* Model Selection Dropdown */}
        <p>Select the Model</p>
        <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
          <option value="mistral">Mistral</option>
          <option value="llama3">Llama3</option>
        </select>

        {/* Creativity Adjustment */}
        <p>Select The Creativity:</p>
        <div className='creativity-adjust'>
          <button onClick={() => handleCreativityChange(-0.01)}>-</button>
          <span className='creativity-value'>{creativity.toFixed(2)}</span>
          <button onClick={() => handleCreativityChange(0.01)}>+</button>
        </div>

        {/* Display Creativity Level */}
        <p>Creativity Level: {getCreativityLevel(creativity)}</p>
      </div>

      <div className='content'>
        <h1>Ticket Tri Age AI</h1>

        {/* Textarea for Email Content */}
        <p>Enter the Email Content:</p>
        <textarea
          placeholder="Enter email content"
          value={emailContent}
          onChange={(e) => setEmailContent(e.target.value)}
          className='email-textarea'
        />

        {/* Acknowledgement Button */}
        <p>
          <button onClick={handleAcknowledgement} className='acknowledgement-btn'>
            Acknowledgement
          </button>
        </p>
      </div>
    </div>
  );
};

export default Tickettriageai;
