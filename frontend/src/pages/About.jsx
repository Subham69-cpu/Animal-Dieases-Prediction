export default function About() {
  return (
    <article className="max-w-3xl mx-auto space-y-4 text-slate-700 dark:text-slate-300 leading-relaxed">
      <h1 className="font-display text-3xl font-bold text-slate-900 dark:text-white">About this project</h1>
      <p>
        This platform demonstrates a production-style layout for <strong>Smart Veterinary Healthcare</strong> using Flask,
        MongoDB, React, Tailwind CSS, and Framer Motion. Deep learning uses a Keras CNN saved as <code className="bg-slate-100 dark:bg-slate-800 px-1 rounded">model.h5</code>; symptom
        models combine <strong>Random Forest</strong> and <strong>XGBoost</strong> in a soft-voting ensemble.
      </p>
      <p>
        Hybrid prediction fuses CNN and symptom probabilities with configurable weights. JWT secures role-based areas (user,
        veterinarian, admin). Appointment flows include optional SMTP notifications when <code className="bg-slate-100 dark:bg-slate-800 px-1 rounded">EMAIL_ENABLED=true</code>.
      </p>
      <p>
        Synthetic datasets can be generated automatically for local training. Always consult a licensed veterinarian for real
        cases—this stack is for learning and prototyping.
      </p>
    </article>
  );
}
