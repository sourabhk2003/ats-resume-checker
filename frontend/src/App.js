import React, { useState } from 'react';

function App() {
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [missingKeywords, setMissingKeywords] = useState([]);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');
  const [uploading, setUploading] = useState(false);

  // ✅ HARDCODED BACKEND URL - CHANGE ONLY HERE IF NEEDED
  const apiUrl = 'https://ats-resume-checker-api.onrender.com';

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
      setError('Please upload PDF or DOCX file only');
      return;
    }

    setUploading(true);
    setError('');
    setFileName(file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/api/upload_resume`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        setResumeText(data.extracted_text);
      } else {
        setError('Failed to extract text from file');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  const analyzeResume = async () => {
    if (!resumeText || !jdText) {
      setError('Please upload resume and enter job description');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jdText
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setScore(data.analysis.ats_score);
        setMissingKeywords(data.analysis.keyword_analysis?.missing_keywords || []);
      } else {
        setError('Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setError('Cannot connect to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Arial' }}>
      <h1 style={{ textAlign: 'center', color: '#667eea' }}>📄 ATS Resume Checker</h1>
      <p style={{ textAlign: 'center' }}>Upload Resume (PDF/DOCX) or Paste Text</p>
      
      {error && (
        <div style={{ background: '#ffebee', color: '#c62828', padding: '10px', borderRadius: '5px', marginBottom: '20px' }}>
          ❌ {error}
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '10px' }}>
          <h3>📄 Upload Resume</h3>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            style={{ marginBottom: '10px', display: 'block' }}
          />
          {uploading && <p>⏳ Processing...</p>}
          {fileName && <p style={{ color: 'green' }}>✅ {fileName}</p>}
          <hr />
          <p><strong>Or paste text:</strong></p>
          <textarea
            rows="10"
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}
            placeholder="Paste your resume here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
          />
        </div>
        
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '10px' }}>
          <h3>💼 Job Description</h3>
          <textarea
            rows="15"
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}
            placeholder="Paste job description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>
      </div>
      
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <button 
          onClick={analyzeResume}
          disabled={loading}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '12px 40px',
            fontSize: '16px',
            borderRadius: '25px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Analyzing...' : 'Analyze Resume'}
        </button>
      </div>
      
      {score !== null && (
        <div style={{ marginTop: '30px', textAlign: 'center' }}>
          <h2>ATS Score: {Math.round(score)}%</h2>
          <div style={{ width: '100%', height: '30px', background: '#e0e0e0', borderRadius: '15px', overflow: 'hidden' }}>
            <div style={{ 
              width: `${score}%`, 
              height: '100%', 
              background: score > 70 ? '#4caf50' : score > 40 ? '#ff9800' : '#f44336'
            }} />
          </div>
          
          {missingKeywords.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Missing Keywords:</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
                {missingKeywords.slice(0, 10).map((kw, i) => (
                  <span key={i} style={{ background: '#f0f0f0', padding: '5px 12px', borderRadius: '20px' }}>+ {kw}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;