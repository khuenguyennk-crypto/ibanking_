import {useEffect, useState} from 'react';
import {createPayment, getPayment} from '../../api/payments.js';
import Confirm from './Confirm.jsx';
import Otp from './Otp.jsx';
import Result from './Result.jsx';

export default function PaymentModal(props) {
    const student = props.student;
    const tuition = props.tuition;
    const account = props.account;
    const onClose = props.onClose;
    const onSettled = props.onSettled;

    const [step, setStep] = useState(1);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const [tx, setTx] = useState(null);
    const [result, setResult] = useState(null);

    async function handleCreate() {
        setError('');
        setBusy(true);
        try {
            const created = await createPayment({
                bank_account_id: account.bank_account_id,
                tuition_id: tuition.tuition_id,
            });
            setTx(created);
            setStep(2);
        } catch (err) {
            setError(err.message);
            onSettled();
        } finally {
            setBusy(false);
        }
    }

    function handleOtpDone(done) {
        setResult(done);
        setStep(3);
    }

    function handleAbort(message) {onClose({message: message});}

    function handleNew() {onClose({reset: true});}

    function handleCancelStep1() {onClose();}

    let processing = false;
    let resultId = null;
    if (result) {
        processing = result.status === 'processing';
        resultId = result.transaction_id;
    }

    useEffect(() => {
        if (!processing) return undefined;
        const timerId = setInterval(() => {getPayment(resultId).then(setResult).catch(() => {});}, 2000);
        return () => clearInterval(timerId);
    }, [processing, resultId]);

    let settled = null;
    if (result && !processing) {settled = result.status;}

    useEffect(() => {if (settled) {onSettled();}}, [settled]);

    useEffect(() => {
        if (step !== 1) return undefined;
        function handleKey(event) {
            if (event.key === 'Escape' && !busy) {
                onClose();
            }
        }
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [step, busy, onClose]);

    let content = null;
    if (step === 1) {
        content = <Confirm student={student} tuition={tuition} account={account} busy={busy} error={error} onCancel={handleCancelStep1} onSubmit={handleCreate} />;
    } else if (step === 2) {
        content = <Otp tx={tx} onDone={handleOtpDone} onAbort={handleAbort} />;
    } else {
        content = <Result result={result} student={student} tuition={tuition} account={account} onNew={handleNew} />;
    }

    let class2 = '';
    if (step >= 2) class2 = 'on';
    let class3 = '';
    if (step >= 3) class3 = 'on';

    return (
        <div className="pay-overlay">
            <div className="pay-dialog" role="dialog" aria-modal="true">
                <div className="pay-prog" aria-hidden="true">
                    <i className="on" />
                    <i className={class2} />
                    <i className={class3} />
                </div>
                {content}
            </div>
        </div>
    );
}
