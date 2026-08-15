# Blocs et captures à insérer dans le chapitre 8

Le mémoire contient uniquement des extraits courts. Le fichier `app.py` et les tests complets restent dans le ZIP technique.

## Page 47 — CODE 8.1-A : intégration du modèle dans le back Flask

```python
model = joblib.load(MODEL_PATH)
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

@app.post("/predict")
def predict():
    values, errors = validate_form()
    profile = pd.DataFrame([values], columns=metadata["features"])
    score = float(model.predict_proba(profile)[0, 1])
    priority = score >= float(metadata["threshold"])
    return render_template("index.html", result={"score": score,
                           "priority": priority}, **page_context)
```

Légende : **Extrait 8.1 — Chargement du pipeline versionné et calcul d’un score dans la route back-end.**

## Page 48 — captures de l’interface

1. Lancer l’application puis ouvrir `http://127.0.0.1:5000`.
2. Capturer la page d’accueil en montrant le titre, l’avertissement et le formulaire : **Capture 8.1-A**.
3. Pour obtenir un résultat « À examiner en priorité », utiliser ce profil de démonstration :

| Champ | Code |
|---|---:|
| TypeHabi | 03 |
| Ancienneté | 10 |
| Reco_PA | 02 |
| Reco_Année_1er_don | 01 |
| Reco_cumul_dons | 09 |
| Reco_don_max | 06 |
| Reco_don_moy | 05 |

Le score attendu avec la version 1.0.0-responsable est d’environ **86,2 %**. Capturer le résultat et l’avertissement de contrôle humain : **Capture 8.1-B**.

## Page 49 — CODE 8.2-A : test d’intégration

```python
def test_valid_prediction_returns_a_score_and_warning():
    app = make_app()
    response = app.test_client().post("/predict", data=valid_payload(app))
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Score estimé" in html
    assert "contrôle humain" in html.lower()
```

Lancer `pytest -q`. Capturer le terminal avec le résultat **8 passed** : **Capture 8.2-A**.

## Page 50 — CODE 8.2-B : en-têtes de sécurité

```python
@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response
```

Dans les outils de développement du navigateur, onglet **Network**, ouvrir la requête `/` puis capturer les en-têtes de réponse : **Capture 8.2-B**.

## Contrôle d’accessibilité à montrer

- Naviguer au clavier avec `Tab`, sans utiliser la souris ; vérifier que le focus jaune reste visible.
- Utiliser Lighthouse ou Accessibility Insights sur la page d’accueil.
- Ne reporter dans le mémoire que le score réellement obtenu.
- Capturer le rapport et consigner la date, le navigateur et la version de l’outil : **Capture 8.2-C**.
