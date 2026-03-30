import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const resp = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.error || 'Failed to register');
      }

      setSuccess('Registration successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="center-flex">
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px' }}>
        <div className="text-center mb-6">
          <h1>Join Us</h1>
          <p>Create an account to analyze skin lesions</p>
        </div>
        
        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label>Name</label>
            <input 
              type="text" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              placeholder="Your Full Name"
              required 
            />
          </div>
          
          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              placeholder="you@domain.com"
              required 
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              placeholder="••••••••"
              required 
              minLength={6}
            />
          </div>

          {error && <div className="error-msg mb-6 text-center">{error}</div>}
          {success && <div className="success-msg mb-6 text-center">{success}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading || success !== ''}>
            {loading ? <span className="loader"></span> : 'Create Account'}
          </button>
        </form>

        <div className="text-center mt-4">
          <p>Already have an account? <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Sign In</Link></p>
        </div>
      </div>
    </div>
  );
}
