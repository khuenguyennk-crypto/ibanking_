import {request} from './http.js';

export const getAccounts = () => request('/api/accounts');

export const revealAccount = (accountId, password) => request(`/api/accounts/${accountId}/reveal`, {method: 'POST', body: {password},});
