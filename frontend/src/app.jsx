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
    setVisualizations([]);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", formData, {
        headers: { 'Accept': 'application/json' }
      });
      const visuals = response.data.visualizations;
      if (Array.isArray(visuals)) {
        setVisualizations(visuals);
      } else {
        throw new Error("Invalid response format from server.");
      }
    } catch (err) {
      setError("Something went wrong: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div
        style={
          visualizations.length === 0
            ? styles.centeredSection
            : styles.header
        }
      >
        <h1 style={styles.title}>📊 CSV Visualization Generator</h1>
        <div style={styles.uploadSection}>
          <input type="file" accept=".csv" onChange={handleFileChange} style={styles.fileInput} />
          <button onClick={handleUpload} style={styles.uploadButton}>Generate Visuals</button>
        </div>
      </div>

      {loading && <p style={styles.loading}>Loading visualizations...</p>}
      {error && <p style={styles.error}>{error}</p>}

      {visualizations.length > 0 && (
        <div style={styles.resultsSection}>
          <h2 style={styles.sectionTitle}>Generated Visualizations</h2>
          {visualizations.map((viz, index) => (
            <div key={index} style={styles.visualizationBlock}>
              <h3 style={styles.vizTitle}>Visualization {index + 1}</h3>
              <p><strong>Summary:</strong> {viz.summary}</p>
              {viz.image ? (
                <img
                  src={`data:image/png;base64,${viz.image}`}
                  alt={`Visualization ${index + 1}`}
                  style={styles.image}
                />
              ) : (
                <p style={styles.error}>⚠️ Error generating image</p>
              )}
              <pre style={styles.codeBlock}>
                <code>{viz.code}</code>
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    fontFamily: "'Segoe UI', sans-serif",
    background: "linear-gradient(to right top, #ffe0e3, #e9f7ef, #e0f0ff, #ffe7f7)",
    minHeight: "100vh",
    padding: "2rem",
    color: "#2c3e50",
    backgroundAttachment: "fixed",
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  centeredSection: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    height: "80vh",
    textAlign: "center",
  },
  header: {
    textAlign: "center",
    marginBottom: "2rem",
  },
  title: {
    fontSize: "2.5rem",
    color: "#1e3a8a",
  },
  uploadSection: {
    marginTop: "1rem",
  },
  fileInput: {
    marginRight: "1rem",
    padding: "0.4rem",
  },
  uploadButton: {
    backgroundColor: "#2563eb",
    color: "white",
    padding: "0.5rem 1rem",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  loading: {
    textAlign: "center",
    fontWeight: "bold",
    color: "#444",
  },
  error: {
    color: "red",
    textAlign: "center",
  },
  resultsSection: {
    marginTop: "2rem",
    maxWidth: "1000px",
    marginLeft: "auto",
    marginRight: "auto",
  },
  sectionTitle: {
    fontSize: "1.8rem",
    color: "#1e3a8a",
    marginBottom: "1rem",
    textAlign: "center",
  },
  visualizationBlock: {
    backgroundColor: "white",
    borderRadius: "12px",
    padding: "1.5rem",
    marginBottom: "2rem",
    boxShadow: "0 6px 30px rgba(0,0,0,0.08)",
    maxWidth: "900px",
    marginLeft: "auto",
    marginRight: "auto"
  },
  vizTitle: {
    fontSize: "1.2rem",
    color: "#111827",
    marginBottom: "0.5rem",
  },
  image: {
    display: "block",
    margin: "1rem auto",
    maxWidth: "100%",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
  },
  codeBlock: {
    background: "#f3f4f6",
    padding: "1rem",
    borderRadius: "8px",
    overflowX: "auto",
    whiteSpace: "pre-wrap",
    fontFamily: "'Fira Code', monospace",
    fontSize: "0.9rem",
  },
};

export default App;
