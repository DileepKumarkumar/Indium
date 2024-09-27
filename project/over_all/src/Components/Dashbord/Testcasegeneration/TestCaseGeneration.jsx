import React, { useState, useEffect } from "react";
import "./TestCaseGeneration.css"; // Ensure you have the CSS file

const TestCaseGeneration = () => {
  const [selectedOrganization, setSelectedOrganization] = useState("revathyb");
  const [selectedApiVersion, setSelectedApiVersion] = useState("7.1");
  const [projects, setProjects] = useState([]);
  const [selectedProjectName, setSelectedProjectName] = useState("");
  const [userStories, setUserStories] = useState([]);
  const [selectedUserStory, setSelectedUserStory] = useState("");
  const [selectedModel, setSelectedModel] = useState("OpenAI");
  const [creativity, setCreativity] = useState(0.3);
  const [selectedTestScenario, setSelectedTestScenario] =
    useState("Functional");
  const [selectedFormat, setSelectedFormat] = useState("Gherkin Format");
  const [loading, setLoading] = useState(false);
  const [acceptanceCriterias, setAcceptanceCriterias] = useState([]); // State for acceptance criteria
  const [error, setError] = useState(null);
  const [userStoryIds, setUserStoryIds] = useState([]); // Store the IDs corresponding to the user stories

  const [descriptions, setDescriptions] = useState([]); // State for descriptions
  const [generatedTestCases, setGeneratedTestCases] = useState("");
  const [statusMessage, setStatusMessage] = useState(""); // State to hold the status message

  const [plainText, setPlainText] = useState("");
  const [key, setKey] = useState("");
  const [value, setValue] = useState(0);
  const [apiKey, setApiKey] = useState("");
  const [temp, setTemp] = useState(0.5);
  const [result, setResult] = useState(null);
  // Fetch projects from FastAPI
  const fetchProjects = async () => {
    setLoading(true);
    setError(""); // Reset error state
    try {
      const response = await fetch("http://localhost:8000/projects");
      if (!response.ok) throw new Error("Failed to fetch projects");
      const data = await response.json();
      setProjects(data.projects || []); // Set projects, default to empty array
    } catch (error) {
      setError(error.message); // Set error message
    } finally {
      setLoading(false); // Stop loading
    }
  };

  // Fetch projects once on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Fetch user stories whenever the selected project name changes
  useEffect(() => {
    if (selectedProjectName) {
      fetchUserStories(selectedProjectName);
    }
  }, [selectedProjectName]);

  const fetchUserStories = async (projectName) => {
    try {
      const response = await fetch(
        `http://localhost:8000/user-stories/${projectName}`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch user stories. Status: ${response.status}`
        );
      }
      const data = await response.json();
      console.log("Fetched User Stories:", data.user_stories);

      const ids = extractWorkItemIds(data.user_stories); // Extract the IDs from stories
      console.log("Extracted Work Item IDs:", ids);

      setUserStories(data.user_stories || []); // Store the full user story list
      setSelectedStoryIds(ids); // Store the extracted IDs
    } catch (error) {
      setError(error.message);
    }
  };

  // Function to extract work item IDs from user stories
  const extractWorkItemIds = (stories) => {
    return stories.map((story) => {
      const idPart = story.split(",")[0]; // Extract 'ID: <number>' part
      const workItemId = idPart.split(" ")[1]; // Get the number part after 'ID:'
      return parseInt(workItemId, 10); // Convert it to an integer
    });
  };

  const decodeHtml = (html) => {
    const txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
  };

  // Fetch acceptance criteria and description for the selected user story
  const fetchAcceptanceCriteria = async (selectedUserStoryId) => {
    try {
      const response = await fetch(
        "http://localhost:8000/acceptance-criteria",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_story_ids: [selectedUserStoryId],
            pat: "",
            base_url: "https://dev.azure.com/revathyb",
            api_version: "7.1",
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Fetched acceptance criteria:", data);

      // Update state with the fetched data
      setAcceptanceCriterias(data.acceptance_criterias || []); // Set acceptance criteria
      setDescriptions(data.descriptions || []); // Set descriptions
    } catch (error) {
      console.error("Error fetching acceptance criteria:", error);
      setError(error.message);
    }
  };

  const getCreativityLevel = (temp) => {
    const levels = {
      0.0: "Less Creativity",
      0.1: "Very Low Creativity",
      0.2: "Low Creativity",
      0.3: "Slightly Low Creativity",
      0.4: "Moderate Creativity",
      0.5: "Average Creativity",
      0.6: "Above Average Creativity",
      0.7: "Slightly High Creativity",
      0.8: "High Creativity",
      0.9: "Very High Creativity",
      1.0: "Max Creativity",
    };
    return levels[temp] || "Unknown";
  };
  const handleCreativityChange = (delta) => {
    setCreativity((prev) => Math.max(0, Math.min(1, prev + delta)));
  };

  // Function to handle generating test cases
  const handleGenerateTestCases = async () => {
    setLoading(true);
    setStatusMessage("Triggered Ollama llama3 and waiting for the output..."); // Message when request is triggered

    const requestData = {
      model: "llama3",
      temperature: creativity,
      testScenario: selectedTestScenario,
      format: selectedFormat,
      description: descriptions[0],
      acceptanceCriteria: acceptanceCriterias[0],
    };

    try {
      const response = await fetch(
        "http://localhost:8000/generate-test-cases",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setGeneratedTestCases(result.test_cases);
      setStatusMessage("Test cases generated successfully!"); // Update message on success
    } catch (error) {
      console.error("Error generating test cases:", error);
      setStatusMessage("Error occurred while generating test cases.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="testcase-generation">
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      <div className="sidebar">
        <p>Select The Organization:</p>
        <select
          value={selectedOrganization}
          onChange={(e) => setSelectedOrganization(e.target.value)}
        >
          <option value="revathyb">revathyb</option>
        </select>

        <p>API Version:</p>
        <select
          value={selectedApiVersion}
          onChange={(e) => setSelectedApiVersion(e.target.value)}
        >
          <option value="7.1">api-version=7.1</option>
        </select>

        <p>Project Name:</p>
        <select
          value={selectedProjectName}
          onChange={(e) => setSelectedProjectName(e.target.value)}
        >
          {projects.map((project) => (
            <option key={project} value={project}>
              {project}
            </option>
          ))}
        </select>

        <p>Select the User Story:</p>
        <select
          value={selectedUserStory}
          onChange={(e) => setSelectedUserStory(e.target.value)} // Update selected user story
          disabled={loading || userStories.length === 0} // Disable if loading or no stories
        >
          <option value="">--Select a User Story--</option>
          {userStories.length > 0 ? (
            userStories.map((story, index) => {
              const storyId = story.split(", ")[0].split(": ")[1]; // Extract ID from the story string
              return (
                <option key={index} value={storyId}>
                  {story}
                </option> // Use the ID as the value
              );
            })
          ) : (
            <option value="">No user stories available</option>
          )}
        </select>

        <p>Select the Model:</p>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
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
        <select
          value={selectedTestScenario}
          onChange={(e) => setSelectedTestScenario(e.target.value)}
        >
          <option value="Functional">Functional</option>
          <option value="Exploratory">Exploratory</option>
          <option value="Performance">Performance</option>
          <option value="Security">Security</option>
        </select>

        <p>Select the Format for Update:</p>
        <select
          value={selectedFormat}
          onChange={(e) => setSelectedFormat(e.target.value)}
        >
          <option value="Gherkin Format">Gherkin Format</option>
          <option value="Text Format">Text Format</option>
        </select>
      </div>

      <div className="content">
        <button
          onClick={() => fetchAcceptanceCriteria(selectedUserStory)}
          disabled={!selectedUserStory || loading}
        >
          Fetch Acceptance Criteria
        </button>

        {/* Render acceptance criteria and descriptions */}
        <div className="output">
          {descriptions.length > 0 && (
            <div>
              <h3>Description:</h3>
              {descriptions.map((description, index) => (
                <p key={index}>{decodeHtml(description)}</p> // Decode before rendering
              ))}
            </div>
          )}
          {acceptanceCriterias.length > 0 ? (
            <div>
              <h3>Acceptance Criteria:</h3>
              <ul>
                {acceptanceCriterias.map((criteria, index) => (
                  <li key={index}>{decodeHtml(criteria)}</li> // Decode before rendering
                ))}
              </ul>
            </div>
          ) : (
            <p>No acceptance criteria available.</p>
          )}
        </div>
        <button onClick={handleGenerateTestCases} disabled={loading}>
          {loading ? "Generating..." : "Generate Test Cases"}
        </button>

        {/* Display the status message */}
        <h3>Status: {statusMessage}</h3>

        <h3>Generated Test Cases:</h3>
        {loading ? (
          <p>Loading test cases...</p>
        ) : generatedTestCases ? (
          <pre>{generatedTestCases}</pre>
        ) : (
          <p>No test cases generated yet.</p>
        )}
      </div>
    </div>
  );
};

export default TestCaseGeneration;
