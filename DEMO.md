# 🔍 Mingo - Moteur de Recherche

**Félicitations !** Votre moteur de recherche Mingo est maintenant opérationnel !

## 🚀 Démarrage Rapide

### 1. Démarrer Mingo
```bash
python3 run_mingo.py
```

### 2. Accéder à l'interface
Ouvrez votre navigateur et allez à : **http://localhost:8000**

## ✨ Fonctionnalités

### 🔍 Recherche Intelligente
- **Recherche textuelle avancée** avec TF-IDF et similarité cosinus
- **Support du français** avec préprocessing intelligent
- **Scoring de pertinence** pour classer les résultats
- **Snippets automatiques** pour prévisualiser le contenu

### 📊 Interface Moderne
- **Design responsive** qui s'adapte à tous les écrans
- **Interface intuitive** avec barre de recherche centrée
- **Panneau d'administration** pour gérer l'index
- **Notifications temps réel** pour les actions

### 🛠️ Administration
- **Indexation d'URLs** pour crawler des sites web
- **Ajout de documents** texte manuellement
- **Gestion des documents** indexés
- **Statistiques en temps réel** de l'index

## 📖 Guide d'Utilisation

### Effectuer une Recherche
1. Tapez votre requête dans la barre de recherche
2. Appuyez sur Entrée ou cliquez sur le bouton 🔍
3. Consultez les résultats triés par pertinence

### Ajouter du Contenu
1. Cliquez sur l'icône ⚙️ en haut à droite
2. Choisissez l'onglet "Indexation"
3. Ajoutez une URL ou un document texte
4. Le contenu sera automatiquement indexé

### Gérer l'Index
- **Voir les documents** : Onglet "Documents"
- **Paramètres** : Onglet "Paramètres"
- **Vider l'index** : Bouton "Vider l'index" (attention !)

## 🔧 API REST

Mingo expose une API REST complète pour intégration :

### Endpoints Principaux

#### Recherche
```bash
GET /api/search?q=python&max_results=10
```

#### Statistiques
```bash
GET /api/stats
```

#### Indexer une URL
```bash
POST /api/index/url
Content-Type: application/json

{
  "url": "https://example.com"
}
```

#### Indexer du texte
```bash
POST /api/index/text
Content-Type: application/json

{
  "title": "Mon Document",
  "content": "Contenu de mon document...",
  "url": "optionnel"
}
```

#### Documentation complète
Visitez : **http://localhost:8000/docs**

## 📂 Structure du Projet

```
mingo/
├── 📁 backend/          # Serveur FastAPI
│   └── main.py          # Point d'entrée de l'API
├── 📁 frontend/         # Interface web
│   ├── index.html       # Page principale
│   └── 📁 static/       # CSS et JavaScript
├── 📁 search_engine/    # Cœur du moteur
│   ├── __init__.py
│   └── core.py          # Logique de recherche
├── 📁 data/             # Index et données (auto-créé)
├── requirements.txt     # Dépendances Python
├── run_mingo.py         # Script de démarrage
└── test_mingo.py        # Tests automatiques
```

## 🧪 Tests

Pour vérifier que tout fonctionne :
```bash
python3 test_mingo.py
```

## 💡 Exemples de Recherches

Une fois Mingo démarré, essayez ces recherches :

- **"Mingo recherche"** - Pour voir les documents d'aide
- **"Python programmation"** - Si vous ajoutez du contenu technique
- **"intelligence artificielle"** - Pour du contenu IA
- **"web développement"** - Pour du contenu web

## 🔐 Sécurité

⚠️ **Important** : Cette version est destinée au développement local.
Pour un déploiement en production :

1. Configurez un reverse proxy (nginx)
2. Ajoutez l'authentification pour l'admin
3. Limitez les accès à l'API
4. Configurez HTTPS

## 🚀 Prochaines Étapes

Voici comment vous pouvez étendre Mingo :

### 🎯 Fonctionnalités Avancées
- **Recherche par facettes** (catégories, dates, types)
- **Recherche floue** pour les fautes de frappe
- **Suggestions automatiques** pendant la saisie
- **Historique des recherches**

### 🔧 Améliorations Techniques
- **Base de données** (PostgreSQL, MongoDB)
- **Cache distribué** (Redis)
- **Indexation asynchrone** avec Celery
- **Clustering** pour la scalabilité

### 🌐 Intégrations
- **Connecteurs** pour CMS (WordPress, Drupal)
- **API externe** (Google, Bing)
- **Formats de fichiers** (PDF, DOCX, etc.)
- **Réseaux sociaux** (Twitter, LinkedIn)

## 📧 Support

Pour toute question ou suggestion :
- Consultez la documentation API : `/docs`
- Vérifiez les logs en cas d'erreur
- Lancez les tests : `python3 test_mingo.py`

---

🎉 **Bravo !** Vous avez créé votre propre moteur de recherche !

Mingo est maintenant prêt à indexer et rechercher tout type de contenu.
Amusez-vous bien à explorer ses fonctionnalités ! 🔍✨