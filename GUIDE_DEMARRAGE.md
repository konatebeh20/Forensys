# 🚀 Guide de Démarrage Rapide - Forensics & Data Mining

## 📋 Résumé
Cette application web permet d'analyser des bases de données (CSV, Excel, SQLite) pour détecter des anomalies, patterns suspects et effectuer des analyses forensiques avancées.

## ⚡ Démarrage en 3 étapes

### 1. Installation des dépendances
```bash
pip install --break-system-packages flask pandas numpy scikit-learn plotly openpyxl sqlalchemy seaborn matplotlib
```

### 2. Lancement de l'application
```bash
python3 run_demo.py
```
ou
```bash
python3 app.py
```

### 3. Accès à l'interface
Ouvrez votre navigateur sur : **http://localhost:5000**

## 🧪 Test avec les données d'exemple

Un fichier `sample_data.csv` est fourni avec des données suspectes pour tester l'application :

1. **Uploadez** le fichier `sample_data.csv`
2. **Explorez** les différents onglets d'analyse
3. **Découvrez** les anomalies détectées :
   - Tentatives d'injection SQL
   - Adresses IP suspectes
   - Transactions anormales
   - Patterns d'activité suspects

## 🔍 Fonctionnalités Principales

### Vue d'Ensemble
- ✅ Statistiques générales des données
- ✅ Qualité des données et intégrité
- ✅ Analyse des colonnes
- ✅ Métadonnées du fichier (hash MD5/SHA256)

### Analyse Forensique
- 🛡️ Détection d'indicateurs de sécurité
- 🔒 Vérification de l'intégrité des données
- ⚠️ Identification de patterns suspects
- 📅 Timeline des événements

### Détection de Patterns
- 🔢 Patterns séquentiels et mathématiques
- 📝 Patterns textuels (emails, IPs, etc.)
- ⏰ Patterns temporels
- 🔗 Corrélations entre variables

### Détection d'Anomalies
- 📊 Outliers statistiques (IQR, Z-score)
- 🤖 Machine Learning (Isolation Forest, DBSCAN)
- 📈 Anomalies temporelles
- 📝 Anomalies textuelles

### Visualisations
- �� Graphiques interactifs avec Plotly
- 🔥 Heatmaps de corrélation
- 📈 Distributions et histogrammes
- 🕐 Analyses temporelles

## 📂 Formats Supportés

| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | `.csv` | Comma-separated values |
| Excel | `.xlsx`, `.xls` | Fichiers Microsoft Excel |
| SQLite | `.db`, `.sqlite` | Bases de données SQLite |

## 🔧 Structure du Projet

```
forensics-data-mining/
├── app.py                          # Application principale
├── run_demo.py                     # Script de démonstration
├── requirements.txt                # Dépendances
├── sample_data.csv                 # Données d'exemple
├── README.md                       # Documentation complète
├── GUIDE_DEMARRAGE.md             # Ce guide
└── app/
    ├── templates/                  # Templates HTML
    │   ├── base.html
    │   ├── index.html
    │   └── analyze.html
    ├── static/uploads/             # Fichiers uploadés
    ├── core/                       # Modules d'analyse
    │   ├── database_analyzer.py
    │   └── forensic_analyzer.py
    └── analyzers/                  # Détecteurs spécialisés
        ├── pattern_detector.py
        └── anomaly_detector.py
```

## 🚨 Cas d'Usage

### 🏦 Analyse Financière
- Détection de transactions suspectes
- Identification de patterns de fraude
- Anomalies dans les montants

### 🔐 Sécurité Informatique
- Analyse de logs de sécurité
- Détection d'attaques (SQL injection, XSS)
- Identification d'activités malveillantes

### 📊 Audit de Données
- Vérification de l'intégrité des données
- Détection de manipulation
- Contrôle qualité

### 🕵️ Investigation Numérique
- Analyse forensique de bases de données
- Timeline des événements
- Recherche de preuves

## 🔧 Personnalisation

### Ajouter de nouveaux détecteurs
1. Créez un nouveau fichier dans `app/analyzers/`
2. Implémentez votre logique de détection
3. Ajoutez les imports dans `app.py`

### Modifier l'interface
1. Éditez les templates dans `app/templates/`
2. Ajoutez du CSS dans `app/static/css/`
3. Ajoutez du JavaScript dans `app/static/js/`

## 🐛 Dépannage

### L'application ne se lance pas
```bash
# Vérifiez les dépendances
python3 -c "import flask, pandas, numpy; print('OK')"

# Vérifiez les permissions
ls -la app.py

# Lancez avec plus de logs
python3 app.py
```

### Erreur d'import de modules
```bash
# Ajoutez le répertoire au PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 app.py
```

### Port déjà utilisé
```bash
# Changez le port dans app.py
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 📈 Prochaines Étapes

1. **Testez** avec vos propres données
2. **Explorez** les différentes fonctionnalités
3. **Exportez** vos rapports d'analyse
4. **Personnalisez** selon vos besoins

## 🆘 Support

- 📖 Documentation complète : `README.md`
- 🧪 Données de test : `sample_data.csv`
- 🐛 Issues : Créez une issue GitHub
- 💬 Questions : Contactez l'équipe de développement

---

**🎉 Bonne analyse forensique !**
