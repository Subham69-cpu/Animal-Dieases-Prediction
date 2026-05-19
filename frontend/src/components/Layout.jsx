import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext.jsx";
import { useTheme } from "../context/ThemeContext.jsx";

const linkClass = ({ isActive }) =>
  `px-3 py-2 rounded-lg text-sm font-medium transition ${
    isActive ? "bg-brand-600 text-white" : "text-slate-600 dark:text-slate-300 hover:bg-slate-200/80 dark:hover:bg-slate-800"
  }`;

export default function Layout() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();

  return (
    <div className="min-h-screen flex flex-col">
      <motion.header
        initial={{ y: -12, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="border-b border-slate-200/80 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-40"
      >
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3 justify-between">
          <NavLink to="/" className="font-display font-bold text-lg text-brand-700 dark:text-brand-500">
            VetAI Care
          </NavLink>
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink to="/" className={linkClass} end>
              Home
            </NavLink>
            <NavLink to="/predict" className={linkClass}>
              AI Prediction
            </NavLink>
            <NavLink to="/predict/image" className={linkClass}>
              Image Scan
            </NavLink>
            <NavLink to="/appointments" className={linkClass}>
              Appointments
            </NavLink>
            <NavLink to="/about" className={linkClass}>
              About
            </NavLink>
            {user && (
              <NavLink to="/dashboard" className={linkClass}>
                Dashboard
              </NavLink>
            )}
          </nav>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggle}
              className="rounded-lg border border-slate-200 dark:border-slate-700 px-3 py-1.5 text-xs font-medium"
            >
              {dark ? "Light" : "Dark"}
            </button>
            {user ? (
              <button type="button" onClick={logout} className="text-sm text-red-600 dark:text-red-400 font-medium">
                Log out
              </button>
            ) : (
              <NavLink to="/login" className="rounded-lg bg-brand-600 text-white px-4 py-2 text-sm font-semibold">
                Login
              </NavLink>
            )}
          </div>
        </div>
      </motion.header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-sm text-slate-500">
        Smart Veterinary Healthcare System — educational demo. Not a substitute for licensed veterinary care.
      </footer>
    </div>
  );
}
