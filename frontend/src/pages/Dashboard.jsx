import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Dashboard() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Dashboard</h1>
      <p className="text-slate-600 dark:text-slate-400">Signed in as {user.email} ({user.role})</p>
      <div className="grid sm:grid-cols-2 gap-4">
        {(user.role === "user" || user.role === "admin") && (
          <Link to="/dashboard/user" className="rounded-2xl border p-6 hover:border-brand-500 block">
            <h2 className="font-semibold text-lg">Owner dashboard</h2>
            <p className="text-sm text-slate-500 mt-1">Predictions, animals, PDF export</p>
          </Link>
        )}
        {(user.role === "veterinarian" || user.role === "admin") && (
          <Link to="/dashboard/doctor" className="rounded-2xl border p-6 hover:border-brand-500 block">
            <h2 className="font-semibold text-lg">Veterinarian dashboard</h2>
            <p className="text-sm text-slate-500 mt-1">Upcoming visits</p>
          </Link>
        )}
        {user.role === "admin" && (
          <Link to="/dashboard/admin" className="rounded-2xl border p-6 hover:border-brand-500 block sm:col-span-2">
            <h2 className="font-semibold text-lg">Admin analytics</h2>
            <p className="text-sm text-slate-500 mt-1">Users, predictions, disease trends</p>
          </Link>
        )}
      </div>
    </div>
  );
}
