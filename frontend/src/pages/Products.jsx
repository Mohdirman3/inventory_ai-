import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'

function Products() {
  const [products, setProducts] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', category: '', price: '', supplier_id: '' })
  const [formError, setFormError] = useState('')

  const fetchProducts = async () => {
    setLoading(true)
    try {
      const response = await api.get('/products/')
      setProducts(response.data.data)
    } catch (err) {
      console.error('Failed to load products:', err)
      setError('Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const fetchSuppliers = async () => {
    try {
      const response = await api.get('/suppliers/')
      setSuppliers(response.data.data)
    } catch (err) {
      console.error('Failed to load suppliers:', err)
    }
  }

  useEffect(() => {
    fetchProducts()
    fetchSuppliers()
  }, [])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ name: '', category: '', price: '', supplier_id: '' })
    setFormError('')
    setShowModal(true)
  }

  const openEditModal = (product) => {
    setEditingId(product.id)
    setForm({
      name: product.name,
      category: product.category,
      price: product.price,
      supplier_id: product.supplier_id
    })
    setFormError('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    const payload = {
      name: form.name,
      category: form.category,
      price: parseFloat(form.price),
      supplier_id: parseInt(form.supplier_id)
    }

    try {
      if (editingId) {
        await api.put(`/products/${editingId}`, payload)
        toast.success('Product updated')
      } else {
        await api.post('/products/', payload)
        toast.success('Product created')
      }
      setShowModal(false)
      fetchProducts()
    } catch (err) {
      setFormError(err.response?.data?.message || 'Something went wrong')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Deactivate this product?')) return
    try {
      await api.delete(`/products/${id}`)
      toast.success('Product deactivated')
      fetchProducts()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to delete')
    }
  }

  const getSupplierName = (id) => {
    const supplier = suppliers.find((s) => s.id === id)
    return supplier ? supplier.name : `#${id}`
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Products</h2>
          <p className="page-subtitle">Manage your product catalog</p>
        </div>
        <button className="btn btn-primary" onClick={openCreateModal}>+ New Product</button>
      </div>

      <div className="card">
        {loading && <p className="state-message">Loading products…</p>}
        {error && <p className="state-message error">{error}</p>}

        {!loading && !error && (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Supplier</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 ? (
                  <tr><td colSpan="5" className="state-message">No products yet</td></tr>
                ) : (
                  products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.name}</td>
                      <td>{product.category}</td>
                      <td>₹{product.price}</td>
                      <td>{getSupplierName(product.supplier_id)}</td>
                      <td>
                        <div className="action-buttons">
                          <button className="icon-btn" onClick={() => openEditModal(product)}>Edit</button>
                          <button className="icon-btn danger" onClick={() => handleDelete(product.id)}>Delete</button>
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
            <h3>{editingId ? 'Edit Product' : 'New Product'}</h3>
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
                <label>Category</label>
                <input
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Supplier</label>
                <select
                  value={form.supplier_id}
                  onChange={(e) => setForm({ ...form, supplier_id: e.target.value })}
                  required
                >
                  <option value="">Select a supplier…</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
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

export default Products