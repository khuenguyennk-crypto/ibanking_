import {useEffect, useRef, useState} from 'react';

import {getAccounts} from '../api/accounts.js';
import {lookupStudent} from '../api/tuitions.js';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import Loading from '../components/common/Loading.jsx';
import BankAccount from '../components/payment/BankAccount.jsx';
import PaymentModal from '../components/payment/PaymentModal.jsx';
import Student from '../components/payment/Student.jsx';
import Tuition from '../components/payment/Tuition.jsx';

export default function Payment() {
    const [accounts, setAccounts] = useState(null);
    const [accountsError, setAccountsError] = useState('');

    const [mssv, setMssv] = useState('');
    const [tick, setTick] = useState(0);
    const [student, setStudent] = useState(null);
    const [tuitionId, setTuitionId] = useState(null);
    const [accountId, setAccountId] = useState(null);
    const [lookupBusy, setLookupBusy] = useState(false);
    const [lookupError, setLookupError] = useState('');

    const [notice, setNotice] = useState('');
    const [modalOpen, setModalOpen] = useState(false);

    const seqRef = useRef(0);
    const manualRef = useRef(false);

    async function loadAccounts() {
        try {
            const data = await getAccounts();
            setAccounts(data);
        } catch (err) {
            setAccountsError(err.message);
        }
    }

    useEffect(() => {loadAccounts();}, []);

    useEffect(() => {
        const id = mssv.trim();

        seqRef.current = seqRef.current + 1;
        const seq = seqRef.current;

        setStudent(null);
        setTuitionId(null);
        setLookupError('');
        setNotice('');

        if (id === '') {
            setLookupBusy(false);
            return undefined;
        }

        let delay = 600;
        if (manualRef.current) {
            delay = 0;
        }
        manualRef.current = false;

        async function search() {
        setLookupBusy(true);
        try {
            const data = await lookupStudent(id);
            if (seq !== seqRef.current) {
                return;
            }
            setStudent(data);

            const unpaid = data.tuitions.filter((t) => t.status === 'unpaid');
            if (unpaid.length === 1) {
                setTuitionId(unpaid[0].tuition_id);
            }
        } catch (err) {
            if (seq === seqRef.current) {
                setLookupError(err.message);
            }
        } finally {
            if (seq === seqRef.current) {
                setLookupBusy(false);
            }
        }
        }

        const timer = setTimeout(search, delay);
        return () => clearTimeout(timer);
    }, [mssv, tick]);

    function handleSearch() {
        manualRef.current = true;
        setTick(tick + 1);
    }

    async function refreshData() {
        try {
        await loadAccounts();
        if (student) {
            const studentData = await lookupStudent(student.student_id);
            setStudent(studentData);
        }
        } catch (err) {}
    }

    function handleContinue() {
        setNotice('');
        setModalOpen(true);
    }

    function handleClose(arg) {
        setModalOpen(false);

        if (arg && arg.message) {
            setNotice(arg.message);
        }

        if (arg && arg.reset) {
            setMssv('');
            setAccountId(null);
            loadAccounts();
        } else {
            refreshData();
        }
    }

    let tuition = null;
    if (student) {tuition = student.tuitions.find((t) => t.tuition_id === tuitionId);}
    let account = null;
    if (accounts) {account = accounts.find((a) => a.bank_account_id === accountId);}

    let bankBlock = null;
    if (student) {
        if (accountsError) {
            bankBlock = <ErrorMessage message={accountsError} />;
        } else if (!accounts) {
            bankBlock = <Loading />;
        } else {
            bankBlock = <BankAccount accounts={accounts} account={account} tuition={tuition} onSelect={setAccountId} onContinue={handleContinue} error={notice} />;
        }
    }

    return (
        <>
            <h1 className="pay-title">Thanh toán học phí</h1>

            <Student value={mssv} onChange={setMssv} onSearch={handleSearch} busy={lookupBusy} error={lookupError} student={student} />

            {student && (<Tuition tuitions={student.tuitions} selectedId={tuitionId} onSelect={setTuitionId} />)}

            {bankBlock}

            {modalOpen && student && tuition && account && (
                <PaymentModal student={student} tuition={tuition} account={account} onClose={handleClose} onSettled={refreshData} />
            )}
        </>
    );
}
