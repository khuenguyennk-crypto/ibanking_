import {useState} from 'react';
import {useAuth} from '../../AuthContext.jsx';
import {accountLabel, formatMoney} from '../../utils/format.js';
import ErrorMessage from '../common/ErrorMessage.jsx';

export default function Confirm(props) {
    const student = props.student;
    const tuition = props.tuition;
    const account = props.account;

    const auth = useAuth();
    const user = auth.user || {};

    const [agreed, setAgreed] = useState(false);

    const enough = Number(account.balance) >= Number(tuition.amount);

    let canConfirm = false;
    if (agreed && enough && tuition.status === 'unpaid' && !props.busy) {canConfirm = true;}

    let notEnough = null;
    if (!enough) {notEnough = <p className="pay-error">Số dư không đủ để thanh toán khoản học phí này.</p>;}

    let confirmText = 'Xác nhận giao dịch';
    if (props.busy) {confirmText = 'Đang xử lý...';}

    function handleAgreeChange(event) {setAgreed(event.target.checked);}

    return (
        <>
            <h2>Xác nhận thanh toán</h2>
            <p className="pay-muted">Kiểm tra lại thông tin trước khi xác nhận.</p>

            <div className="pay-group">
                <h3>Người nộp tiền</h3>
                <dl className="pay-dl">
                    <div><dt>Họ và tên</dt><dd>{user.full_name}</dd></div>
                    <div><dt>Số điện thoại</dt><dd>{user.phone}</dd></div>
                    <div><dt>Email</dt><dd>{user.email}</dd></div>
                </dl>
            </div>


            <div className="pay-group">
                <h3>Thông tin học phí</h3>
                <dl className="pay-dl">
                    <div><dt>MSSV</dt><dd>{student.student_id}</dd></div>
                    <div><dt>Họ và tên sinh viên</dt><dd>{student.full_name}</dd></div>
                    <div><dt>Học kỳ</dt><dd>{tuition.semester}</dd></div>
                    <div><dt>Số tiền học phí</dt><dd>{formatMoney(tuition.amount)}</dd></div>
                </dl>
            </div>


            <div className="pay-group">
                <h3>Thông tin thanh toán</h3>
                <dl className="pay-dl">
                    <div><dt>Tài khoản</dt><dd>{accountLabel(account)}</dd></div>
                    <div><dt>Số dư khả dụng</dt><dd>{formatMoney(account.balance)}</dd></div>
                    <div><dt>Số tiền cần thanh toán</dt><dd>{formatMoney(tuition.amount)}</dd></div>
                </dl>

                {notEnough}

                <ul className="pay-muted pay-terms-list">
                    <li>Chỉ thanh toán toàn bộ khoản học phí, không thanh toán một phần.</li>
                    <li>Giao dịch được xác thực bằng mã OTP gửi qua email, hiệu lực 5 phút và chỉ dùng một lần.</li>
                    <li>Nếu giao dịch lỗi sau khi đã trừ tiền, hệ thống tự động hoàn tiền về tài khoản.</li>
                </ul>

                <label className="pay-check">
                    <input type="checkbox" checked={agreed} onChange={handleAgreeChange} />
                    <span>Tôi đã đọc và đồng ý với các thỏa thuận và điều khoản.</span>
                </label>
            </div>

            <ErrorMessage message={props.error} />

            <div className="pay-actions">
                <button type="button" className="pay-btn-ghost" onClick={props.onCancel} disabled={props.busy}>
                    Quay lại
                </button>
                <button type="button" className="pay-btn" onClick={props.onSubmit} disabled={!canConfirm}>
                    {confirmText}
                </button>
            </div>
        </>
    );
}
