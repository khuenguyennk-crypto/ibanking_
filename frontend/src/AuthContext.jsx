import { createContext, useContext, useEffect, useState } from 'react';

import { getCurrentUser, login as loginRequest } from './api/auth.js';
import { clearAccessToken, getAccessToken, setAccessToken } from './api/http.js';

const AuthContext = createContext(null);

export function AuthProvider(props) {
    const [user, setUser] = useState(null);
    const [status, setStatus] = useState('loading');

    function logout() {
        clearAccessToken();
        setUser(null);
        setStatus('anonymous');
    }

    async function refreshUser() {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        setStatus('authenticated');
        return currentUser;
    }

    async function login(credentials) {
        const result = await loginRequest({
            username: credentials.username.trim(),
            password: credentials.password,
        });

        if (!result || !result.access_token) {throw new Error('Máy chủ không trả về access token hợp lệ.');}

        setAccessToken(result.access_token);

        try {
            return await refreshUser();
        } catch (error) {
            clearAccessToken();
            setUser(null);
            setStatus('anonymous');
            throw error;
        }
    }

    useEffect(() => {
        async function restoreSession() {
            if (!getAccessToken()) {
                setStatus('anonymous');
                return;
            }

            try {
                await refreshUser();
            } catch (error) {
                clearAccessToken();
                setUser(null);
                setStatus('anonymous');
            }
        }
        restoreSession();
    }, []);

    useEffect(() => {
        function handleUnauthorized() {
            setUser(null);
            setStatus('anonymous');
        }
        window.addEventListener('ibanking:unauthorized', handleUnauthorized);
        return () => window.removeEventListener('ibanking:unauthorized', handleUnauthorized);
    }, []);

    const value = {
        user: user,
        status: status,
        isLoading: status === 'loading',
        isAuthenticated: status === 'authenticated',
        login: login,
        logout: logout,
        refreshUser: refreshUser,
    };

    return <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {throw new Error('useAuth phải được sử dụng bên trong AuthProvider.');}
    return context;
}

