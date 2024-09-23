import React, { useState } from 'react';
import axios from 'axios';

const AITCGen = () => {
  const [selectedModel, setSelectedModel] = useState('OpenAI');
  const [creativity, setCreativity] = useState(0.0);
  const [selectedTestScenario, setSelectedTestScenario] = useState('Functional');
  const [content, setContent] = useState('');
  const [generatedTestCases, setGeneratedTestCases] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to determine creativity level label
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

  // Function to change creativity value
  const handleCreativityChange = (change) => {
    setCreativity((prev) => Math.min(1.0, Math.max(0.0, prev + change)));
  };

  // Function to handle test case generation
  const handleGenerateTestCases = async () => {
    setLoading(true);
    setError(null);
    setGeneratedTestCases('');

    try {
      // Send a POST request to the backend API
      const response = await axios.post('http://localhost:8000/generate-testcases', {
        selected_model: selectedModel,
        content: content,
        test_scenario: selectedTestScenario,
        temp: creativity,
      });

      // Handle the response and set the generated test cases
      setGeneratedTestCases(response.data.zerkinScript);
    } catch (err) {
      setError('Failed to generate test cases. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="aitcgen">
      <div className="sidebar">
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
          <option value="Exploratory">Exploratory</option>
          <option value="Performance">Performance</option>
          <option value="Security">Security</option>
        </select>
      </div>

      <div className="content">
        <h1>AI TCGen</h1>

        {/* Enter Content Text Box */}
        <p>Enter Content:</p>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Enter content here..."
          className="content-textbox"
          rows={5}
          cols={50}
        />

        {/* Generate Test Cases Button */}
        <button onClick={handleGenerateTestCases} className="generate-test-btn" disabled={loading}>
          {loading ? "Generating..." : "Generate Test Cases"}
        </button>

        {/* Loading and Error States */}
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {/* Display Generated Test Cases */}
        {generatedTestCases && (
          <div className="test-cases-output">
            <h2>Generated Test Cases</h2>
            <pre>{generatedTestCases}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITCGen;
