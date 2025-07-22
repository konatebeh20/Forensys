# Application de Forensics et Data Mining

## Description

Cette application web permet d'effectuer des analyses forensiques et de data mining sur des bases de données (CSV, Excel, SQLite). Elle offre des fonctionnalités avancées pour détecter des anomalies, identifier des patterns suspects et générer des rapports d'analyse complets.

## Fonctionnalités

### 🔍 Analyse de Base
- **Statistiques descriptives** : Analyse complète des données avec métriques de qualité
- **Analyse des colonnes** : Type de données, valeurs manquantes, unicité
- **Visualisations automatiques** : Graphiques et diagrammes interactifs
- **Intégrité des données** : Détection de doublons et incohérences

### 🛡️ Analyse Forensique
- **Métadonnées de fichiers** : Hash MD5/SHA256, timestamps, permissions
- **Détection d'indicateurs de sécurité** : Mots-clés suspects, adresses IP
- **Analyse de l'intégrité** : Vérification de manipulation de données
- **Timeline forensique** : Chronologie des événements

### 🧠 Détection de Patterns
- **Patterns séquentiels** : Suites arithmétiques et géométriques
- **Patterns répétitifs** : Valeurs anormalement fréquentes
- **Patterns textuels** : Expressions régulières, formats de données
- **Patterns temporels** : Analyse des timestamps et intervalles
- **Corrélations** : Détection de relations entre variables

### ⚠️ Détection d'Anomalies
- **Outliers statistiques** : Méthodes IQR, Z-score, Z-score modifié
- **Isolation Forest** : Détection d'anomalies par machine learning
- **Clustering DBSCAN** : Identification de points aberrants
- **Anomalies temporelles** : Gaps et bursts d'activité
- **Anomalies textuelles** : Problèmes d'encodage, caractères suspects

## Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd forensics-data-mining
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Lancer l'application**
```bash
python app.py
```

4. **Accéder à l'application**
Ouvrez votre navigateur et allez sur : `http://localhost:5000`

## Utilisation

### 1. Upload de fichier
- Glissez-déposez votre fichier sur la zone d'upload
- Ou cliquez pour sélectionner un fichier
- Formats supportés : CSV, Excel (.xlsx, .xls), SQLite (.db, .sqlite)

### 2. Analyse automatique
L'application lance automatiquement une analyse de base du fichier uploadé.

### 3. Exploration des résultats
Naviguez entre les différents onglets :
- **Vue d'ensemble** : Statistiques générales et qualité des données
- **Analyse Forensique** : Indicateurs de sécurité et intégrité
- **Détection de Patterns** : Motifs récurrents et suspects
- **Anomalies** : Points aberrants et incohérences
- **Visualisations** : Graphiques et diagrammes interactifs

### 4. Export du rapport
Cliquez sur "Exporter le rapport" pour télécharger un rapport JSON complet.

## Structure du Projet

```
forensics-data-mining/
├── app.py                          # Application Flask principale
├── requirements.txt                # Dépendances Python
├── README.md                      # Documentation
├── app/
│   ├── __init__.py
│   ├── static/
│   │   ├── css/                   # Styles CSS
│   │   ├── js/                    # Scripts JavaScript
│   │   └── uploads/               # Fichiers uploadés
│   ├── templates/
│   │   ├── base.html              # Template de base
│   │   ├── index.html             # Page d'accueil
│   │   └── analyze.html           # Page d'analyse
│   ├── core/
│   │   ├── database_analyzer.py   # Analyseur de base
│   │   └── forensic_analyzer.py   # Analyseur forensique
│   └── analyzers/
│       ├── pattern_detector.py    # Détecteur de patterns
│       └── anomaly_detector.py    # Détecteur d'anomalies
```

## API Endpoints

### Upload et Analyse
- `POST /upload` : Upload et analyse initiale d'un fichier
- `GET /analyze/<filename>` : Page d'analyse détaillée

### APIs d'Analyse
- `GET /api/basic_analysis/<filename>` : Analyse de base
- `GET /api/forensic_analysis/<filename>` : Analyse forensique
- `GET /api/pattern_analysis/<filename>` : Détection de patterns
- `GET /api/anomaly_detection/<filename>` : Détection d'anomalies
- `GET /api/visualizations/<filename>` : Génération de visualisations
- `GET /api/export_report/<filename>` : Export du rapport complet

## Dépendances Principales

- **Flask** : Framework web
- **Pandas** : Manipulation de données
- **NumPy** : Calculs numériques
- **Scikit-learn** : Algorithmes de machine learning
- **Plotly** : Visualisations interactives
- **SQLAlchemy** : ORM pour bases de données
- **OpenPyXL** : Lecture de fichiers Excel

## Exemples d'Utilisation

### Analyse d'un fichier CSV de logs
```python
# L'application détectera automatiquement :
# - Patterns temporels suspects
# - Adresses IP anormales
# - Activité utilisateur inhabituelle
# - Anomalies dans les timestamps
```

### Analyse d'une base de données financière
```python
# Détection de :
# - Transactions suspectes (montants arrondis)
# - Patterns de fraude
# - Anomalies dans les montants
# - Corrélations inhabituelles
```

### Analyse de données utilisateur
```python
# Identification de :
# - Comptes suspects
# - Patterns d'accès anormaux
# - Données personnelles exposées
# - Activité automatisée
```

## Sécurité

- **Validation des fichiers** : Vérification des extensions et types MIME
- **Isolation des uploads** : Fichiers stockés dans un dossier sécurisé
- **Hachage des fichiers** : Calcul MD5/SHA256 pour l'intégrité
- **Logs d'activité** : Enregistrement des actions importantes

## Performance

- **Streaming des gros fichiers** : Traitement par chunks
- **Cache des analyses** : Évite la re-calcul
- **Optimisation mémoire** : Gestion efficace des DataFrames
- **Visualisations optimisées** : Échantillonnage pour les gros datasets

## Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Support

Pour le support et les questions, ouvrez une issue sur GitHub ou contactez l'équipe de développement.

## Roadmap

### Version Future
- [ ] Support pour PostgreSQL et MySQL
- [ ] Analyse de fichiers logs (Apache, Nginx)
- [ ] Détection de malware dans les données
- [ ] Interface de reporting avancée
- [ ] API REST complète
- [ ] Intégration avec des outils SIEM
- [ ] Analyse en temps réel
- [ ] Support multi-utilisateurs
