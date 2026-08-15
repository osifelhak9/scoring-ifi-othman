from __future__ import annotations

import os
import random


def _fixed_urandom(n: int) -> bytes:
    return bytes(((i * 73 + 19) % 256) for i in range(n))


os.urandom = _fixed_urandom
random._urandom = _fixed_urandom

from app import create_app


def make_app(**overrides):
    config = {"TESTING": True, "SECRET_KEY": "test-secret", "CSRF_ENABLED": False}
    config.update(overrides)
    return create_app(config)


def valid_payload(app):
    with app.app_context():
        client = app.test_client()
        response = client.get("/")
        assert response.status_code == 200
    metadata = __import__("app").load_artifacts()[1]
    return dict(metadata["defaults"])


def test_home_is_accessible_and_has_no_identity_fields():
    app = make_app()
    response = app.test_client().get("/")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert '<html lang="fr">' in html
    assert "Aller au contenu principal" in html
    assert 'name="email"' not in html.lower()
    assert 'name="telephone"' not in html.lower()
    assert 'name="adresse"' not in html.lower()


def test_health_endpoint_exposes_only_technical_status():
    app = make_app()
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json == {
        "features": 7,
        "model_version": "1.0.0-responsable",
        "status": "ok",
    }


def test_valid_prediction_returns_a_score_and_warning():
    app = make_app()
    response = app.test_client().post("/predict", data=valid_payload(app))
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Score estimé" in html
    assert "contrôle humain" in html.lower()


def test_missing_fields_are_rejected():
    app = make_app()
    response = app.test_client().post("/predict", data={})
    assert response.status_code == 400
    assert "7 erreur(s)" in response.get_data(as_text=True)


def test_unknown_category_is_rejected():
    app = make_app()
    payload = valid_payload(app)
    payload["Reco_don_max"] = "999"
    response = app.test_client().post("/predict", data=payload)
    assert response.status_code == 400
    assert "invalide" in response.get_data(as_text=True)


def test_security_headers_are_present():
    app = make_app()
    response = app.test_client().get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_csrf_is_required_when_enabled():
    app = make_app(CSRF_ENABLED=True)
    client = app.test_client()
    client.get("/")
    response = client.post("/predict", data=valid_payload(app))
    assert response.status_code == 400
    assert "Jeton de formulaire" in response.get_data(as_text=True)


def test_predict_route_does_not_accept_get():
    app = make_app()
    assert app.test_client().get("/predict").status_code == 405
