import { useState } from 'react'
import api from '../api/axios'
import { useNavigate, Link } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login', { email, password })

      if (response.data.success) {
        localStorage.setItem('token', response.data.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.data.user))
        navigate('/dashboard')
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <nav className="login-topbar">
        <div className="login-topbar-brand">📦 Inventory AI</div>
      </nav>

      <div className="login-split">
        <div className="login-brand-panel">
          <div className="login-badge">Enterprise Inventory Platform</div>
          <h1>Run your inventory<br />on autopilot.</h1>
          <p>
            Track stock in real time, automate reorder decisions with
            demand-aware recommendations, and keep every supplier
            accountable — all from one dashboard.
          </p>
          <ul className="login-feature-list">
            <li><span className="feature-check">✓</span> Real-time inventory tracking</li>
            <li><span className="feature-check">✓</span> AI-driven reorder recommendations</li>
            <li><span className="feature-check">✓</span> Supplier performance insights</li>
            <li><span className="feature-check">✓</span> Role-based access control</li>
          </ul>
        </div>

        <div className="login-card">
          <h1>Welcome back</h1>
          <p className="subtitle">Sign in to your account to continue</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="form-group">
              <div className="form-label-row">
                <label>Password</label>
                <Link to="/forgot-password" className="inline-link">Forgot password?</Link>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && <div className="form-error">{error}</div>}

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="login-footer-text">
            Don't have an account? <Link to="/register" className="inline-link">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login