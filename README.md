# Smart Veterinary Healthcare System

Full-stack **animal disease prediction** (CNN + Random Forest / XGBoost hybrid) and **veterinary appointment** platform with JWT role-based access, MongoDB persistence, React + Tailwind + Framer Motion UI, and Docker deployment.

## Stack

| Layer | Technology |
|--------|------------|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion, Recharts |
| API | Python 3.11, Flask, PyJWT, Flask-CORS |
| Database | MongoDB |
| CNN | TensorFlow / Keras (`cnn_model/model.h5`) |
| Symptom ML | scikit-learn Pipeline (OneHotEncoder + VotingClassifier RF + XGBoost) |
| Image I/O | OpenCV, Pillow |

## Quick start (local)

### 1. MongoDB

Run MongoDB locally (default `mongodb://localhost:27017/vet_healthcare`) or use Docker:

```bash
docker run -d -p 27017:27017 --name vet-mongo mongo:7
```

### 2. Backend

```bash
cd "path/to/Animal Dieases Prediction"
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
copy .env.example .env          # then edit secrets and ADMIN_* if needed
python scripts\generate_datasets.py --per-class 40
python scripts\train_ml.py
python scripts\train_cnn.py       # requires TensorFlow; may take several minutes
python backend\run.py
```

API: `http://127.0.0.1:5000/health`

If models are missing, authenticated prediction routes return `503` with a hint; **demo** routes (`/predict/symptoms/demo`, `/predict/hybrid/demo`, `/predict/image/demo`) work the same without saving history.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to the Flask port.

### 4. Roles & admin

- Register as **user** or **veterinarian**.
- **Admin**: set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`; on startup an admin account is created if that email is not already registered.
- **Veterinarian dashboard**: after registering as **veterinarian**, use an email that matches a seeded doctor profile, for example:
  - `ananya.sharma@clinic.example` (large animal)
  - `marcus.lee@clinic.example` (small animal)
  - `priya.nair@clinic.example` (poultry)

## Docker Compose

From the project root:

```bash
docker compose build
docker compose up
```

Then run dataset generation and training **inside** the API container (or on the host before build) so `cnn_model/` and `ml_model/` exist:

```bash
docker compose exec api python scripts/generate_datasets.py
docker compose exec api python scripts/train_ml.py
docker compose exec api python scripts/train_cnn.py
```

## Deploy (Render / Railway)

1. **MongoDB**: use Atlas or a managed Mongo URL; set `MONGO_URI` and `MONGO_DB_NAME` on the API service.
2. **API**: deploy repo with `Dockerfile.backend` or `gunicorn backend.run:app`; set `SECRET_KEY`, `JWT_SECRET`, `CORS_ORIGINS` (your frontend origin).
3. **Frontend**: build with `VITE_API_URL=https://your-api-host` (no trailing slash). Serve `frontend/dist` as static files or use `Dockerfile.frontend` with build-arg `VITE_API_URL`.

## Project layout

```
backend/           # Flask app, controllers, services, utils
scripts/           # generate_datasets, train_cnn, train_ml
frontend/          # Vite React SPA
dataset/           # generated images + symptom_dataset.csv (gitignored except .gitkeep)
cnn_model/         # model.h5 + class_indices.json
ml_model/          # symptom_pipeline.joblib + symptom_meta.json
docs/              # API reference
```

## API documentation

See [docs/API.md](docs/API.md).

## Legal / ethics

This project is for **education and prototyping**. It is **not** a licensed veterinary diagnostic tool. Always consult a qualified veterinarian for real animals.
