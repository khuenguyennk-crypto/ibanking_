import {useEffect, useState} from 'react';
import {cancelPayment, confirmPayment, resendOtp} from '../../api/payments.js';
import {useAuth} from '../../AuthContext.jsx';
import ErrorMessage from '../common/ErrorMessage.jsx';

const RESEND_WAIT_SECONDS = 30;

function twoDigits(number) {
  let text = String(number);
  if (text.length < 2) {text = '0' + text;}
  return text;
}

function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return twoDigits(minutes) + ':' + twoDigits(seconds);
}

export default function Otp(props) {
    const tx = props.tx;

    const auth = useAuth();
    const user = auth.user || {};

    const [otp, setOtp] = useState('');
    const [error, setError] = useState('');

    const [info, setInfo] = useState('');
    const [busy, setBusy] = useState(false);

    const [secondsLeft, setSecondsLeft] = useState(() => tx.otp_expires_in);
    const [resendWait, setResendWait] = useState(RESEND_WAIT_SECONDS);

    useEffect(() => {
        if (secondsLeft <= 0) {return undefined;}
        const timerId = setTimeout(() => {setSecondsLeft(secondsLeft - 1);}, 1000);
        return () => clearTimeout(timerId);
    }, [secondsLeft]);

    useEffect(() => {
        if (resendWait <= 0) {return undefined;}
        const timerId = setTimeout(() => {setResendWait(resendWait - 1);}, 1000);
        return () => clearTimeout(timerId);
    }, [resendWait]);

    const expired = secondsLeft <= 0;

    async function handleConfirm(event) {
        event.preventDefault();
        setError('');
        setInfo('');

        if (otp.length !== 6) {
            setError('Mã OTP gồm đúng 6 chữ số.');
            return;
        }

        setBusy(true);
        try {
            const result = await confirmPayment(tx.transaction_id, otp);
            props.onDone(result);
        } catch (err) {
            if (err.code === 'OTP_EXPIRED') {
                props.onAbort('OTP đã hết hạn, giao dịch bị hủy. Vui lòng tạo giao dịch mới.');
            } else if (err.code === 'TRANSACTION_CLOSED') {
                props.onAbort(err.message);
            } else {
                setError(err.message);
                setBusy(false);
            }
        }
    }

    async function handleCancel() {
        if (busy) {return;}

        setBusy(true);
        try {
            await cancelPayment(tx.transaction_id);
        } catch (err) {
            if (err.code === 'TRANSACTION_NOT_CANCELLABLE') {
                props.onAbort('Giao dịch đang được xử lý, vui lòng xem kết quả ở mục Lịch sử.');
                return;
            }
        }
        props.onAbort('Bạn đã hủy giao dịch.');
    }

    useEffect(() => {
        function handleKey(event) {
            if (event.key === 'Escape') {handleCancel();}
        }
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [busy]);

    async function handleResend() {
        setError('');
        setInfo('');
        setBusy(true);
        try {
            const res = await resendOtp(tx.transaction_id);
            setSecondsLeft(res.otp_expires_in);
            setResendWait(RESEND_WAIT_SECONDS);
            setOtp('');
            setInfo('Đã gửi lại mã OTP tới email của bạn. Mã cũ không còn hiệu lực.');
        } catch (err) {
            if (err.code === 'TRANSACTION_EXPIRED') {
                props.onAbort(err.message);
            } else {
                setError(err.message);
            }
        } finally {
            setBusy(false);
        }
    }

    function handleOtpChange(event) {
        const typed = event.target.value;

        let digitsOnly = '';
        for (let i = 0; i < typed.length; i++) {
            const ch = typed.charAt(i);
            if (ch >= '0' && ch <= '9') {
                digitsOnly = digitsOnly + ch;
            }
        }
        setOtp(digitsOnly);
    }

    function handleExpiredClose() {
        props.onAbort('OTP đã hết hạn, giao dịch bị hủy.');
    }

    let timeText = 'Mã còn hiệu lực: ' + formatTime(secondsLeft);
    let timeClass = 'pay-muted pay-center';
    if (expired) {
        timeText = 'OTP đã hết hạn. Hãy đóng cửa sổ và tạo giao dịch mới.';
        timeClass = 'pay-error pay-center';
    }

    let infoLine = null;
    if (info) {infoLine = <p className="pay-ok pay-center">{info}</p>;}

    let resendText = 'Gửi lại OTP';
    if (resendWait > 0) {resendText = 'Gửi lại OTP (' + resendWait + 's)';}

    let confirmText = 'Xác nhận';
    if (busy) {confirmText = 'Đang xử lý...';}

    let buttons = null;
    if (expired) {
        buttons = (
        <button type="button" className="pay-btn" onClick={handleExpiredClose}>
            Đóng
        </button>
        );
    } else {
        buttons = (
        <>
            <button type="button" className="pay-btn-ghost" onClick={handleCancel} disabled={busy}>
                Hủy
            </button>
            <button type="button" className="pay-btn-ghost" onClick={handleResend} disabled={busy || resendWait > 0}>
                {resendText}
            </button>
            <button type="submit" className="pay-btn" disabled={busy}>
                {confirmText}
            </button>
        </>
        );
    }

    return (
        <form onSubmit={handleConfirm}>
            <h2>Nhập mã OTP</h2>

            <p className="pay-muted">
                Mã OTP gồm 6 chữ số đã được gửi tới email <strong>{user.email}</strong>.
            </p>

            <input className="pay-otp-input" inputMode="numeric" maxLength={6} autoFocus placeholder="______" value={otp} disabled={busy || expired} onChange={handleOtpChange} />

            <p className={timeClass}>{timeText}</p>
            
            {infoLine}
            
            <ErrorMessage message={error} />

            <div className="pay-actions">{buttons}</div>
        </form>
    );
}
