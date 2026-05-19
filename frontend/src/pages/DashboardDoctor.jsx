import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function DashboardDoctor() {
  const [data, setData] = useState(null);
  useEffect(() => {
    (async () => {
      try {
        const { data: d } = await api.get("/dashboard/doctor");
        setData(d);
      } catch {
        setData({ message: "Could not load" });
      }
    })();
  }, []);

  if (!data) return <p>Loading…</p>;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Clinic schedule</h1>
      {data.message && <p className="text-slate-500">{data.message}</p>}
      <p className="text-sm text-slate-600">Total consultations logged: {data.total_consultations ?? 0}</p>
      <ul className="space-y-2">
        {(data.upcoming_appointments || []).map((a) => (
          <li key={a.id} className="rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <p className="font-medium">{a.scheduled_at}</p>
            <p className="text-sm text-slate-500">{a.patient_email}</p>
            <p className="text-sm">{a.animal_name}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
