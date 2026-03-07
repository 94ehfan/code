import { useState, useEffect, useCallback } from "react";
import { User } from "../types";
import * as api from "../services/api";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api
        .getMe()
        .then(setUser)
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const { access_token } = await api.login(username, password);
    localStorage.setItem("token", access_token);
    const me = await api.getMe();
    setUser(me);
  }, []);

  const register = useCallback(
    async (data: {
      username: string;
      display_name: string;
      password: string;
      phone_number?: string;
    }) => {
      const { access_token } = await api.register(data);
      localStorage.setItem("token", access_token);
      const me = await api.getMe();
      setUser(me);
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  return { user, loading, login, register, logout };
}
