import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'

function Profile() {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || 'null'))
  const [teamSummary, setTeamSummary] = useState(null)

  const [showEditModal, setShowEditModal] = useState(false)
  const [editForm, setEditForm] = useState({ name: '', email: '' })
  const [editError, setEditError] = useState('')

  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [passwordError, setPasswordError] = useState('')

  useEffect(() => {
    if (user?.role === 'ADMIN') {
      api.get('/auth/team-summary')
        .then((res) => setTeamSummary(res.data.data))
        .catch(() => {})
    }
  }, [])

  if (!user) return null

  const initials = user.name.charAt(0).toUpperCase()

  const openEditModal = () => {
    setEditForm({ name: user.name, email: user.email })
    setEditError('')
    setShowEditModal(true)
  }

  const handleEditSubmit = async (e) => {
    e.preventDefault()
    setEditError('')

    try {
      const response = await api.put('/auth/profile', {
        name: editForm.name,
        email: editForm.email
      })

      const updatedUser = response.data.data
      localStorage.setItem('user', JSON.stringify(updatedUser))
      setUser(updatedUser)
      toast.success('Profile updated')
      setShowEditModal(false)
    } catch (err) {
      setEditError(err.response?.data?.message || 'Failed to update profile')
    }
  }

  const openPasswordModal = () => {
    setPasswordForm({ current_password: '', new_password: '', confirm_password: '' })
    setPasswordError('')
    setShowPasswordModal(true)
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setPasswordError('')

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError('New passwords do not match')
      return
    }

    try {
      await api.put('/auth/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      })
      toast.success('Password changed successfully')
      setShowPasswordModal(false)
    } catch (err) {
      setPasswordError(err.response?.data?.message || 'Failed to change password')
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Profile</h2>
          <p className="page-subtitle">Your account details</p>
        </div>
      </div>

      <div className="profile-grid">
        <div className="card profile-card">
          <div className="profile-avatar-lg">{initials}</div>
          <h3>{user.name}</h3>
          <p className="profile-email">{user.email}</p>
          <span className={`badge ${user.role === 'ADMIN' ? 'badge-info' : 'badge-success'}`} style={{ marginTop: '8px' }}>
            {user.role === 'ADMIN' ? '🛡️ Administrator' : '👤 Employee'}
          </span>

          <div className="profile-detail-list">
            <div className="profile-detail-row">
              <span>User ID</span>
              <span>#{user.id}</span>
            </div>
            <div className="profile-detail-row">
              <span>Access Level</span>
              <span>{user.role === 'ADMIN' ? 'Full access' : 'Standard access'}</span>
            </div>
          </div>

          <div className="profile-actions">
            <button className="btn btn-primary btn-block" onClick={openEditModal}>Edit Profile</button>
            <button className="btn btn-secondary btn-block" onClick={openPasswordModal}>Change Password</button>
          </div>
        </div>

        <div className="card">
          <div className="card-title">🔑 Your Permissions</div>
          <div style={{ padding: '16px' }}>
            <ul className="permission-list">
              <li className="permission-yes">✓ View products, suppliers, inventory, sales</li>
              <li className={user.role === 'ADMIN' ? 'permission-yes' : 'permission-no'}>
                {user.role === 'ADMIN' ? '✓' : '✕'} Create, edit, delete products & suppliers
              </li>
              <li className={user.role === 'ADMIN' ? 'permission-yes' : 'permission-no'}>
                {user.role === 'ADMIN' ? '✓' : '✕'} Adjust inventory stock levels
              </li>
              <li className="permission-yes">✓ Record sales</li>
              <li className={user.role === 'ADMIN' ? 'permission-yes' : 'permission-no'}>
                {user.role === 'ADMIN' ? '✓' : '✕'} Create & receive purchase orders
              </li>
              <li className={user.role === 'ADMIN' ? 'permission-yes' : 'permission-no'}>
                {user.role === 'ADMIN' ? '✓' : '✕'} View team summary
              </li>
            </ul>
          </div>
        </div>
      </div>

      {user.role === 'ADMIN' && teamSummary && (
        <div className="card" style={{ marginTop: '16px' }}>
          <div className="card-title">👥 Team Overview</div>
          <div className="team-stats-row">
            <div className="team-stat">
              <span className="team-stat-value">{teamSummary.total_users}</span>
              <span className="team-stat-label">Total Users</span>
            </div>
            <div className="team-stat">
              <span className="team-stat-value">{teamSummary.total_admins}</span>
              <span className="team-stat-label">Admins</span>
            </div>
            <div className="team-stat">
              <span className="team-stat-value">{teamSummary.total_employees}</span>
              <span className="team-stat-label">Employees</span>
            </div>
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: '16px' }}>
        <div className="card-title">📦 About Inventory AI</div>
        <div style={{ padding: '16px' }}>
          <p className="page-subtitle" style={{ margin: 0 }}>
            An inventory management platform for tracking products, suppliers, stock,
            sales, and purchase orders — with AI-driven reorder recommendations built in.
          </p>
        </div>
      </div>

      {/* Edit profile modal */}
      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Profile</h3>
            <form onSubmit={handleEditSubmit}>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  required
                />
              </div>

              <div className="profile-role-note">
                Your role ({user.role}) can only be changed by an administrator.
              </div>

              {editError && <div className="form-error">{editError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Change password modal */}
      {showPasswordModal && (
        <div className="modal-overlay" onClick={() => setShowPasswordModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>Change Password</h3>
            <form onSubmit={handlePasswordSubmit}>
              <div className="form-group">
                <label>Current Password</label>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>New Password</label>
                <input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  required
                  minLength={6}
                />
              </div>
              <div className="form-group">
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  required
                />
              </div>

              {passwordError && <div className="form-error">{passwordError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowPasswordModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Update Password</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Profile