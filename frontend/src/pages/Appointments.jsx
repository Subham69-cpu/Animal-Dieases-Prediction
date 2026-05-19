import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function Appointments() {
  const { user } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [q, setQ] = useState("");
  const [species, setSpecies] = useState("");
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const params = {};
        if (q) params.q = q;
        if (species) params.species = species;
        const { data } = await api.get("/doctors", { params });
        setDoctors(data.doctors || []);
      } catch {
        setMsg("Could not load doctors. Is the API running?");
      } finally {
        setLoading(false);
      }
    })();
  }, [q, species]);

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Veterinary appointments</h1>
      <div className="flex flex-wrap gap-3">
        <input
          placeholder="Search name or specialization"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 flex-1 min-w-[200px]"
        />
        <select
          value={species}
          onChange={(e) => setSpecies(e.target.value)}
          className="rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2"
        >
          <option value="">All species</option>
          {["cow", "dog", "cat", "goat", "poultry"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
      {msg && <p className="text-amber-600 text-sm">{msg}</p>}
      {loading ? (
        <p>Loading…</p>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {doctors.map((d, i) => (
            <motion.div
              key={d.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-900 shadow-sm"
            >
              <h3 className="font-display font-semibold text-lg">{d.name}</h3>
              <p className="text-sm text-brand-700 dark:text-brand-400">{d.specialization}</p>
              <p className="text-xs text-slate-500 mt-2">{d.clinic_location}</p>
              <p className="text-sm mt-2">₹{d.consultation_fee_inr} · ★ {d.rating_avg}</p>
              <Link to={`/doctors/${d.id}`} className="inline-block mt-3 text-brand-600 font-semibold text-sm">
                View profile & book →
              </Link>
            </motion.div>
          ))}
        </div>
      )}
      {!user && (
        <p className="text-sm text-slate-500">
          <Link to="/login" className="text-brand-600 font-medium">
            Log in
          </Link>{" "}
          to book and manage appointments.
        </p>
      )}
    </div>
  );
}
