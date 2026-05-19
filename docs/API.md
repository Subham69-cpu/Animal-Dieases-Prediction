# HTTP API reference

Base URL: your API host (e.g. `http://127.0.0.1:5000`).  
Auth: `Authorization: Bearer <JWT>` for protected routes.

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness; reports Mongo connectivity. |

## Authentication

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/signup` | JSON `{ email, password, name?, role?: "user"\|"veterinarian" }` | Creates user; returns `token`. |
| POST | `/login` | JSON `{ email, password }` | Returns `token` and `user`. |

## Prediction

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/predict/symptoms` | Yes | JSON body: `animal_type` + boolean-ish `fever`, `cough`, `vomiting`, `diarrhea`, `skin_problem`, `breathing_issue`, `appetite_loss`, `weakness` (0/1). |
| POST | `/predict/symptoms/demo` | No | Same body; no persistence. |
| POST | `/predict/image` | Yes | `multipart/form-data`: `animal_type`, `image` file. |
| POST | `/predict/image/demo` | No | Same as image. |
| POST | `/predict/hybrid` | Yes | Multipart or JSON + optional `image`: symptoms + CNN fusion. |
| POST | `/predict/hybrid/demo` | No | Same as hybrid. |

**Sample symptom JSON**

```json
{
  "animal_type": "cow",
  "fever": 1,
  "cough": 0,
  "vomiting": 0,
  "diarrhea": 1,
  "skin_problem": 0,
  "breathing_issue": 0,
  "appetite_loss": 1,
  "weakness": 1
}
```

**Typical success payload**

- `final_prediction`, `severity`, `precautions[]`, `treatment`, `vet_recommendation`, `recommended_action`
- `cnn_confidence`, `ml_confidence`, `final_confidence` (when applicable)

## Doctors & appointments

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/doctors?q=&species=` | No | List / search doctors. |
| GET | `/doctor/<id>` | No | Doctor profile. |
| POST | `/appointment/book` | Yes | JSON `{ doctor_id, scheduled_at (ISO8601), animal_name?, notes? }`. |
| GET | `/appointments` | Yes | List for user or linked veterinarian. |
| PUT | `/appointment/update` | Yes | JSON `{ appointment_id, status?, scheduled_at?, notes?, treatment_notes? }`. |
| PUT | `/appointments/<id>` | Yes | Same fields in JSON (REST style). |

## Dashboards & data

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/dashboard/user` | user, admin | Totals, recent predictions. |
| GET | `/dashboard/doctor` | veterinarian, admin | Upcoming appointments. |
| GET | `/dashboard/admin` | admin | Aggregates and disease trends. |
| GET | `/animals` | Any user | Saved animals. |
| POST | `/animals` | Any user | `{ name, species?, notes? }`. |
| GET | `/export/prediction/pdf` | Any user | Latest prediction as PDF. |

## Training (admin)

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/train/cnn` | admin | Runs `scripts/train_cnn.py` (long-running). |
| POST | `/train/ml` | admin | Runs `scripts/train_ml.py`. |

## Error format

JSON `{ "error": "message" }` with appropriate HTTP status (`400`, `401`, `403`, `404`, `503`, `504`).
