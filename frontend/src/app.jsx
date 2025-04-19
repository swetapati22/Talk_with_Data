import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [visualizations, setVisualizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a CSV file to upload.");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/analyze", formData);
      setVisualizations(response.data.visualizations);
    } catch (err) {
      setError("Something went wrong: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      <h1>📊 CSV Visualization Generator</h1>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "1rem" }}>
        Generate Visuals
      </button>

      {loading && <p>Loading visualizations...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {visualizations.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Generated Visualizations</h2>
          {visualizations.map((viz, index) => (
            <div key={index} style={{ marginBottom: "2rem" }}>
              {viz.image ? (
                <img
                  src={`data:image/png;base64,${viz.image}`}
                  alt={`Visualization ${index + 1}`}
                  style={{ maxWidth: "100%", border: "1px solid #ccc", borderRadius: "8px" }}
                />
              ) : (
                <p style={{ color: "red" }}>⚠️ Error generating image</p>
              )}
              <pre style={{ background: "#f4f4f4", padding: "1rem", borderRadius: "8px" }}>
                <code>{viz.code}</code>
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
