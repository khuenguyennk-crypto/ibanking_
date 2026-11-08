import {useEffect, useRef, useState} from 'react';
import {Link, Outlet, useLocation, useNavigate} from 'react-router-dom';
import {ChevronDown, CircleUser, CreditCard, History, House, Landmark, LogOut, UserRound,} from 'lucide-react';
import {useAuth} from '../AuthContext.jsx';
import '../payment.css';
import '../layout.css';

function sideClass(isActive) {
  if (isActive) {return 'side-link active';}
  return 'side-link';
}

export default function AppLayout() {
  const auth = useAuth();
  const user = auth.user || {};

  const navigate = useNavigate();
  const location = useLocation();
  const pathname = location.pathname;

  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {setOpen(false);}, [pathname]);

  function handleToggleMenu() {setOpen(!open);}

  function handleProfile() {navigate('/profile');}

  function handleLogout() {auth.logout();}

  const homeActive = pathname === '/home' || pathname === '/accounts';
  const paymentActive = pathname === '/payment';
  const historyActive = pathname === '/history';

  let menuBox = null;
  if (open) {
    menuBox = (
      <div className="menu" role="menu">
        <div className="menu-head">
          <strong>{user.full_name}</strong>
          <span>{user.email}</span>
        </div>
        <button type="button" className="menu-item" role="menuitem" onClick={handleProfile}>
          <UserRound size={18} />
          Tài khoản
        </button>
        <button type="button" className="menu-item" role="menuitem" onClick={handleLogout}>
          <LogOut size={18} />
          Đăng xuất
        </button>
      </div>
    );
  }

  return (
    <div className="shell">
      <header className="hdr">
        <div className="hdr-brand">
          <Landmark size={28} />
          <span>iBanking</span>
        </div>

        <div className="usermenu" ref={menuRef}>
          <button type="button" className="userbtn" aria-haspopup="menu" aria-expanded={open} onClick={handleToggleMenu}>
            <CircleUser size={22} />
            <span>Người nộp tiền</span>
            <ChevronDown size={16} />
          </button>
          {menuBox}
        </div>
      </header>

      <div className="layout">
        <nav className="side" aria-label="Menu chính">
          <Link to="/home" className={sideClass(homeActive)}>
            <House size={18} />
            Trang chủ
          </Link>

          <Link to="/payment" className={sideClass(paymentActive)}>
            <CreditCard size={18} />
            Thanh toán
          </Link>
          
          <Link to="/history" className={sideClass(historyActive)}>
            <History size={18} />
            Lịch sử giao dịch
          </Link>
        </nav>

        <main className="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
