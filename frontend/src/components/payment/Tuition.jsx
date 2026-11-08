import {formatMoney} from '../../utils/format.js';

export default function Tuition(props) {
    const tuitions = props.tuitions;

    let emptyLine = null;
    if (tuitions.length === 0) {emptyLine = <p className="pay-muted">Sinh viên này chưa có khoản học phí nào.</p>;}

    const items = tuitions.map(function (t) {
        const paid = t.status === 'paid';
        const selected = props.selectedId === t.tuition_id;

        let badgeText = 'Chưa thanh toán';
        let badgeClass = 'pay-badge pay-badge-otp_sent';
        if (paid) {
            badgeText = 'Đã thanh toán';
            badgeClass = 'pay-badge pay-badge-success';
        }

        function handleClick() {props.onSelect(t.tuition_id);}

        return (
        <button key={t.tuition_id} type="button" className="pay-tui" aria-pressed={selected} disabled={paid} onClick={handleClick}>
            <span className="pay-tui-top">
                <span>{t.semester}</span>
                <span className={badgeClass}>{badgeText}</span>
            </span>
            <span className="pay-tui-amount">{formatMoney(t.amount)}</span>
        </button>
        );
    });

    return (
        <section className="pay-card">
            <h2>Các khoản học phí</h2>
            {emptyLine}
            {items}
        </section>
    );
}
