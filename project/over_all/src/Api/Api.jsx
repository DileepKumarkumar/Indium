const API_BASE_URL = 'http://localhost:5000'; // Change to your backend URL

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};

export const scrapeUrl = async (url) => {
  const response = await fetch(`${API_BASE_URL}/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  return response.json();
};

export const processQuery = async (data) => {
  const response = await fetch(`${API_BASE_URL}/process-query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
