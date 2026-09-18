import { useEffect, useState } from 'react'
import api from '../api/axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'

const PALETTE = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#f43f5e']
const STOCK_COLORS = { 'Healthy Stock': '#10b981', 'Low Stock': '#f59e0b', 'Out of Stock': '#ef4444' }

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="chart-tooltip-row">
          <span className="chart-tooltip-dot" style={{ background: p.fill || p.color }} />
          {p.name}: <strong>{p.value}</strong>
        </div>
      ))}
    </div>
  )
}

function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [topSelling, setTopSelling] = useState([])
  const [reorders, setReorders] = useState([])
  const [supplierPerf, setSupplierPerf] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [summaryRes, topRes, reorderRes, supplierRes] = await Promise.all([
          api.get('/analytics/inventory-summary'),
          api.get('/analytics/top-selling'),
          api.get('/analytics/reorder-recommendations'),
          api.get('/analytics/supplier-performance')
        ])

        setSummary(summaryRes.data.data)
        setTopSelling(topRes.data.data)
        setReorders(reorderRes.data.data)
        setSupplierPerf(supplierRes.data.data)
      } catch (err) {
        console.error('Failed to load dashboard data:', err)
        setError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [])

  if (loading) return <div className="page-container"><p className="state-message">Loading dashboard…</p></div>
  if (error) return <div className="page-container"><p className="state-message error">{error}</p></div>

  const activeProducts = summary?.total_active_products ?? 0
  const lowStock = summary?.low_stock_products ?? 0
  const outOfStock = summary?.out_of_stock_products ?? 0
  const healthyStock = Math.max(0, activeProducts - lowStock - outOfStock)

  const stockPieData = [
    { name: 'Healthy Stock', value: healthyStock },
    { name: 'Low Stock', value: lowStock },
    { name: 'Out of Stock', value: outOfStock }
  ].filter((d) => d.value > 0)

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p className="page-subtitle">Live overview of your inventory operations</p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="stats-grid">
        <div className="stat-card stat-card-indigo">
          <div className="stat-icon">📦</div>
          <span className="stat-label">Active Products</span>
          <span className="stat-value">{summary?.total_active_products ?? 0}</span>
        </div>
        <div className="stat-card stat-card-blue">
          <div className="stat-icon">📊</div>
          <span className="stat-label">Total Stock Units</span>
          <span className="stat-value">{summary?.total_stock_units ?? 0}</span>
        </div>
        <div className="stat-card stat-card-amber">
          <div className="stat-icon">⚠️</div>
          <span className="stat-label">Low Stock</span>
          <span className="stat-value stat-danger">{summary?.low_stock_products ?? 0}</span>
        </div>
        <div className="stat-card stat-card-rose">
          <div className="stat-icon">🚨</div>
          <span className="stat-label">Out of Stock</span>
          <span className="stat-value stat-danger">{summary?.out_of_stock_products ?? 0}</span>
        </div>
      </div>

      {/* Charts row */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-title">📈 Top Selling Products</div>
          <div style={{ padding: '16px' }}>
            {topSelling.length === 0 ? (
              <p className="state-message">No sales data yet</p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={topSelling} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                    <defs>
                      {topSelling.map((_, i) => (
                        <linearGradient key={i} id={`barGrad${i}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0.95} />
                          <stop offset="100%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0.55} />
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                    <XAxis dataKey="product_name" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={55} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.06)' }} />
                    <Bar dataKey="total_sold" name="Units Sold" radius={[8, 8, 0, 0]}>
                      {topSelling.map((_, i) => (
                        <Cell key={i} fill={`url(#barGrad${i})`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                <div className="stat-list">
                  {topSelling.map((p, i) => (
                    <div key={p.product_id} className="stat-list-row">
                      <span className="stat-list-dot" style={{ background: PALETTE[i % PALETTE.length] }} />
                      <span className="stat-list-name">{p.product_name}</span>
                      <span className="stat-list-value">{p.total_sold} units</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-title">🩺 Stock Health</div>
          <div style={{ padding: '16px' }}>
            {stockPieData.length === 0 ? (
              <p className="state-message">No inventory data yet</p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={stockPieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={52}
                      outerRadius={82}
                      paddingAngle={4}
                      stroke="none"
                    >
                      {stockPieData.map((entry) => (
                        <Cell key={entry.name} fill={STOCK_COLORS[entry.name]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>

                <div className="stat-list">
                  {stockPieData.map((d) => (
                    <div key={d.name} className="stat-list-row">
                      <span className="stat-list-dot" style={{ background: STOCK_COLORS[d.name] }} />
                      <span className="stat-list-name">{d.name}</span>
                      <span className="stat-list-value">
                        {d.value} product{d.value !== 1 ? 's' : ''}
                        {' '}
                        <span className="stat-list-percent">
                          ({Math.round((d.value / summary.total_active_products) * 100)}%)
                        </span>
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Reorder recommendations */}
      <div className="card" style={{ marginTop: '16px' }}>
        <div className="card-title">🔄 Reorder Recommendations</div>
        {reorders.length === 0 ? (
          <p className="state-message">All stock levels are healthy — no reorders needed</p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr><th>Product</th><th>Current Stock</th><th>Avg Daily Sales</th><th>Status</th></tr>
              </thead>
              <tbody>
                {reorders.map((r) => (
                  <tr key={r.product_id}>
                    <td>{r.product_name}</td>
                    <td>{r.current_stock}</td>
                    <td>{r.avg_daily_sales}</td>
                    <td><span className="badge badge-danger">Reorder</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Supplier performance chart */}
      <div className="card" style={{ marginTop: '16px' }}>
        <div className="card-title">🤝 Supplier Fulfillment Rate</div>
        <div style={{ padding: '16px' }}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={supplierPerf.filter((s) => s.fulfillment_rate_percent !== null)}
              margin={{ top: 10, right: 10, left: -20, bottom: 10 }}
            >
              <defs>
                <linearGradient id="supplierGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.95} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.65} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
              <XAxis dataKey="supplier_name" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={55} />
              <YAxis tick={{ fontSize: 11 }} unit="%" />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(16,185,129,0.06)' }} />
              <Bar dataKey="fulfillment_rate_percent" name="Fulfillment" fill="url(#supplierGrad)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>

          <div className="stat-list">
            {supplierPerf.map((s) => (
              <div key={s.supplier_id} className="stat-list-row">
                <span className="stat-list-name">{s.supplier_name}</span>
                <span className="stat-list-value">
                  {s.received_orders}/{s.total_purchase_orders} orders
                  {s.fulfillment_rate_percent !== null && (
                    <span className={`badge ${s.fulfillment_rate_percent >= 70 ? 'badge-success' : 'badge-danger'}`} style={{ marginLeft: '8px' }}>
                      {s.fulfillment_rate_percent}%
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard