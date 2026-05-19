import { createContext, useContext, useMemo, useState, useCallback } from "react";
import { api, setAuthToken } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const login = useCallback(async (email, password) => {
    const { data } = await api.post("/login", { email, password });
    setAuthToken(data.token);
    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const signup = useCallback(async (payload) => {
    const { data } = await api.post("/signup", payload);
    setAuthToken(data.token);
    localStorage.setItem("user", JSON.stringify({ id: data.user_id, email: data.email, name: data.name, role: data.role }));
    setUser({ id: data.user_id, email: data.email, name: data.name, role: data.role });
    return data;
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    localStorage.removeItem("user");
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, login, signup, logout }), [user, login, signup, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
