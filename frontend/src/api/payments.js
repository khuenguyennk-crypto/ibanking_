import {request} from './http.js';

export const createPayment = ({bank_account_id, tuition_id}) => request('/api/payments', {method: 'POST', body: {bank_account_id, tuition_id}});

export const confirmPayment = (transactionId, otpCode) => request(`/api/payments/${transactionId}/confirm`, {method: 'POST', body: {otp_code: otpCode}});

export const resendOtp = (transactionId) => request(`/api/payments/${transactionId}/resend-otp`, {method: 'POST'});

export const getPayments = () => request('/api/payments');

export const getPayment = (transactionId) => request(`/api/payments/${transactionId}`);

export const cancelPayment = (transactionId) => request(`/api/payments/${transactionId}/cancel`, {method: 'POST'});
