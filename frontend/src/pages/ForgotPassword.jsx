import { Link } from 'react-router-dom'

function ForgotPassword() {
  return (
    <div className="login-page">
      <div className="login-card" style={{ maxWidth: '420px', margin: '0 auto' }}>
        <h1>Reset your password</h1>
        <p className="subtitle">
          Password reset isn't available yet — please contact your administrator to reset your password.
        </p>
        <Link to="/login" className="btn btn-secondary btn-block" style={{ textAlign: 'center', textDecoration: 'none' }}>
          Back to login
        </Link>
      </div>
    </div>
  )
}

export default ForgotPassword