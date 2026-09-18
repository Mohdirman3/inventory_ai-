import { useEffect, useState } from 'react'
import api from '../api/axios'

function Sales() {
  const [sales, setSales] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ product_id: '', quantity: '' })
  const [formError, setFormError] = useState('')

  const fetchSales = async () => {
    setLoading(true)
    try {
      const response = await api.get('/sales/')
      setSales(response.data.data)
    } catch (err) {
      console.error('Failed to load sales:', err)
      setError('Failed to load sales')
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
    fetchSales()
    fetchProducts()
  }, [])

  const openModal = () => {
    setForm({ product_id: '', quantity: '' })
    setFormError('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    try {
      await api.post('/sales/', {
        product_id: parseInt(form.product_id),
        quantity: parseInt(form.quantity)
      })
      setShowModal(false)
      fetchSales()
    } catch (err) {
      setFormError(err.response?.data?.message || 'Failed to record sale')
    }
  }

  const selectedProduct = products.find((p) => p.id === parseInt(form.product_id))

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Sales</h2>
          <p className="page-subtitle">Record and review sales history</p>
        </div>
        <button className="btn btn-primary" onClick={openModal}>+ Record Sale</button>
      </div>

      <div className="card">
        {loading && <p className="state-message">Loading sales…</p>}
        {error && <p className="state-message error">{error}</p>}

        {!loading && !error && (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Total</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {sales.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="state-message">No sales recorded yet</td>
                  </tr>
                ) : (
                  sales.map((sale) => (
                    <tr key={sale.id}>
                      <td>{sale.product_name}</td>
                      <td>{sale.quantity}</td>
                      <td>₹{sale.total_amount}</td>
                      <td>{new Date(sale.sale_date).toLocaleDateString()}</td>
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
            <h3>Record a Sale</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Product</label>
                <select
                  value={form.product_id}
                  onChange={(e) => setForm({ ...form, product_id: e.target.value })}
                  required
                >
                  <option value="">Select a product…</option>
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} — ₹{p.price}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                  required
                />
              </div>

              {selectedProduct && form.quantity && (
                <p className="page-subtitle" style={{ marginTop: '-10px', marginBottom: '16px' }}>
                  Estimated total: ₹{(selectedProduct.price * parseInt(form.quantity || 0)).toFixed(2)}
                </p>
              )}

              {formError && <div className="form-error">{formError}</div>}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Record Sale</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Sales