import {useEffect, useState} from 'react';
import {Link} from 'react-router-dom';
import {CreditCard, Eye, EyeOff, Wallet} from 'lucide-react';
import {getAccounts} from '../api/accounts.js';
import {useAuth} from '../AuthContext.jsx';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import {formatMoney} from '../utils/format.js';

export default function Home() {
    const auth = useAuth();
    const user = auth.user || {};

    const [accounts, setAccounts] = useState(null);
    const [error, setError] = useState('');
    const [show, setShow] = useState(false);

    useEffect(() => {
        async function loadAccounts() {
            try {
                const data = await getAccounts();
                setAccounts(data);
            } catch (err) {
                setError(err.message);
            }
        }
        loadAccounts();
    }, []);

    let total = 0;
    if (accounts) {
        for (let i = 0; i < accounts.length; i++) {
            total = total + Number(accounts[i].balance);
        }
    }

    let amountText = '-------- VND';
    if (show && accounts) {
        amountText = formatMoney(total);
    } else if (show) {
        amountText = 'Đang tải...';
    }

    let eyeIcon = <Eye size={20} />;
    let eyeLabel = 'Hiện số dư';
    if (show) {
        eyeIcon = <EyeOff size={20} />;
        eyeLabel = 'Ẩn số dư';
    }

    let accountsText = 'Tài khoản ngân hàng';
    if (accounts) {accountsText = `${accounts.length} tài khoản ngân hàng`;}

    return (
        <section className="pay-card">
            <h1>Xin chào, {user.full_name}!</h1>
            <p className="pay-muted">Tổng quan tài khoản của bạn</p>

            <ErrorMessage message={error} />

            <div className="home-total">
                <div className="pay-muted">Tổng số dư khả dụng</div>
                <div className="home-amount">
                    <span>{amountText}</span>
                    <button type="button" className="icon-btn" onClick={() => setShow(!show)} aria-label={eyeLabel}>
                        {eyeIcon}
                    </button>
                </div>
            </div>

            <div className="tiles">
                <Link to="/accounts" className="tile">
                    <Wallet size={24} />
                    <span>
                        <b>Tài khoản</b>
                        {accountsText}
                    </span>
                </Link>
                <Link to="/payment" className="tile">
                    <CreditCard size={24} />
                    <span>
                        <b>Thanh toán học phí</b>
                        Tra cứu MSSV và đóng học phí
                    </span>
                </Link>
            </div>
            
        </section>
    );
}
