import { useEffect, useState } from 'react'
import api from '../api/axios'

function Suppliers() {
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', email: '', phone: '', lead_time_days: '' })
  const [formError, setFormError] = useState('')

  const fetchSuppliers = async () => {
    setLoading(true)
    try {
      const response = await api.get('/suppliers/')
      setSuppliers(response.data.data)
    } catch (err) {
      console.error('Failed to load suppliers:', err)
      setError('Failed to load suppliers')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSuppliers()
  }, [])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ name: '', email: '', phone: '', lead_time_days: '' })
    setFormError('')
    setShowModal(true)
  }

  const openEditModal = (supplier) => {
    setEditingId(supplier.id)
    setForm({
      name: supplier.name,
      email: supplier.email,
      phone: supplier.phone,
      lead_time_days: supplier.lead_time_days
    })
    setFormError('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    const payload = {
      name: form.name,
      email: form.email,
      phone: form.phone,
      lead_time_days: parseInt(form.lead_time_days)
    }

    try {
      if (editingId) {
        await api.put(`/suppliers/${editingId}`, payload)
      } else {
        await api.post('/suppliers/', payload)
      }
      setShowModal(false)
      fetchSuppliers()
    } catch (err) {
      setFormError(err.response?.data?.message || 'Something went wrong')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Deactivate this supplier?')) return
    try {
      await api.delete(`/suppliers/${id}`)
      fetchSuppliers()
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete supplier')
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Suppliers</h2>
          <p className="page-subtitle">Manage your supplier relationships</p>
        </div>
        <button className="btn btn-primary" onClick={openCreateModal}>+ New Supplier</button>
      </div>

      <div className="card">
        {loading && <p className="state-message">Loading suppliers…</p>}
        {error && <p className="state-message error">{error}</p>}

        {!loading && !error && (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Lead Time</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {suppliers.length === 0 ? (
                  <tr><td colSpan="5" className="state-message">No suppliers yet</td></tr>
                ) : (
                  suppliers.map((supplier) => (
                    <tr key={supplier.id}>
                      <td>{supplier.name}</td>
                      <td>{supplier.email}</td>
                      <td>{supplier.phone}</td>
                      <td>{supplier.lead_time_days} days</td>
                      <td>
                        <div className="action-buttons">
                          <button className="icon-btn" onClick={() => openEditModal(supplier)}>Edit</button>
                          <button className="icon-btn danger" onClick={() => handleDelete(supplier.id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>{editingId ? 'Edit Supplier' : 'New Supplier'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Lead Time (days)</label>
                <input
                  type="number"
                  min="0"
                  value={form.lead_time_days}
                  onChange={(e) => setForm({ ...form, lead_time_days: e.target.value })}
                  required
                />
              </div>

              {formError && <div className="form-error">{formError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Suppliers