import {useAuth} from '../AuthContext.jsx';

export default function Profile() {
    const auth = useAuth();
    const user = auth.user || {};

    return (
        <section className="pay-card">
            <h1>Thông tin cá nhân</h1>
            <dl className="pay-dl">
                <div><dt>Họ và tên</dt><dd>{user.full_name}</dd></div>
                <div><dt>Email</dt><dd>{user.email}</dd></div>
                <div><dt>Số điện thoại</dt><dd>{user.phone}</dd></div>
            </dl>
        </section>
    );
}