import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "../api/client.js";

export default function DashboardUser() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data: d } = await api.get("/dashboard/user");
        if (d.error) throw new Error(d.error);
        setData(d);
      } catch (e) {
        setErr(e.response?.data?.error || e.message);
      }
    })();
  }, []);

  const exportPdf = async () => {
    const res = await api.get("/export/prediction/pdf", { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "prediction_report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (err) return <p className="text-red-600">{err}</p>;
  if (!data) return <p>Loading…</p>;

  const chartData = [
    { name: "Predictions", value: data.total_predictions },
    { name: "Appointments", value: data.total_appointments },
  ];

  return (
    <div className="space-y-8">
      <h1 className="font-display text-3xl font-bold">Your health workspace</h1>
      <div className="h-56 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 bg-white dark:bg-slate-900">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="value" fill="#16a34a" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <button type="button" onClick={exportPdf} className="rounded-xl border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-semibold">
        Export latest prediction PDF
      </button>
      <div>
        <h2 className="font-semibold mb-2">Recent predictions</h2>
        <ul className="space-y-2 text-sm">
          {(data.recent_predictions || []).map((p) => (
            <li key={p.id} className="rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-2">
              {p.final_prediction} — {p.severity}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
