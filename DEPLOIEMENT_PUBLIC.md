# Mise en ligne de l'application IFI

## 1. Déposer ce dossier dans un dépôt Git

Créer un dépôt privé ou public, puis y placer directement le contenu de ce
dossier. Le fichier `render.yaml` doit se trouver à la racine du dépôt.

Ne jamais ajouter un fichier `.env` contenant de véritables secrets.

## 2. Créer le service Render

1. Créer ou ouvrir un compte Render.
2. Connecter le dépôt Git contenant l'application.
3. Choisir **New > Blueprint**.
4. Sélectionner le dépôt et confirmer le fichier `render.yaml`.
5. Lancer le déploiement et attendre que le statut devienne **Live**.

Le service utilise automatiquement :

- Python 3.12.10 ;
- `pip install -r requirements.txt` pour la construction ;
- Gunicorn pour le serveur public ;
- `/health` pour le contrôle de disponibilité ;
- une clé Flask aléatoire générée par Render.

## 3. Vérifier l'application

Ouvrir l'URL `https://scoring-ifi-othman.onrender.com` ou l'adresse équivalente
attribuée par Render. Si le nom est déjà utilisé, Render fournit une variante.

Effectuer les contrôles suivants :

1. La page d'accueil s'affiche.
2. Un profil de démonstration peut être évalué.
3. L'adresse `/health` renvoie `status: ok`.
4. L'URL fonctionne depuis un autre appareil ou en navigation privée.

## 4. Compléter le livrable du jury

Après validation, copier l'URL réelle :

- en haut du `README.md` du ZIP final ;
- dans un fichier `URL_PUBLIQUE.txt` ;
- dans la partie déploiement du mémoire et du support de soutenance.

Conserver également l'exécution locale `http://127.0.0.1:5000` comme solution
de secours pour la soutenance.

## Limite du service gratuit

Une instance gratuite peut s'arrêter après une période d'inactivité. Ouvrir le
lien quelques minutes avant la soutenance afin que l'application soit réveillée.
