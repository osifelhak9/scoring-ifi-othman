# Démonstrateur de scoring IFI responsable

Application Flask locale intégrant le modèle restreint présenté au chapitre 7. Elle utilise sept variables historiques ou comportementales et exclut les variables dérivées du prénom, le sexe et les indicateurs territoriaux sensibles.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\\Scripts\\activate
pip install -r requirements-dev.txt
export IFI_SECRET_KEY="une-cle-locale-longue"
flask --app app run --host 127.0.0.1 --port 5000
```

Ouvrir `http://127.0.0.1:5000`. La route `GET /health` vérifie le chargement du modèle.

## Déploiement public sur Render

Le dépôt contient un fichier `render.yaml` prêt à créer un service web public.
Render installe les dépendances, lance l'application avec Gunicorn et génère une
URL HTTPS en `onrender.com`.

Configuration prévue :

- build : `pip install -r requirements.txt` ;
- démarrage : `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 app:app` ;
- contrôle de santé : `GET /health` ;
- secret Flask généré automatiquement ;
- cookies de session sécurisés en HTTPS.

Les étapes de publication sont détaillées dans `DEPLOIEMENT_PUBLIC.md`.

## Tests

```bash
pytest -q
```

Les tests couvrent l'affichage, la prédiction, la validation des entrées, le jeton CSRF, les en-têtes HTTP, la route de santé et les méthodes autorisées.

## Cadre d'utilisation

- Aucun nom, e-mail, téléphone ou adresse n'est demandé ou enregistré.
- Le score sert à prioriser une revue humaine ; il ne détermine pas l'assujettissement à l'IFI.
- Le modèle et le seuil sont versionnés dans `model/model_metadata.json`.
- Les codes métiers doivent être validés et la dérive mesurée avant un usage réel.
- Le serveur de développement Flask reste réservé à la démonstration locale. La version publique utilise HTTPS et Gunicorn.

## Arborescence

```text
application_ifi/
├── app.py
├── model/
│   ├── modele_responsable_ifi.joblib
│   └── model_metadata.json
├── static/styles.css
├── templates/base.html
├── templates/index.html
├── templates/error.html
├── tests/test_app.py
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```
