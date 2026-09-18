import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import Products from './pages/Products'
import Suppliers from './pages/Suppliers'
import Inventory from './pages/Inventory'
import Sales from './pages/Sales'
import Dashboard from './pages/Dashboard'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import PurchaseOrders from './pages/purchaseOrders'
import { Toaster } from 'react-hot-toast'
import Profile from './pages/profile'

function Layout({ children }) {
  const location = useLocation()
  const publicPaths = ['/', '/login', '/register', '/forgot-password']
  const hideNavbar = publicPaths.includes(location.pathname)

  return (
    <>
      {!hideNavbar && <Navbar />}
      {children}
    </>
  )
}

function App() {
  return (
    <><BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
          <Route path="/suppliers" element={<ProtectedRoute><Suppliers /></ProtectedRoute>} />
          <Route path="/inventory" element={<ProtectedRoute><Inventory /></ProtectedRoute>} />
          <Route path="/sales" element={<ProtectedRoute><Sales /></ProtectedRoute>} />
          <Route path="/purchase-orders" element={<ProtectedRoute><PurchaseOrders /></ProtectedRoute>} />
          <Route path="/profile" element={
          <ProtectedRoute><Profile /></ProtectedRoute>
} />
        </Routes>
      </Layout>
    </BrowserRouter><Toaster position="top-right" toastOptions={{
      style: { fontFamily: 'Inter, sans-serif', fontSize: '14px' }
    }} /></>  
  )
}

export default App