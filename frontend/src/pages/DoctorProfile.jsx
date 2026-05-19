import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function DoctorProfile() {
  const { id } = useParams();
  const nav = useNavigate();
  const { user } = useAuth();
  const [d, setD] = useState(null);
  const [when, setWhen] = useState("");
  const [animal, setAnimal] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get(`/doctor/${id}`);
        if (data.error) throw new Error(data.error);
        setD(data);
      } catch {
        setD(null);
      }
    })();
  }, [id]);

  const book = async () => {
    if (!user) {
      nav("/login");
      return;
    }
    setStatus("");
    try {
      await api.post("/appointment/book", {
        doctor_id: id,
        scheduled_at: when,
        animal_name: animal,
        notes: note,
      });
      setStatus("Booked! Check your dashboard.");
    } catch (e) {
      setStatus(e.response?.data?.error || e.message);
    }
  };

  if (!d) return <p className="text-slate-500">Loading doctor…</p>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="font-display text-3xl font-bold">{d.name}</h1>
      <p className="text-brand-600 font-medium">{d.specialization}</p>
      <p className="text-slate-600 dark:text-slate-300">{d.clinic_location}</p>
      <p className="text-sm">Experience: {d.experience_years} years</p>
      <p className="text-sm">Fee: ₹{d.consultation_fee_inr}</p>
      <p className="text-sm">Rating: {d.rating_avg} ({d.review_count} reviews)</p>
      <div>
        <h3 className="font-semibold mt-4">Timings</h3>
        <ul className="list-disc pl-5 text-sm">
          {(d.available_timings || []).map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3">
        <h3 className="font-display font-semibold">Book appointment</h3>
        <input
          type="datetime-local"
          value={when}
          onChange={(e) => setWhen(e.target.value)}
          className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950"
        />
        <input
          placeholder="Animal name"
          value={animal}
          onChange={(e) => setAnimal(e.target.value)}
          className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950"
        />
        <textarea
          placeholder="Notes"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="w-full rounded-lg border px-3 py-2 dark:bg-slate-950"
          rows={2}
        />
        <button type="button" onClick={book} className="rounded-xl bg-brand-600 text-white px-4 py-2 font-semibold">
          Confirm booking
        </button>
        {status && <p className="text-sm">{status}</p>}
      </div>
    </div>
  );
}
