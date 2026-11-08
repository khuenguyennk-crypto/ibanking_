const TOKEN_KEY = 'ibanking_access_token';

export function getAccessToken() {
    return sessionStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token) {
    if (token) {
        sessionStorage.setItem(TOKEN_KEY, token);
    } else {
        sessionStorage.removeItem(TOKEN_KEY);
    }
}

export function clearAccessToken() {
    sessionStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
    constructor(message, {status = 0, code = 'NETWORK_ERROR', details = null,} = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.code = code;
        this.details = details;
    }
}

export async function request(path, options = {}) {
    const {method = 'GET', body, headers = {}, auth = true, signal,} = options;

    const requestHeaders = new Headers(headers);
    if (body !== undefined && !requestHeaders.has('Content-Type')) {
        requestHeaders.set('Content-Type', 'application/json');
    }

    const token = getAccessToken();
    if (auth && token) {
        requestHeaders.set('Authorization', `Bearer ${token}`);
    }

    let response;
    try {
        response = await fetch(path, {method, headers: requestHeaders, body: body === undefined ? undefined : JSON.stringify(body), signal,});
    } catch (error) {
        if (error.name === 'AbortError') throw error;
        throw new ApiError('Không thể kết nối đến máy chủ. Vui lòng thử lại.', {code: 'NETWORK_ERROR'});
    }

    const raw = await response.text();
    let data = null;
    if (raw) {try {data = JSON.parse(raw);} catch {data = raw;}}

    if (!response.ok) {
        let errorData = data;
        if (data && data.error) {
            errorData = data.error;
        } else if (data && data.detail) {
            errorData = data.detail;
        }

        let message = `Yêu cầu thất bại (HTTP ${response.status}).`;
        if (errorData && errorData.message) {
            message = errorData.message;
        } else if (typeof errorData === 'string') {
            message = errorData;
        }

        let code = `HTTP_${response.status}`;
        if (errorData && errorData.code) {code = errorData.code;}

        if (response.status === 401 && auth && token) {
            clearAccessToken(); 
            window.dispatchEvent(new Event('ibanking:unauthorized'));
        }

        throw new ApiError(message, {
            status: response.status,
            code,
            details: errorData,
        });
    }

    return data;
}
