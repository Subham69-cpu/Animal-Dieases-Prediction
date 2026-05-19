import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="grid md:grid-cols-2 gap-10 items-center">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
          <p className="text-brand-600 dark:text-brand-400 font-semibold text-sm uppercase tracking-wide">CNN + Machine Learning</p>
          <h1 className="font-display text-4xl md:text-5xl font-bold mt-2 text-slate-900 dark:text-white leading-tight">
            Smart Veterinary Healthcare for your herd & companions
          </h1>
          <p className="mt-4 text-slate-600 dark:text-slate-300 text-lg">
            Combine symptom-based Random Forest / XGBoost models with CNN image analysis. Book verified veterinarians and keep
            medical history in one secure workspace.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/predict"
              className="inline-flex items-center justify-center rounded-xl bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 font-semibold shadow-lg shadow-brand-600/25"
            >
              Start AI diagnosis
            </Link>
            <Link
              to="/appointments"
              className="inline-flex items-center justify-center rounded-xl border border-slate-300 dark:border-slate-600 px-6 py-3 font-semibold"
            >
              Find a vet
            </Link>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="relative rounded-3xl bg-gradient-to-br from-brand-500 to-emerald-800 p-8 text-white shadow-2xl"
        >
          <div className="absolute inset-0 rounded-3xl bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iLjA4Ij48cGF0aCBkPSJNMzYgMzRjMC0yLjIgMS44LTQgNC00czQgMS44IDQgNC0xLjggNC00IDRzLTQtMS44LTQtNHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-40" />
          <h3 className="font-display text-2xl font-semibold relative">Supported species</h3>
          <ul className="mt-4 space-y-2 relative text-white/90">
            {["Cow", "Dog", "Cat", "Goat", "Poultry"].map((s) => (
              <li key={s} className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-white" />
                {s}
              </li>
            ))}
          </ul>
          <p className="mt-6 text-sm text-white/80 relative">
            Hybrid fusion blends CNN confidence with structured symptom models for a single actionable report.
          </p>
        </motion.div>
      </section>
    </div>
  );
}
