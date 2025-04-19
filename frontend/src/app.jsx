import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [image, setImage] = useState(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    setLoading(true);
    setError("");
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/analyze", formData);
      setImage(`data:image/png;base64,${response.data.image}`);
      setCode(response.data.code);
    } catch (err) {
      setError("Something went wrong: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2em", fontFamily: "Arial, sans-serif" }}>
      <h2>📊 PromptAnalytics</h2>
      <input type="file" onChange={handleUpload} />
      
      {loading && <p>Loading analysis from Gemini AI...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      
      {image && (
        <>
          <h3>🔍 Data Visualization</h3>
          <img src={image} alt="Chart" style={{ maxWidth: "100%", marginTop: "1em" }} />
        </>
      )}

      {code && (
        <>
          <h3 style={{ marginTop: "2em" }}>🧠 Gemini Generated Code</h3>
          <pre style={{ background: "#f4f4f4", padding: "1em", borderRadius: "8px" }}>
            <code>{code}</code>
          </pre>
        </>
      )}
    </div>
  );
}

export default App;
