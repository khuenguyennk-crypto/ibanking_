export function formatMoney(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value));
}

export function formatDateTime(value) {
    if (!value) return '—';

    let iso = value;
    if (!value.endsWith('Z') && !value.includes('+')) {iso = value + 'Z';}

    return new Date(iso).toLocaleString('vi-VN');
}

export const STATUS_LABELS = {
    pending: 'Đang khởi tạo',
    otp_sent: 'Chờ nhập OTP',
    processing: 'Đang xử lý',
    success: 'Thành công',
    failed: 'Thất bại',
    expired: 'Hết hạn',
    cancelled: 'Đã hủy',
};

export function last4(num) {
    if (!num) return '';
    return String(num).slice(-4);
}

export function accountLabel(account) {
    return account.bank_name + ' **** ' + last4(account.account_num);
}

