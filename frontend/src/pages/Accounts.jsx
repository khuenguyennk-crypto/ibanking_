import {useEffect, useState} from 'react';
import {Link} from 'react-router-dom';
import {ArrowLeft, Landmark, Lock, LockOpen} from 'lucide-react';
import {getAccounts, revealAccount} from '../api/accounts.js';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import Loading from '../components/common/Loading.jsx';
import {formatMoney} from '../utils/format.js';

const UNLOCK_SECONDS = 60;

export default function Accounts() {
  const [accounts, setAccounts] = useState(null);
  const [error, setError] = useState('');

  const [asking, setAsking] = useState(null);
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [unlockError, setUnlockError] = useState('');

  const [open, setOpen] = useState(null);
  const [secondsLeft, setSecondsLeft] = useState(0);

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

  useEffect(() => {
    if (!open) {return undefined;}
    if (secondsLeft <= 0) {
      setOpen(null);
      return undefined;
    }
    const timerId = setTimeout(() => {setSecondsLeft(secondsLeft - 1);}, 1000);
    return () => clearTimeout(timerId);
  }, [open, secondsLeft]);

  function startUnlock(id) {
    setAsking(id);
    setPassword('');
    setUnlockError('');
  }

  function cancelUnlock() {
    setAsking(null);
    setPassword('');
    setUnlockError('');
  }

  async function handleUnlock(event) {
    event.preventDefault();
    if (password === '') {
      setUnlockError('Vui lòng nhập mật khẩu.');
      return;
    }

    setBusy(true);
    setUnlockError('');
    try {
      const detail = await revealAccount(asking, password);
      setOpen({ id: asking, detail: detail });
      setSecondsLeft(UNLOCK_SECONDS);
      cancelUnlock();
    } catch (err) {
      setUnlockError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value);
  }

  function handleRelock() {
    setOpen(null);
  }

  let loadingLine = null;
  if (!accounts && !error) {loadingLine = <Loading />;}

  let list = null;
  if (accounts) {
    list = accounts.map(function (a) {
      let isOpen = false;
      if (open && open.id === a.bank_account_id) {isOpen = true;}
      const isAsking = asking === a.bank_account_id;


      let detail = null;
      let accountNum = a.account_num;
      if (isOpen) {
        detail = open.detail;
        accountNum = detail.account_num;
      }

      let lockClass = 'pay-lock';
      let lockIcon = <Lock size={14} />;
      let lockText = 'Đã khóa';
      let cardClass = 'pay-acc';
      if (isOpen) {
        lockClass = 'pay-lock is-open';
        lockIcon = <LockOpen size={14} />;
        lockText = 'Đã mở';
        cardClass = 'pay-acc open';
      }

      const head = (
        <>
          <span className="pay-bankic"><Landmark size={20} /></span>
          <span className="pay-acc-title">
            <b>{a.bank_name}</b>
            <span className="pay-muted">{accountNum}</span>
          </span>
          <span className="pay-acc-bal">{formatMoney(a.balance)}</span>
          <span className={lockClass}>
            {lockIcon}
            {lockText}
          </span>
        </>
      );

      function handleStart() {startUnlock(a.bank_account_id);}

      let headBlock = null;
      if (isOpen || isAsking) {
        headBlock = <div className="pay-acc-head">{head}</div>;
      } else {
        headBlock = (
          <button type="button" className="pay-acc-head" onClick={handleStart}>
            {head}
          </button>
        );
      }

      let askBlock = null;
      if (isAsking) {
        let unlockText = 'Mở khóa';
        if (busy) {unlockText = 'Đang kiểm tra...';}

        askBlock = (
          <form className="pay-acc-body" onSubmit={handleUnlock}>
            <label className="pay-label" htmlFor="unlock-pw">
              Nhập mật khẩu đăng nhập để mở khóa
            </label>
            <div className="pay-unlock">
              <input id="unlock-pw" type="password" autoFocus autoComplete="current-password" placeholder="Mật khẩu" value={password} disabled={busy} onChange={handlePasswordChange} />
              <button type="submit" className="pay-btn" disabled={busy}>
                {unlockText}
              </button>
              <button type="button" className="pay-btn-ghost" onClick={cancelUnlock} disabled={busy}>
                Hủy
              </button>
            </div>
            <ErrorMessage message={unlockError} />
          </form>
        );
      }

      let detailBlock = null;
      if (isOpen) {
        detailBlock = (
          <div className="pay-acc-body">
            <dl className="pay-dl">
              <div><dt>Ngân hàng</dt><dd>{detail.bank_name}</dd></div>
              <div><dt>Số tài khoản</dt><dd>{detail.account_num}</dd></div>
              <div><dt>Chủ tài khoản</dt><dd>{detail.account_name}</dd></div>
            </dl>
            <p className="pay-muted">Tự khóa lại sau {secondsLeft} giây.</p>
            <div>
              <button type="button" className="pay-btn-ghost" onClick={handleRelock}>
                Khóa lại
              </button>
            </div>
          </div>
        );
      }

      return (
        <article key={a.bank_account_id} className={cardClass}>
          {headBlock}
          {askBlock}
          {detailBlock}
        </article>
      );
    });
  }

  return (
    <section className="pay-card">
      <div className="pay-back">
        <Link to="/home" className="icon-btn" aria-label="Quay lại trang chủ">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1>Tài khoản ngân hàng</h1>
          <p className="pay-muted">Nhập mật khẩu để xem thông tin thẻ.</p>
        </div>
      </div>

      <ErrorMessage message={error} />
      {loadingLine}

      <div className="pay-acc-list">{list}</div>
    </section>
  );
}
