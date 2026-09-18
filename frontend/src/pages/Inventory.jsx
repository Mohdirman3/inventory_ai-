import { useEffect, useState } from 'react'
import api from '../api/axios'

function Inventory() {
  const [items, setItems] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({ product_id: '', quantity: '' })
  const [createError, setCreateError] = useState('')

  const [adjustTarget, setAdjustTarget] = useState(null) // { product_id, mode: 'add'|'remove'|'set' }
  const [adjustAmount, setAdjustAmount] = useState('')
  const [adjustError, setAdjustError] = useState('')

  const fetchInventory = async () => {
    setLoading(true)
    try {
      const response = await api.get('/inventory/')
      setItems(response.data.data)
    } catch (err) {
      console.error('Failed to load inventory:', err)
      setError('Failed to load inventory')
    } finally {
      setLoading(false)
    }
  }

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/')
      setProducts(response.data.data)
    } catch (err) {
      console.error('Failed to load products:', err)
    }
  }

  useEffect(() => {
    fetchInventory()
    fetchProducts()
  }, [])

  const getProductName = (id) => {
    const p = products.find((p) => p.id === id)
    return p ? p.name : `#${id}`
  }

  // Products that don't yet have an inventory record — for the create dropdown
  const productsWithoutInventory = products.filter(
    (p) => !items.some((i) => i.product_id === p.id)
  )

  const openCreateModal = () => {
    setCreateForm({ product_id: '', quantity: '' })
    setCreateError('')
    setShowCreateModal(true)
  }

  const handleCreateSubmit = async (e) => {
    e.preventDefault()
    setCreateError('')
    try {
      await api.post('/inventory/', {
        product_id: parseInt(createForm.product_id),
        quantity: parseInt(createForm.quantity)
      })
      setShowCreateModal(false)
      fetchInventory()
    } catch (err) {
      setCreateError(err.response?.data?.message || 'Failed to create record')
    }
  }

  const openAdjustModal = (item, mode) => {
    setAdjustTarget({ ...item, mode })
    setAdjustAmount('')
    setAdjustError('')
  }

  const handleAdjustSubmit = async (e) => {
    e.preventDefault()
    setAdjustError('')
    const amount = parseInt(adjustAmount)

    try {
      if (adjustTarget.mode === 'set') {
        await api.put(`/inventory/${adjustTarget.product_id}`, { quantity: amount })
      } else if (adjustTarget.mode === 'add') {
        await api.post(`/inventory/${adjustTarget.product_id}/add`, { quantity: amount })
      } else if (adjustTarget.mode === 'remove') {
        await api.post(`/inventory/${adjustTarget.product_id}/remove`, { quantity: amount })
      }
      setAdjustTarget(null)
      fetchInventory()
    } catch (err) {
      setAdjustError(err.response?.data?.message || 'Failed to update stock')
    }
  }

  const modeLabel = {
    add: 'Add Stock',
    remove: 'Remove Stock',
    set: 'Set Exact Quantity'
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Inventory</h2>
          <p className="page-subtitle">Track and adjust stock levels</p>
        </div>
   {productsWithoutInventory.length === 0 && products.length > 0 ? (
  <button className="btn btn-secondary" disabled>
    All products have stock records
  </button>
) : productsWithoutInventory.length === 0 && products.length === 0 ? (
  <a href="/products" className="btn btn-primary">
    Add a product first →
  </a>
) : (
  <button className="btn btn-primary" onClick={openCreateModal}>
    + New Stock Record
  </button>
)}
      </div>

      <div className="card">
        {loading && <p className="state-message">Loading inventory…</p>}
        {error && <p className="state-message error">{error}</p>}

        {!loading && !error && (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Last Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.product_name || getProductName(item.product_id)}</td>
                    <td>
                      {item.quantity}
                      {item.quantity <= 10 && (
                        <span className="badge badge-danger" style={{ marginLeft: '8px' }}>
                          Low stock
                        </span>
                      )}
                    </td>
                    <td>
                      {item.last_updated
                        ? new Date(item.last_updated).toLocaleDateString()
                        : '—'}
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button className="icon-btn" onClick={() => openAdjustModal(item, 'add')}>+ Add</button>
                        <button className="icon-btn" onClick={() => openAdjustModal(item, 'remove')}>− Remove</button>
                        <button className="icon-btn" onClick={() => openAdjustModal(item, 'set')}>Set</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create new inventory record modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>New Stock Record</h3>
            <form onSubmit={handleCreateSubmit}>
              <div className="form-group">
                <label>Product</label>
                <select
                  value={createForm.product_id}
                  onChange={(e) => setCreateForm({ ...createForm, product_id: e.target.value })}
                  required
                >
                  <option value="">Select a product…</option>
                  {productsWithoutInventory.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Initial Quantity</label>
                <input
                  type="number"
                  min="0"
                  value={createForm.quantity}
                  onChange={(e) => setCreateForm({ ...createForm, quantity: e.target.value })}
                  required
                />
              </div>

              {createError && <div className="form-error">{createError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Adjust stock modal (add / remove / set) */}
      {adjustTarget && (
        <div className="modal-overlay" onClick={() => setAdjustTarget(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>{modeLabel[adjustTarget.mode]}</h3>
            <p className="page-subtitle" style={{ marginTop: '-10px', marginBottom: '18px' }}>
              {adjustTarget.product_name || getProductName(adjustTarget.product_id)} — current stock: {adjustTarget.quantity}
            </p>
            <form onSubmit={handleAdjustSubmit}>
              <div className="form-group">
                <label>{adjustTarget.mode === 'set' ? 'New Quantity' : 'Amount'}</label>
                <input
                  type="number"
                  min={adjustTarget.mode === 'set' ? '0' : '1'}
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              {adjustError && <div className="form-error">{adjustError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setAdjustTarget(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Confirm</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Inventory