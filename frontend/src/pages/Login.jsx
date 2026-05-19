import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login, signup } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("user");
  const [err, setErr] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      if (mode === "login") await login(email, password);
      else await signup({ email, password, name, role });
      const to = loc.state?.from?.pathname || "/dashboard";
      nav(to, { replace: true });
    } catch (ex) {
      setErr(ex.response?.data?.error || ex.message);
    }
  };

  return (
    <div className="max-w-md mx-auto rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-lg">
      <div className="flex gap-2 mb-6">
        {["login", "register"].map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`flex-1 py-2 rounded-lg font-semibold capitalize ${mode === m ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800"}`}
          >
            {m}
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="space-y-4">
        {mode === "register" && (
          <>
            <input required placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950" />
            <select value={role} onChange={(e) => setRole(e.target.value)} className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950">
              <option value="user">Pet / farm owner</option>
              <option value="veterinarian">Veterinarian</option>
            </select>
          </>
        )}
        <input required type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950" />
        <input required type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950" />
        {err && (
          <p className="text-red-600 text-sm">
            {err}
            {typeof err === "string" && /mongo|database|sqlite/i.test(err) && (
              <span className="block mt-2 text-slate-600 dark:text-slate-400 font-normal">
                Tip: If MongoDB is not installed, the backend uses local SQLite (<code className="text-xs bg-slate-100 dark:bg-slate-800 px-1 rounded">data/vet_local.db</code>). Restart the API server after updating. Or install MongoDB and set <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1 rounded">MONGO_URI</code> in <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1 rounded">.env</code>.
              </span>
            )}
          </p>
        )}
        <button type="submit" className="w-full rounded-xl bg-brand-600 text-white font-semibold py-3">
          {mode === "login" ? "Sign in" : "Create account"}
        </button>
      </form>
      <p className="text-xs text-slate-500 mt-4">
        Veterinarians: use an email that matches a seeded doctor profile (see README) to see appointments on the doctor dashboard.
      </p>
    </div>
  );
}
