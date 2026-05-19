import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

const ANIMALS = ["cow", "dog", "cat", "goat", "poultry"];
const SYMPTOMS = [
  ["fever", "Fever"],
  ["cough", "Cough"],
  ["vomiting", "Vomiting"],
  ["diarrhea", "Diarrhea"],
  ["skin_problem", "Skin infection / lesion"],
  ["breathing_issue", "Breathing issue"],
  ["appetite_loss", "Appetite loss"],
  ["weakness", "Weakness"],
];

export default function Predict() {
  const { user } = useAuth();
  const [tab, setTab] = useState("symptoms");
  const [animal, setAnimal] = useState("cow");
  const [flags, setFlags] = useState({});
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  const toggle = (k) => setFlags((f) => ({ ...f, [k]: f[k] ? 0 : 1 }));

  const runSymptoms = async () => {
    setLoading(true);
    setErr("");
    setResult(null);
    try {
      const body = { animal_type: animal, ...SYMPTOMS.reduce((a, [k]) => ({ ...a, [k]: flags[k] ? 1 : 0 }), {}) };
      const path = user ? "/predict/symptoms" : "/predict/symptoms/demo";
      const { data } = await api.post(path, body);
      if (data.error) throw new Error(data.error + (data.hint ? ` — ${data.hint}` : ""));
      setResult(data);
    } catch (e) {
      setErr(e.response?.data?.error || e.message);
    } finally {
      setLoading(false);
    }
  };

  const runHybrid = async () => {
    setLoading(true);
    setErr("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("animal_type", animal);
      SYMPTOMS.forEach(([k]) => fd.append(k, flags[k] ? 1 : 0));
      if (file) fd.append("image", file);
      const path = user ? "/predict/hybrid" : "/predict/hybrid/demo";
      const { data } = await api.post(path, fd, { headers: { "Content-Type": "multipart/form-data" } });
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (e) {
      setErr(e.response?.data?.error || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">AI disease prediction</h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Symptom ML (Random Forest + XGBoost) and optional CNN hybrid. Sign in to save history to your profile.
        </p>
      </div>
      <div className="flex gap-2">
        {["symptoms", "hybrid"].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold capitalize ${
              tab === t ? "bg-brand-600 text-white" : "bg-slate-200 dark:bg-slate-800"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 space-y-4 shadow-sm">
        <label className="block text-sm font-medium">Animal type</label>
        <select
          value={animal}
          onChange={(e) => setAnimal(e.target.value)}
          className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-950 px-3 py-2"
        >
          {ANIMALS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <div>
          <p className="text-sm font-medium mb-2">Symptoms</p>
          <div className="grid sm:grid-cols-2 gap-2">
            {SYMPTOMS.map(([k, label]) => (
              <label key={k} className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={!!flags[k]} onChange={() => toggle(k)} className="rounded border-slate-400" />
                {label}
              </label>
            ))}
          </div>
        </div>
        {tab === "hybrid" && (
          <div>
            <label className="block text-sm font-medium">Optional image for CNN</label>
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mt-1 text-sm" />
          </div>
        )}
        <button
          type="button"
          disabled={loading}
          onClick={tab === "symptoms" ? runSymptoms : runHybrid}
          className="w-full rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-semibold py-3"
        >
          {loading ? "Analyzing…" : tab === "symptoms" ? "Run symptom ML" : "Run hybrid AI"}
        </button>
        {err && <p className="text-red-600 text-sm">{err}</p>}
      </div>
      {result && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-brand-200 dark:border-brand-900 bg-brand-50/50 dark:bg-slate-900 p-6 space-y-2">
          <h2 className="font-display text-xl font-bold">{result.final_prediction || result.disease}</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">Severity: {result.severity}</p>
          {result.cnn_confidence != null && (
            <p className="text-sm">CNN confidence: {(result.cnn_confidence * 100).toFixed(1)}%</p>
          )}
          {result.ml_confidence != null && (
            <p className="text-sm">Symptom ML confidence: {(result.ml_confidence * 100).toFixed(1)}%</p>
          )}
          {result.final_confidence != null && (
            <p className="text-sm font-semibold">Fused confidence: {(result.final_confidence * 100).toFixed(1)}%</p>
          )}
          <p className="text-sm">{result.recommended_action}</p>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {(result.precautions || []).map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
}
