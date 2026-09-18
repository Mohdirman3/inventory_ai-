import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="home-page">
      <nav className="home-nav">
        <div className="home-nav-brand">📦 Inventory AI</div>
        <div className="home-nav-actions">
          <Link to="/login" className="btn btn-secondary">Sign in</Link>
          <Link to="/register" className="btn btn-primary">Get Started</Link>
        </div>
      </nav>

      <section className="home-hero">
        <div className="home-badge">Built for growing businesses</div>
        <h1>Inventory management,<br />finally made simple.</h1>
        <p>
          Track products, suppliers, and stock in real time. Let AI-driven
          reorder recommendations tell you exactly when to restock —
          before you run out.
        </p>
        <div className="home-hero-actions">
          <Link to="/register" className="btn btn-primary btn-lg">Get Started Free</Link>
          <Link to="/login" className="btn btn-secondary btn-lg">Sign In</Link>
        </div>
      </section>

      <section className="home-features">
        <div className="home-feature-card">
          <div className="home-feature-icon">📊</div>
          <h3>Real-Time Dashboard</h3>
          <p>See stock levels, top sellers, and supplier performance at a glance.</p>
        </div>
        <div className="home-feature-card">
          <div className="home-feature-icon">🤖</div>
          <h3>Smart Reordering</h3>
          <p>AI calculates exactly when to reorder based on real sales velocity and supplier lead times.</p>
        </div>
        <div className="home-feature-card">
          <div className="home-feature-icon">🔒</div>
          <h3>Role-Based Access</h3>
          <p>Admins and employees get exactly the access they need — nothing more.</p>
        </div>
        <div className="home-feature-card">
          <div className="home-feature-icon">🔗</div>
          <h3>Supplier Tracking</h3>
          <p>Monitor fulfillment rates and lead times across every supplier relationship.</p>
        </div>
      </section>

      <footer className="home-footer">
        <p>© 2026 Inventory AI. Built as a placement project.</p>
      </footer>
    </div>
  )
}

export default Home