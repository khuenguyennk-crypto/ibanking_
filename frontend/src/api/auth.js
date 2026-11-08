import {request} from './http.js';

export function login(credentials) {
    return request('/api/auth/login', {method: 'POST', body: credentials, auth: false,});
}

export function getCurrentUser() {
    return request('/api/users/me');
}
