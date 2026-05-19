import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ||
  (import.meta.env.DEV ? "/api" : "http://127.0.0.1:5000");

export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const t = localStorage.getItem("token");
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

export function setAuthToken(token) {
  if (token) localStorage.setItem("token", token);
  else localStorage.removeItem("token");
}
