import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [logs, setLogs] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeLogs = async () => {
    try {
      setLoading(true);

      const response = await axios.post(
        "http://localhost:8000/analyze",
        {
          logs: logs,
        }
      );

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("Failed to analyze logs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Kubernetes AI Assistant</h1>

      <textarea
        placeholder="Paste Kubernetes logs here..."
        value={logs}
        onChange={(e) => setLogs(e.target.value)}
      />

      <button onClick={analyzeLogs}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {result && (
        <div className="result">
          <h2>Root Cause</h2>
          <p>{result.root_cause}</p>

          <h2>Severity</h2>
          <p>{result.severity}</p>
          
          <h2>Evidence</h2>
          <ul>
            {result.evidence?.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>

          <h2>Recommendations</h2>
          <ul>
            {result.recommendations?.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;