import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

const ANIMALS = ["cow", "dog", "cat", "goat", "poultry"];

export default function ImagePredict() {
  const { user } = useAuth();
  const [animal, setAnimal] = useState("dog");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  const run = async () => {
    if (!file) {
      setErr("Choose an image");
      return;
    }
    setLoading(true);
    setErr("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("animal_type", animal);
      fd.append("image", file);
      const path = user ? "/predict/image" : "/predict/image/demo";
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
    <div className="max-w-xl mx-auto space-y-6">
      <h1 className="font-display text-3xl font-bold">CNN image scan</h1>
      <p className="text-slate-600 dark:text-slate-400">Upload skin, eye, or mouth region photos for visible-condition screening.</p>
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 space-y-4">
        <label className="block text-sm font-medium">Animal</label>
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
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button type="button" disabled={loading} onClick={run} className="w-full rounded-xl bg-brand-600 text-white font-semibold py-3">
          {loading ? "Running CNN…" : "Analyze image"}
        </button>
        {err && <p className="text-red-600 text-sm">{err}</p>}
      </div>
      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="rounded-2xl bg-slate-100 dark:bg-slate-800 p-6">
          <p className="font-semibold text-lg">{result.final_prediction}</p>
          <p className="text-sm mt-2">Confidence: {((result.cnn_confidence || 0) * 100).toFixed(1)}%</p>
          <p className="text-sm mt-2">{result.recommended_action}</p>
        </motion.div>
      )}
    </div>
  );
}
