import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  // Safely parse user from localStorage
  let user;
  try {
    user = JSON.parse(localStorage.getItem('user'));
  } catch(e) { user = null; }

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setPrediction(null);
      setError('');
    }
  };

  const handlePredict = async () => {
    if (!file) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const resp = await fetch('/predict', {
        method: 'POST',
        body: formData,
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.error || 'Prediction failed');
      }

      setPrediction({
        result: data.result,
        confidence: data.confidence,
        imageUrl: data.image_url
      });
      
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">
      <div className="dashboard-header glass-panel" style={{ padding: '1rem 2rem', marginBottom: '2rem' }}>
        <div>
          <h2>Skin Lesion Analyzer</h2>
          <p>Welcome back, {user?.email || 'User'}!</p>
        </div>
        <button onClick={handleLogout} className="btn btn-logout">Logout</button>
      </div>

      <div className="glass-panel text-center" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h3>Upload Image for Analysis</h3>
        <p className="mb-6">Our AI model will analyze the image and predict whether the lesion is Malignant or Benign.</p>

        {!preview && (
          <div className="file-input-wrapper">
            <div className="file-input-btn">
              <span style={{ fontSize: '2rem', display: 'block', marginBottom: '0.5rem' }}>📁</span>
              Click here to upload an image
            </div>
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleFileChange} 
              ref={fileInputRef}
            />
          </div>
        )}

        {preview && (
          <div>
            <img src={preview} alt="Upload Preview" className="image-preview" />
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button 
                className="btn btn-secondary" 
                onClick={() => { setFile(null); setPreview(''); setPrediction(null); }}
              >
                Choose Different Image
              </button>
              <button 
                className="btn btn-primary" 
                style={{ width: 'auto' }}
                onClick={handlePredict}
                disabled={loading}
              >
                {loading ? <span className="loader"></span> : 'Analyze Image'}
              </button>
            </div>
          </div>
        )}

        {error && <div className="error-msg mt-4">{error}</div>}

        {prediction && !loading && (
          <div className="prediction-result">
            <h3>Analysis Result</h3>
            <div className={`result-tag tag-${prediction.result.toLowerCase()}`}>
              {prediction.result}
            </div>
            <p className="mt-4" style={{ color: 'var(--text-main)' }}>
              Confidence: <strong>{prediction.confidence}%</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
