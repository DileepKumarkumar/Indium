import React, { useState } from 'react';
import './Aiqgenapp.css'; // Make sure this path is correct
import axios from 'axios';

const Aiqgenapp = () => {
  const [selectedModel, setSelectedModel] = useState('LLama3');
  const [temperature, setTemperature] = useState(0.5);
  const [selectedQuestionType, setSelectedQuestionType] = useState('Informational Questions');
  const [numOfQuestions, setNumOfQuestions] = useState(1);
  const [selectedDifficulty, setSelectedDifficulty] = useState('Easy');
  const [easyPercentage, setEasyPercentage] = useState(0);
  const [generateWithAnswers, setGenerateWithAnswers] = useState('Yes');
  const [inputMethod, setInputMethod] = useState('File Upload');
  const [query, setQuery] = useState('');
  const [file, setFile] = useState(null);
  const [contentText, setContentText] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false); // For loading state
  const [apiResponse, setApiResponse] = useState(''); // To store the API response

  // Handle changes for various states
  const handleModelChange = (e) => setSelectedModel(e.target.value);
  const handleQuestionTypeChange = (e) => setSelectedQuestionType(e.target.value);
  const decreaseTemperature = () => setTemperature((prevTemp) => Math.max(0, (prevTemp - 0.01).toFixed(2)));
  const increaseTemperature = () => setTemperature((prevTemp) => Math.min(1, (parseFloat(prevTemp) + 0.01).toFixed(2)));
  const handleDifficultyChange = (e) => setSelectedDifficulty(e.target.value);
  const decreasePercentage = () => setEasyPercentage((prevPercentage) => Math.max(0, prevPercentage - 1));
  const increasePercentage = () => setEasyPercentage((prevPercentage) => Math.min(100, prevPercentage + 1));
  const handleGenerateWithAnswersChange = (e) => setGenerateWithAnswers(e.target.value);
  const handleInputMethodChange = (e) => setInputMethod(e.target.value);
  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleQueryChange = (e) => setQuery(e.target.value);
  const handleContentTextChange = (e) => setContentText(e.target.value);
  const handleUrlChange = (e) => setUrl(e.target.value);

  // Function to map temperature to creativity level
  const getCreativityLevel = (temp) => {
    if (temp === 0.0) return 'Less Creativity';
    if (temp <= 0.1) return 'Very Low Creativity';
    if (temp <= 0.2) return 'Low Creativity';
    if (temp <= 0.3) return 'Slightly Low Creativity';
    if (temp <= 0.4) return 'Moderate Creativity';
    if (temp <= 0.5) return 'Average Creativity';
    if (temp <= 0.6) return 'Above Average Creativity';
    if (temp <= 0.7) return 'Slightly High Creativity';
    if (temp <= 0.8) return 'High Creativity';
    if (temp <= 0.9) return 'Very High Creativity';
    if (temp === 1.0) return 'Max Creativity';
  };

  // Function to handle the API call
  const generateQuestions = async () => {
    console.log('Generate Questions button clicked');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('model', selectedModel);
      formData.append('temperature', Number(temperature)); // Ensure this is a number
      formData.append('questionType', selectedQuestionType);
      formData.append('numOfQuestions', Number(numOfQuestions)); // Ensure this is a number
      formData.append('difficulty', selectedDifficulty);
      formData.append('easyPercentage', Number(easyPercentage)); // Ensure this is a number
      formData.append('generateWithAnswers', generateWithAnswers); // Ensure this is 'No' or 'Yes' based on the selection

      if (inputMethod === 'Content Text' && contentText) {
        formData.append('contentText', contentText);
      } else if (inputMethod === 'URL' && url) {
        formData.append('url', url);
      } else if (inputMethod === 'File Upload' && file) {
        formData.append('file', file);
      }

      console.log('FormData before sending:', [...formData.entries()]);

      const response = await axios.post('http://127.0.0.1:8000/query', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      console.log('Response:', response.data);
      setApiResponse(response.data.response);
    } catch (error) {
      console.error('Error fetching data from API:', error.response?.data || error.message);
      setApiResponse(error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  // Check if the "Generate Questions" button should be enabled
  const isButtonDisabled = () => {
    if (inputMethod === 'File Upload' && file) return false;
    if (inputMethod === 'URL' && url) return false;
    if (inputMethod === 'Content Text' && contentText) return false;
    return true;
  };

  return (
    <div className='aiqgen'>
      <div className='sidebar'>
        <p className='sidebar-label'>Select The Model:</p>
        <select className='model-dropdown' value={selectedModel} onChange={handleModelChange}>
          <option value='LLama3'>LLama3</option>
          <option value='Mistral'>Mistral</option>
          <option value='LLama3.1'>LLama3.1</option>
        </select>

        <p className="sidebar-label">Select A Temperature Value</p>
        <div className='temperature-control'>
          <button className="temp-button" onClick={decreaseTemperature}>-</button>
          <span className="temperature-value">{temperature}</span>
          <button className="temp-button" onClick={increaseTemperature}>+</button>
        </div>

        <p className="creativity-level">Creativity Level: {getCreativityLevel(temperature)}</p>

        <p className="sidebar-label">Select Question Type:</p>
        <select className="question-type-dropdown" value={selectedQuestionType} onChange={handleQuestionTypeChange}>
          {/* Add other options here */}
          <option value="Informational Questions">Informational Questions</option>
          {/* other options */}
        </select>

        <p className="sidebar-label">No. Of Questions:</p>
        <input
          type="number"
          min="1"
          className="questions-input"
          value={numOfQuestions}
          onChange={(e) => setNumOfQuestions(parseInt(e.target.value))}
        />

        <p className="sidebar-label">Select Difficulty Level:</p>
        <select className="difficulty-dropdown" value={selectedDifficulty} onChange={handleDifficultyChange}>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>

        <p className="sidebar-label">Percentage for Easy:</p>
        <div className='percentage-control'>
          <button className="percentage-button" onClick={decreasePercentage}>-</button>
          <span className="percentage-value">{easyPercentage}%</span>
          <button className="percentage-button" onClick={increasePercentage}>+</button>
        </div>

        <p className="sidebar-label">Generate With Answers or Not:</p>
        <select className="answers-dropdown" value={generateWithAnswers} onChange={handleGenerateWithAnswersChange}>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      <div className='content'>
        <h1>AIQGen App</h1>

        <p>Select Input Method:</p>
        <div className='input-methods'>
          <label>
            <input
              type="radio"
              value="File Upload"
              checked={inputMethod === 'File Upload'}
              onChange={handleInputMethodChange}
            />
            File Upload
          </label>
          <label>
            <input
              type="radio"
              value="Content Text"
              checked={inputMethod === 'Content Text'}
              onChange={handleInputMethodChange}
            />
            Content Text
          </label>
          <label>
            <input
              type="radio"
              value="URL"
              checked={inputMethod === 'URL'}
              onChange={handleInputMethodChange}
            />
            URL
          </label>
        </div>

        {inputMethod === 'File Upload' && (
          <>
            <p>Upload Here:</p>
            <input
              type="file"
              onChange={handleFileChange}
            />
          </>
        )}

        {inputMethod === 'Content Text' && (
          <>
            <p>Enter Content Text:</p>
            <textarea
              value={contentText}
              onChange={handleContentTextChange}
              rows="4"
              placeholder="Type your content here..."
            />
          </>
        )}

        {inputMethod === 'URL' && (
          <>
            <p>Enter URL:</p>
            <input
              type="url"
              value={url}
              onChange={handleUrlChange}
              placeholder="http://example.com"
            />
          </>
        )}

        <p>Enter Query:</p>
        <textarea
          value={query}
          onChange={handleQueryChange}
          rows="4"
          placeholder="Type your query here..."
        />

        <button onClick={generateQuestions} disabled={loading || isButtonDisabled()}>
          {loading ? 'Generating...' : 'Generate Questions'}
        </button>

        <div className='api-response-container'>
          <h2>API Response:</h2>
          <pre>{apiResponse}</pre>
        </div>
      </div>
    </div>
  );
};

export default Aiqgenapp;
