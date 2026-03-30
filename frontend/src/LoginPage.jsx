import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const resp = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.error || 'Failed to login');
      }

      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/dashboard');
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
          <h1>Welcome Back</h1>
          <p>Login to access your skin analysis dashboard</p>
        </div>
        
        <form onSubmit={handleLogin}>
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
            />
          </div>

          {error && <div className="error-msg mb-6 text-center">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <span className="loader"></span> : 'Sign In'}
          </button>
        </form>

        <div className="text-center mt-4">
          <p>Don't have an account? <Link to="/register" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Register Here</Link></p>
        </div>
      </div>
    </div>
  );
}
