import {request} from './http.js';

export const lookupStudent = (studentId) => request(`/api/tuitions/${encodeURIComponent(studentId.trim())}`);

