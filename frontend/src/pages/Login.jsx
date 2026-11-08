import {useState} from 'react';
import {Navigate, useLocation, useNavigate} from 'react-router-dom';
import {Eye, EyeOff, Landmark, LockKeyhole, UserRound} from 'lucide-react';

import {useAuth} from '../AuthContext.jsx';

export default function Login() {
    const auth = useAuth();

    const navigate = useNavigate();
    const location = useLocation();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [busy, setBusy] = useState(false);

    if (auth.isLoading) {return <main className="auth-loading">Đang kiểm tra phiên đăng nhập...</main>;}

    if (auth.isAuthenticated) {return <Navigate to="/home" replace />;}

    async function handleSubmit(event) {
        event.preventDefault();
        setError('');

        if (username.trim() === '' || password === '') {
            setError('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.');
            return;
        }

        setBusy(true);
        try {
            await auth.login({ username: username, password: password });

            let goTo = '/home';
            if (location.state && location.state.from && location.state.from.pathname) {
                goTo = location.state.from.pathname;
            }
            navigate(goTo, {replace: true});
        } catch (err) {
            setError(err.message || 'Đăng nhập không thành công.');
        } finally {
            setBusy(false);
        }
    }

    let passwordType = 'password';
    let eyeIcon = <Eye size={18} />;
    let eyeLabel = 'Hiện mật khẩu';
    if (showPassword) {
        passwordType = 'text';
        eyeIcon = <EyeOff size={18} />;
        eyeLabel = 'Ẩn mật khẩu';
    }

    let submitText = 'Đăng nhập';
    if (busy) { submitText = 'Đang đăng nhập...';}

    return (
        <main className="login-page">
            <section className="login-card">
                <div className="login-brand">
                    <span className="brand-icon">
                        <Landmark size={25} />
                    </span>
                    <span>iBanking</span>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <label htmlFor="username">Tên đăng nhập</label>
                    <div className="login-input-wrap">
                        <UserRound size={18} />
                        <input id="username" name="username" autoComplete="username" placeholder="Nhập tên đăng nhập" value={username} onChange={(event) => setUsername(event.target.value)} disabled={busy} />
                    </div>

                    <label htmlFor="password">Mật khẩu</label>
                    <div className="login-input-wrap">
                        <LockKeyhole size={18} />
                        <input id="password" name="password" type={passwordType} autoComplete="current-password" placeholder="Nhập mật khẩu" value={password} onChange={(event) => setPassword(event.target.value)} disabled={busy} />
                        <button className="password-toggle" type="button" onClick={() => setShowPassword(!showPassword)} aria-label={eyeLabel}>
                            {eyeIcon}
                        </button>
                    </div>

                    {error && (
                        <p className="login-error" role="alert">
                        {error}
                        </p>
                    )}

                    <button className="login-submit" type="submit" disabled={busy}>
                        {submitText}
                    </button>
                </form>
            </section>
        </main>
    );
}
