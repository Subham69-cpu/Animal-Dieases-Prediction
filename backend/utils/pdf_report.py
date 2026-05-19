"""Generate simple PDF health reports using fpdf2."""
import io
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)


def build_prediction_pdf(prediction: dict) -> bytes | None:
    """Return PDF bytes for a prediction record; None if fpdf2 missing."""
    try:
        from fpdf import FPDF
    except ImportError:
        log.warning("fpdf2 not installed; PDF export unavailable.")
        return None

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 14)
            self.cell(0, 10, "Smart Veterinary Healthcare — Report", ln=True)
            self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    pdf.ln(4)
    for key in [
        "animal_type",
        "disease",
        "final_prediction",
        "cnn_confidence",
        "ml_confidence",
        "final_confidence",
        "severity",
        "recommended_action",
    ]:
        if key in prediction and prediction[key] is not None:
            label = key.replace("_", " ").title()
            val = prediction[key]
            if isinstance(val, float):
                val = f"{val:.2%}" if "confidence" in key else f"{val:.4f}"
            pdf.multi_cell(0, 8, f"{label}: {val}")
    if prediction.get("precautions"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Precautions:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for p in prediction["precautions"]:
            pdf.multi_cell(0, 8, f"- {p}")
    if prediction.get("treatment"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Treatment guidance:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, str(prediction["treatment"]))
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
