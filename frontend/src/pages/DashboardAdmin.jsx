import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "../api/client.js";

export default function DashboardAdmin() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data: d } = await api.get("/dashboard/admin");
        if (d.error) throw new Error(d.error);
        setData(d);
      } catch (e) {
        setErr(e.response?.data?.error || e.message);
      }
    })();
  }, []);

  if (err) return <p className="text-red-600">{err}</p>;
  if (!data) return <p>Loading…</p>;

  const trends = (data.disease_trends || []).map((t) => ({ name: (t.disease || "?").slice(0, 12), count: t.count }));

  return (
    <div className="space-y-8">
      <h1 className="font-display text-3xl font-bold">Admin analytics</h1>
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border p-4">
          <p className="text-sm text-slate-500">Users</p>
          <p className="text-3xl font-bold">{data.total_users}</p>
        </div>
        <div className="rounded-2xl border p-4">
          <p className="text-sm text-slate-500">Predictions</p>
          <p className="text-3xl font-bold">{data.total_predictions}</p>
        </div>
        <div className="rounded-2xl border p-4">
          <p className="text-sm text-slate-500">Appointments</p>
          <p className="text-3xl font-bold">{data.total_appointments}</p>
        </div>
      </div>
      <div className="h-72 rounded-2xl border p-4 bg-white dark:bg-slate-900">
        <h2 className="font-semibold mb-2">Disease trends</h2>
        <ResponsiveContainer width="100%" height="85%">
          <BarChart data={trends}>
            <XAxis dataKey="name" interval={0} angle={-25} textAnchor="end" height={70} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#15803d" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-slate-500">{data.model_note}</p>
    </div>
  );
}
