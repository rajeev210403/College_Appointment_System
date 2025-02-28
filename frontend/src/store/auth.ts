import { create } from 'zustand';
import api from '../lib/axios';

interface User {
  id: number;
  email: string;
  name: string;
  role: 'student' | 'professor';
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; name: string; role: 'student' | 'professor' }) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { token, user } = response.data;
    localStorage.setItem('token', token);
    set({ token, user });
  },
  register: async (data) => {
    await api.post('/auth/register', data);
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  },
}));