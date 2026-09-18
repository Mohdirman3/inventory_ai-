import { useState } from 'react'
import api from '../api/axios'
import { useNavigate, Link } from 'react-router-dom'

function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    try {
      await api.post('/auth/register', { name, email, password, role: 'EMPLOYEE' })
      setSuccess(true)
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed')
    }
  }

  return (
    <div className="login-page">
      <div className="login-card" style={{ maxWidth: '420px', margin: '0 auto' }}>
        <h1>Create your account</h1>
        <p className="subtitle">New accounts are created with Employee access</p>

        {success ? (
          <div className="form-error" style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)' }}>
            Account created! Redirecting to login…
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Email address</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>

            {error && <div className="form-error">{error}</div>}

            <button type="submit" className="btn btn-primary btn-block">Create account</button>
          </form>
        )}

        <p className="login-footer-text">
          Already have an account? <Link to="/login" className="inline-link">Sign in</Link>
        </p>
      </div>
    </div>
  )
}

export default Register