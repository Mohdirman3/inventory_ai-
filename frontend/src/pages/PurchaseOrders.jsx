import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'

function PurchaseOrders() {
  const [orders, setOrders] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ supplier_id: '', items: [{ product_id: '', quantity: '', unit_price: '' }] })
  const [formError, setFormError] = useState('')

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const response = await api.get('/purchase-orders/')
      setOrders(response.data.data)
    } catch (err) {
      setError('Failed to load purchase orders')
    } finally {
      setLoading(false)
    }
  }

  const fetchSuppliers = async () => {
    try {
      const response = await api.get('/suppliers/')
      setSuppliers(response.data.data)
    } catch (err) {}
  }

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/')
      setProducts(response.data.data)
    } catch (err) {}
  }

  useEffect(() => {
    fetchOrders()
    fetchSuppliers()
    fetchProducts()
  }, [])

  const openModal = () => {
    setForm({ supplier_id: '', items: [{ product_id: '', quantity: '', unit_price: '' }] })
    setFormError('')
    setShowModal(true)
  }

  const addItemRow = () => {
    setForm({ ...form, items: [...form.items, { product_id: '', quantity: '', unit_price: '' }] })
  }

  const removeItemRow = (index) => {
    setForm({ ...form, items: form.items.filter((_, i) => i !== index) })
  }

  const updateItem = (index, field, value) => {
    const newItems = [...form.items]
    newItems[index][field] = value

    if (field === 'product_id') {
      const product = products.find((p) => p.id === parseInt(value))
      if (product) newItems[index].unit_price = product.price
    }

    setForm({ ...form, items: newItems })
  }

  const handleSupplierChange = (value) => {
    setForm({
      supplier_id: value,
      items: [{ product_id: '', quantity: '', unit_price: '' }]
    })
  }

  const orderTotal = form.items.reduce((sum, item) => {
    const qty = parseFloat(item.quantity) || 0
    const price = parseFloat(item.unit_price) || 0
    return sum + qty * price
  }, 0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    const payload = {
      supplier_id: parseInt(form.supplier_id),
      items: form.items.map((item) => ({
        product_id: parseInt(item.product_id),
        quantity: parseInt(item.quantity),
        unit_price: parseFloat(item.unit_price)
      }))
    }

    try {
      await api.post('/purchase-orders/', payload)
      toast.success('Purchase order created')
      setShowModal(false)
      fetchOrders()
    } catch (err) {
      setFormError(err.response?.data?.message || 'Failed to create purchase order')
    }
  }

  const handleReceive = async (orderId) => {
    if (!window.confirm('Mark this order as received? This will increase inventory.')) return
    try {
      await api.post(`/purchase-orders/${orderId}/receive`)
      toast.success('Order received — inventory updated')
      fetchOrders()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to receive order')
    }
  }

  const getSupplierName = (id) => suppliers.find((s) => s.id === id)?.name || `#${id}`
  const getProductName = (id) => products.find((p) => p.id === id)?.name || `#${id}`

  const orderItemTotal = (order) =>
    order.items.reduce((sum, i) => sum + i.quantity * i.unit_price, 0)

  const statusConfig = {
    PENDING: { badge: 'badge-warning', icon: '⏳', label: 'Pending' },
    RECEIVED: { badge: 'badge-success', icon: '✅', label: 'Received' },
    CANCELLED: { badge: 'badge-danger', icon: '✕', label: 'Cancelled' }
  }

  const availableProducts = form.supplier_id
    ? products.filter((p) => p.supplier_id === parseInt(form.supplier_id))
    : []

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Purchase Orders</h2>
          <p className="page-subtitle">Order stock from suppliers and receive shipments</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={openModal}
          disabled={suppliers.length === 0 || products.length === 0}
        >
          + New Purchase Order
        </button>
      </div>

      {loading && <p className="state-message">Loading purchase orders…</p>}
      {error && <p className="state-message error">{error}</p>}

      {!loading && !error && orders.length === 0 && (
        <div className="card">
          <p className="state-message">No purchase orders yet — create one to restock from a supplier.</p>
        </div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="po-list">
          {orders.map((order) => {
            const config = statusConfig[order.status] || statusConfig.PENDING
            const isOpen = expandedId === order.id

            return (
              <div className="po-card" key={order.id}>
                <div
                  className="po-card-header"
                  onClick={() => setExpandedId(isOpen ? null : order.id)}
                >
                  <div className="po-card-main">
                    <span className="po-status-icon">{config.icon}</span>
                    <div>
                      <div className="po-card-title">
                        Order #{order.id} · {getSupplierName(order.supplier_id)}
                      </div>
                      <div className="po-card-meta">
                        {order.items.length} item{order.items.length !== 1 ? 's' : ''} ·{' '}
                        {order.order_date ? new Date(order.order_date).toLocaleDateString() : '—'}
                      </div>
                    </div>
                  </div>
                  <div className="po-card-right">
                    <span className="po-card-total">₹{orderItemTotal(order).toFixed(2)}</span>
                    <span className={`badge ${config.badge}`}>{config.label}</span>
                    <span className={`po-chevron ${isOpen ? 'open' : ''}`}>▾</span>
                  </div>
                </div>

                {isOpen && (
                  <div className="po-card-body">
                    <table className="po-item-table">
                      <thead>
                        <tr><th>Product</th><th>Qty</th><th>Unit Price</th><th>Subtotal</th></tr>
                      </thead>
                      <tbody>
                        {order.items.map((item, i) => (
                          <tr key={i}>
                            <td>{getProductName(item.product_id)}</td>
                            <td>{item.quantity}</td>
                            <td>₹{item.unit_price}</td>
                            <td>₹{(item.quantity * item.unit_price).toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {order.status === 'PENDING' && (
                      <button
                        className="btn btn-primary"
                        style={{ marginTop: '14px' }}
                        onClick={() => handleReceive(order.id)}
                      >
                        ✓ Mark as Received
                      </button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box po-modal" onClick={(e) => e.stopPropagation()}>
            <div className="po-modal-header">
              <div>
                <h3>New Purchase Order</h3>
                <p className="page-subtitle" style={{ marginTop: '2px' }}>Restock from a supplier</p>
              </div>
              <button type="button" className="po-close-btn" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="po-step">
                <div className="po-step-label">
                  <span className="po-step-num">1</span> Choose Supplier
                </div>
                <select
                  value={form.supplier_id}
                  onChange={(e) => handleSupplierChange(e.target.value)}
                  required
                >
                  <option value="">Select a supplier…</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>{s.name} · {s.lead_time_days}d lead time</option>
                  ))}
                </select>
              </div>

              {form.supplier_id && availableProducts.length === 0 && (
                <div className="po-empty-notice">
                  <span>⚠️</span>
                  <div>
                    <strong>No products linked to this supplier</strong>
                    <p>Add a product under this supplier first, then create the order.</p>
                  </div>
                </div>
              )}

              {form.supplier_id && availableProducts.length > 0 && (
                <>
                  <div className="po-step">
                    <div className="po-step-label">
                      <span className="po-step-num">2</span> Add Items
                    </div>

                    {form.items.map((item, index) => {
                      const selectedProduct = availableProducts.find((p) => p.id === parseInt(item.product_id))
                      const subtotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)

                      return (
                        <div key={index} className="po-item-card">
                          <div className="po-item-card-header">
                            <span>Item {index + 1}</span>
                            {form.items.length > 1 && (
                              <button type="button" className="po-remove-btn" onClick={() => removeItemRow(index)}>
                                Remove
                              </button>
                            )}
                          </div>

                          <select
                            value={item.product_id}
                            onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                            required
                          >
                            <option value="">Select product…</option>
                            {availableProducts.map((p) => (
                              <option key={p.id} value={p.id}>{p.name} — ₹{p.price}</option>
                            ))}
                          </select>

                          {selectedProduct && (
                            <div className="po-item-fields-row" style={{ marginTop: '8px' }}>
                              <div>
                                <label className="po-mini-label">Quantity</label>
                                <input
                                  type="number"
                                  min="1"
                                  placeholder="0"
                                  value={item.quantity}
                                  onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                                  required
                                />
                              </div>
                              <div>
                                <label className="po-mini-label">Unit Price (₹)</label>
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={item.unit_price}
                                  onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
                                  required
                                />
                              </div>
                            </div>
                          )}

                          {subtotal > 0 && (
                            <div className="po-item-subtotal">Subtotal: ₹{subtotal.toFixed(2)}</div>
                          )}
                        </div>
                      )
                    })}

                    <button type="button" className="btn btn-secondary btn-block" onClick={addItemRow}>
                      + Add Another Item
                    </button>
                  </div>

                  <div className="po-total-row">
                    <span>Order Total</span>
                    <strong>₹{orderTotal.toFixed(2)}</strong>
                  </div>
                </>
              )}

              {formError && <div className="form-error">{formError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!form.supplier_id || availableProducts.length === 0}
                >
                  Create Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default PurchaseOrders