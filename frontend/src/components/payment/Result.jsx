import {Link} from 'react-router-dom';
import {useAuth} from '../../AuthContext.jsx';
import {accountLabel, formatMoney} from '../../utils/format.js';
import StatusBadge from '../common/Status.jsx';

export default function Result(props) {
    const result = props.result;
    const student = props.student;
    const tuition = props.tuition;
    const account = props.account;

    const auth = useAuth();
    const user = auth.user || {};

    const processing = result.status === 'processing';
    const success = result.status === 'success';
    const cancelled = result.status === 'cancelled';

    let tone = 'bad';
    let title = 'Thanh toán thất bại';

    if (success) {
        tone = 'ok';
        title = 'Thanh toán thành công';
    } else if (processing) {
        tone = 'warn';
        title = 'Giao dịch đang được xử lý';
    } else if (cancelled) {
        title = 'Giao dịch đã hủy';
    }

    let noteLine = null;
    if (success) {
        noteLine = <p className="pay-muted">Email xác nhận đã được gửi tới {user.email}.</p>;
    } else if (processing) {
        noteLine = (
        <p className="pay-muted">Hệ thống đang hoàn tất giao dịch...</p>
        );
    }

    let reasonLine = null;
    if (result.failure_reason) {
        reasonLine = <p className="pay-error">{result.failure_reason}</p>;
    }

    return (
        <>
            <div className={'pay-res pay-res-' + tone}>
                <h2>{title}</h2>
                {noteLine}
                {reasonLine}
            </div>

            <dl className="pay-dl">
                <div><dt>Mã giao dịch</dt><dd>#{result.transaction_id}</dd></div>
                <div><dt>Trạng thái</dt><dd><StatusBadge status={result.status} /></dd></div>
                <div><dt>Số tiền</dt><dd>{formatMoney(result.amount)}</dd></div>
                <div><dt>Tài khoản</dt><dd>{accountLabel(account)}</dd></div>
                <div><dt>Sinh viên</dt><dd>{student.full_name} ({student.student_id})</dd></div>
                <div><dt>Học kỳ</dt><dd>{tuition.semester}</dd></div>
            </dl>

            <div className="pay-actions">
                <Link to="/history" className="pay-btn-ghost">Xem lịch sử</Link>
                <button type="button" className="pay-btn" onClick={props.onNew} disabled={processing}>
                    Giao dịch mới
                </button>
            </div>
        </>
    );
}
