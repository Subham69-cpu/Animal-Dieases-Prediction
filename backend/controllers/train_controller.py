"""Trigger CNN / ML training (admin)."""
import logging
import os
import subprocess
import sys

from ..services import model_service

log = logging.getLogger(__name__)


def _repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def run_cnn_training() -> tuple[dict, int]:
    root = _repo_root()
    script = os.path.join(root, "scripts", "train_cnn.py")
    if not os.path.isfile(script):
        return {"error": "Training script not found"}, 500
    try:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        model_service.reset_caches()
        if proc.returncode != 0:
            log.error("CNN train stderr: %s", proc.stderr[-2000:])
            return {"error": "CNN training failed", "stderr": proc.stderr[-4000:]}, 500
        return {"message": "CNN training completed", "log_tail": proc.stdout[-2000:]}, 200
    except subprocess.TimeoutExpired:
        return {"error": "Training timed out"}, 504
    except Exception as e:
        log.exception(e)
        return {"error": str(e)}, 500


def run_ml_training() -> tuple[dict, int]:
    root = _repo_root()
    script = os.path.join(root, "scripts", "train_ml.py")
    if not os.path.isfile(script):
        return {"error": "Training script not found"}, 500
    try:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=600,
        )
        model_service.reset_caches()
        if proc.returncode != 0:
            return {"error": "ML training failed", "stderr": proc.stderr[-4000:]}, 500
        return {"message": "ML training completed", "log_tail": proc.stdout[-2000:]}, 200
    except Exception as e:
        log.exception(e)
        return {"error": str(e)}, 500
