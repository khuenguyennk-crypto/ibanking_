import {accountLabel, formatMoney} from '../../utils/format.js';
import ErrorMessage from '../common/ErrorMessage.jsx';

export default function BankAccount(props) {
    const accounts = props.accounts;
    const account = props.account;
    const tuition = props.tuition;

    let selectedId = '';
    if (account) {selectedId = account.bank_account_id;}

    let notEnough = false;
    if (account && tuition) {notEnough = Number(account.balance) < Number(tuition.amount);}

    let canContinue = false;
    if (account && tuition && tuition.status === 'unpaid') {canContinue = true;}

    let balanceLine = null;
    if (account) {
        balanceLine = (
        <span>
            Số dư khả dụng: <strong>{formatMoney(account.balance)}</strong>
        </span>
        );
    }

    let warningLine = null;
    if (notEnough) {warningLine = <span className="pay-error"> Không đủ để thanh toán khoản này.</span>;}

    function handleChange(event) {props.onSelect(Number(event.target.value));}
    return (
        <section className="pay-card">
            <label className="pay-label" htmlFor="account">
                Tài khoản thanh toán
            </label>

            <select id="account" className="pay-select" value={selectedId} onChange={handleChange}>
                <option value="" disabled>
                    Chọn tài khoản ngân hàng
                </option>
                {accounts.map(function (a) {
                    return (
                        <option key={a.bank_account_id} value={a.bank_account_id}>
                            {accountLabel(a)}
                        </option>
                    );
                })}
            </select>

            <p className="pay-muted pay-helper">
                {balanceLine}
                {warningLine}
            </p>

            <ErrorMessage message={props.error} />

            <button type="button" className="pay-btn pay-btn-block" disabled={!canContinue} onClick={props.onContinue}>
                Tiếp tục thanh toán
            </button>
        </section>
    );
}
