import { Link, useNavigate, useLocation } from 'react-router-dom'

function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const initials = user?.name ? user.name.charAt(0).toUpperCase() : '?'

  const links = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/products', label: 'Products' },
    { to: '/suppliers', label: 'Suppliers' },
    { to: '/inventory', label: 'Inventory' },
    { to: '/sales', label: 'Sales' },
    { to: '/purchase-orders', label: 'Purchase Orders' },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <span className="navbar-brand">📦 Inventory AI</span>
        <div className="navbar-links">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={location.pathname === link.to ? 'active' : ''}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
      <div className="navbar-user">
        {user && (
          <>
            <Link to="/profile" className="user-avatar">{initials}</Link>
            <span>{user.name} · {user.role}</span>
          </>
        )}
        <button className="btn btn-secondary" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}

export default Navbar