import {useEffect, useState} from 'react';
import {ArrowDown, RefreshCw} from 'lucide-react';
import {getPayments} from '../api/payments.js';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import Loading from '../components/common/Loading.jsx';
import StatusBadge from '../components/common/Status.jsx';
import {accountLabel, formatDateTime, formatMoney} from '../utils/format.js';

export default function History() {
    const [items, setItems] = useState(null);
    const [error, setError] = useState('');
    const [reload, setReload] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadHistory() {
            setLoading(true);
            setError('');
            try {
                const data = await getPayments();
                setItems(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }
        loadHistory();
    }, [reload]);

    function handleRefresh() {
        if (loading) {return;}
        setReload(reload + 1);
    }

    const rows = items || [];

    let refreshIconClass = '';
    if (loading) {refreshIconClass = 'is-spinning';}

    return (
        <section className="pay-card">
            <div className="pay-row">
                <div>
                    <h1>Lịch sử giao dịch</h1>
                </div>
                <button type="button" className="pay-btn-ghost pay-btn-refresh" aria-busy={loading} onClick={handleRefresh}>
                    <RefreshCw size={16} className={refreshIconClass} />
                </button>
            </div>

            <ErrorMessage message={error} />
            {!items && !error && <Loading />}
            {items && rows.length === 0 && <p className="pay-muted pay-block">Chưa có giao dịch nào.</p>}

            {rows.length > 0 && (
                <div className="pay-hist">
                    {rows.map((t) => {
                        const ok = t.status === 'success';
                        return (
                            <div key={t.transaction_id} className="pay-hrow">
                                <span className={ok ? 'pay-hic' : 'pay-hic off'}>
                                    <ArrowDown size={18} />
                                </span>

                                <div className="pay-hmain">
                                    <b>Thanh toán học phí{t.student_id && ` - ${t.student_id}`}{t.student_name && ` - ${t.student_name}`}</b>
                                    <span className="pay-muted">
                                        {t.semester && `${t.semester} - `}
                                        {accountLabel(t)} - {formatDateTime(t.created_at)} - #{t.transaction_id}
                                    </span>
                                    {t.failure_reason && <span className="pay-error">{t.failure_reason}</span>}
                                </div>

                                <div className="pay-hamt">
                                    <strong className={ok ? 'out' : 'off'}>{formatMoney(t.amount)}</strong>
                                    <StatusBadge status={t.status} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </section>
    );
}
