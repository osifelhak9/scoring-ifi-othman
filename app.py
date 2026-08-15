from __future__ import annotations

import json
import os
import secrets
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, abort, jsonify, render_template, request, session


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = Path(os.getenv("IFI_MODEL_PATH", MODEL_DIR / "modele_responsable_ifi.joblib"))
METADATA_PATH = Path(os.getenv("IFI_METADATA_PATH", MODEL_DIR / "model_metadata.json"))

FIELD_LABELS = {
    "TypeHabi": "Type d'habitat (code)",
    "Ancienneté": "Ancienneté de la relation (code)",
    "Reco_PA": "Type de don / prélèvement automatique (code)",
    "Reco_Année_1er_don": "Période du premier don (code)",
    "Reco_cumul_dons": "Cumul des dons (classe codée)",
    "Reco_don_max": "Don maximal (classe codée)",
    "Reco_don_moy": "Don moyen (classe codée)",
}


def load_artifacts() -> tuple[object, dict]:
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise RuntimeError("Artefacts du modèle absents. Exécuter le script de préparation.")
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if list(model.feature_names_in_) != metadata["features"]:
        raise RuntimeError("Incohérence entre le modèle et ses métadonnées.")
    return model, metadata


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("IFI_SECRET_KEY", "change-me-for-local-demo"),
        MAX_CONTENT_LENGTH=64 * 1024,
        CSRF_ENABLED=True,
        MODEL_VERSION="unknown",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("IFI_COOKIE_SECURE", "0") == "1",
    )
    if test_config:
        app.config.update(test_config)

    model, metadata = load_artifacts()
    app.config["MODEL_VERSION"] = metadata["model_version"]

    def csrf_token() -> str:
        if "csrf_token" not in session:
            session["csrf_token"] = "test-token" if app.testing else secrets.token_urlsafe(24)
        return session["csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self'; "
            "script-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store"
        return response

    def validate_form() -> tuple[dict, list[str]]:
        values: dict[str, str] = {}
        errors: list[str] = []
        for feature in metadata["features"]:
            value = request.form.get(feature, "").strip()
            if not value:
                errors.append(f"Le champ « {FIELD_LABELS[feature]} » est obligatoire.")
            elif value not in metadata["options"][feature]:
                errors.append(f"La valeur du champ « {FIELD_LABELS[feature]} » est invalide.")
            else:
                values[feature] = value
        return values, errors

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            metadata=metadata,
            labels=FIELD_LABELS,
            values=metadata["defaults"],
            errors=[],
            result=None,
        )

    @app.post("/predict")
    def predict():
        if app.config["CSRF_ENABLED"]:
            expected = session.get("csrf_token")
            supplied = request.form.get("csrf_token")
            if not expected or not supplied or not secrets.compare_digest(expected, supplied):
                abort(400, description="Jeton de formulaire invalide ou expiré.")

        values, errors = validate_form()
        if errors:
            return (
                render_template(
                    "index.html",
                    metadata=metadata,
                    labels=FIELD_LABELS,
                    values={**metadata["defaults"], **values},
                    errors=errors,
                    result=None,
                ),
                400,
            )

        profile = pd.DataFrame([values], columns=metadata["features"])
        score = float(model.predict_proba(profile)[0, 1])
        priority = score >= float(metadata["threshold"])
        result = {
            "score": score,
            "score_percent": f"{score * 100:.1f}".replace(".", ","),
            "threshold_percent": f"{metadata['threshold'] * 100:.1f}".replace(".", ","),
            "priority": priority,
            "label": "À examiner en priorité" if priority else "Priorité standard",
        }
        return render_template(
            "index.html",
            metadata=metadata,
            labels=FIELD_LABELS,
            values=values,
            errors=[],
            result=result,
        )

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            model_version=metadata["model_version"],
            features=len(metadata["features"]),
        )

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("error.html", code=400, message=getattr(error, "description", "Requête invalide.")), 400

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("error.html", code=413, message="La requête dépasse la taille autorisée."), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
