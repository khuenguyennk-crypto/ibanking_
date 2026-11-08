import {Navigate, Outlet, Route, Routes, useLocation} from 'react-router-dom';
import {useAuth} from './AuthContext.jsx';
import AppLayout from './components/AppLayout.jsx';
import Accounts from './pages/Accounts.jsx';
import History from './pages/History.jsx';
import Home from './pages/Home.jsx';
import Login from './pages/Login.jsx';
import Payment from './pages/Payment.jsx';
import Profile from './pages/Profile.jsx';

function ProtectedRoute() {
  const auth = useAuth();
  const location = useLocation();

  if (auth.isLoading) {return <main className="auth-loading">Đang kiểm tra phiên đăng nhập...</main>;}

  if (!auth.isAuthenticated) {return <Navigate to="/login" replace state={{from: location}} />;}

  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/home" element={<Home />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/history" element={<History />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  );
}
