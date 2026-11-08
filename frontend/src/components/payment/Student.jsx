import {Search} from 'lucide-react';
import ErrorMessage from '../common/ErrorMessage.jsx';

export default function Student(props) {
    const value = props.value;
    const student = props.student;

    function handleChange(event) {
        props.onChange(event.target.value);
    }

    function handleSubmit(event) {
        event.preventDefault();
        props.onSearch();
    }

    let busyLine = null;
    if (props.busy) {busyLine = <p className="pay-muted pay-block">Đang tra cứu...</p>;}

    let studentBlock = null;
    if (student && !props.busy) {
        studentBlock = (
        <div className="pay-block">
            <h2>Thông tin sinh viên</h2>
            <dl className="pay-dl">
            <div><dt>Họ và tên</dt><dd>{student.full_name}</dd></div>
            <div><dt>MSSV</dt><dd>{student.student_id}</dd></div>
            </dl>
        </div>
        );
    }

    let hintLine = null;
    if (value.trim() === '') {
        hintLine = <p className="pay-muted pay-block">Hệ thống tự tra cứu sau khi bạn nhập MSSV.</p>;
    }

    return (
        <section className="pay-card">
            <label className="pay-label" htmlFor="mssv">
                Mã số sinh viên
            </label>

            <form className="pay-row" onSubmit={handleSubmit}>
                <input id="mssv" autoComplete="off" placeholder="Nhập MSSV" value={value} onChange={handleChange} />
                <button type="submit" className="pay-btn pay-btn-icon" aria-label="Tra cứu"><Search size={18} /></button>
            </form>

            {busyLine}
            <ErrorMessage message={props.error} />
            {studentBlock}
            {hintLine}
        </section>
    );
}
