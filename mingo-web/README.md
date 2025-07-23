# 🔍 Mingo - Moteur de Recherche Web

**Version 2.0 - Entièrement en HTML, CSS, JavaScript**

Mingo est un moteur de recherche moderne et intelligent qui fonctionne entièrement côté client. Aucun serveur requis ! Vos données restent privées sur votre appareil.

## ✨ Fonctionnalités

### 🔍 Recherche Avancée
- **Algorithme TF-IDF** pour un scoring précis de pertinence
- **Recherche floue** avec similarité Jaccard pour gérer les fautes de frappe
- **Suggestions automatiques** basées sur le contenu existant
- **Highlighting** des termes de recherche dans les résultats
- **Pagination** et tri des résultats (pertinence, date, titre)

### 🎨 Interface Moderne
- **Design responsive** pour mobile, tablette et desktop
- **Thèmes clair/sombre** avec détection automatique
- **Animations fluides** et transitions élégantes
- **Interface intuitive** avec raccourcis clavier
- **Notifications temps réel** pour toutes les actions

### 🛠️ Gestion de Contenu
- **Ajout rapide** de documents avec catégorisation
- **Extraction simulée** depuis des URLs
- **Import/Export** de données au format JSON
- **Ajout en lot** avec format structuré
- **Gestion complète** des documents indexés

### 🔒 Confidentialité
- **100% côté client** - aucune donnée envoyée sur internet
- **Stockage local** avec localStorage
- **Aucun tracking** ni collecte de données
- **Fonctionne hors ligne** une fois chargé

## 🚀 Démarrage Rapide

### 1. Ouvrir Mingo
Simplement ouvrir le fichier `index.html` dans votre navigateur web moderne.

**Méthodes d'ouverture :**
- Double-cliquer sur `index.html`
- Drag & drop vers votre navigateur
- `Fichier > Ouvrir` dans votre navigateur
- Serveur local : `python -m http.server 8000` puis http://localhost:8000

### 2. Premiers pas
1. **Ajouter du contenu** : Cliquez sur ⚙️ puis "Charger les exemples"
2. **Tester la recherche** : Tapez "Mingo" dans la barre de recherche
3. **Explorer** les fonctionnalités via le panneau d'administration

## 📖 Guide d'Utilisation

### Recherche
- **Recherche simple** : Tapez vos mots-clés et appuyez sur Entrée
- **Suggestions** : Des suggestions apparaissent automatiquement
- **Recherche floue** : Tolère les petites fautes de frappe
- **Actions rapides** : Boutons pour recherches courantes

### Ajout de Contenu

#### Ajout Rapide
1. Cliquez sur l'icône ⚙️ (administration)
2. Onglet "Ajouter du contenu"
3. Remplissez titre, contenu, URL optionnelle et catégorie
4. Cliquez "Ajouter"

#### Extraction d'URL
1. Saisissez une URL dans le champ dédié
2. Cliquez "Extraire" (simulation d'extraction)
3. Prévisualisez le contenu extrait
4. Sauvegardez si satisfait

#### Ajout en Lot
Format : `Titre | Contenu | URL (optionnel)`
```
Guide JavaScript | Tutoriel complet sur JavaScript | https://example.com/js
Python Basics | Introduction à Python | 
Machine Learning | Intelligence artificielle...
```

### Gestion des Documents
- **Voir tous** : Onglet "Documents" dans l'administration
- **Rechercher** : Champ de recherche dans les documents
- **Filtrer** : Par catégorie
- **Sélectionner** : Cases à cocher pour actions groupées
- **Supprimer** : Individuellement ou en lot

### Paramètres
- **Recherche** : Résultats par page, recherche floue, suggestions
- **Interface** : Thème, animations
- **Données** : Sauvegarde automatique

### Import/Export
- **Exporter** : Télécharge toutes vos données en JSON
- **Importer** : Restaure des données depuis un fichier JSON
- **Exemples** : Charge du contenu de démonstration

## ⌨️ Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + K` | Focus sur la recherche |
| `Ctrl + ,` | Ouvrir les paramètres |
| `Échap` | Fermer les modales |
| `Entrée` | Lancer la recherche |

## 🏗️ Architecture Technique

### Structure des Fichiers
```
mingo-web/
├── index.html      # Interface principale
├── style.css       # Styles et thèmes
├── script.js       # Moteur de recherche JS
└── README.md       # Documentation
```

### Technologies Utilisées
- **HTML5** : Structure sémantique moderne
- **CSS3** : Variables CSS, Grid, Flexbox, animations
- **JavaScript ES6+** : Classes, modules, async/await
- **Web APIs** : localStorage, File API, URL API

### Algorithmes Implémentés

#### TF-IDF (Term Frequency-Inverse Document Frequency)
```javascript
score = TF(terme, document) × IDF(terme, collection)
```
- **TF** : Fréquence du terme dans le document
- **IDF** : Rareté du terme dans la collection
- **Score final** : Somme des scores TF-IDF de tous les termes

#### Recherche Floue (Similarité Jaccard)
```javascript
similarité = |A ∩ B| / |A ∪ B|
```
- Calcule la similarité entre deux chaînes
- Seuil configurable (défaut: 80%)
- Gère les variations orthographiques

#### Extraction de Snippets
- Recherche la meilleure position pour l'extrait
- Score basé sur la présence des termes de recherche
- Longueur optimale de 200 caractères

## 🎨 Personnalisation

### Thèmes
Le système de thèmes utilise les variables CSS :

```css
:root {
    --primary: #3b82f6;
    --bg-primary: #ffffff;
    /* ... autres variables */
}

[data-theme="dark"] {
    --bg-primary: #0f172a;
    /* ... surcharges pour thème sombre */
}
```

### Ajout de Catégories
Modifiez la fonction `getCategoryLabel()` dans `script.js` :

```javascript
getCategoryLabel(category) {
    const categories = {
        'article': 'Article',
        'guide': 'Guide',
        'reference': 'Référence',
        'news': 'Actualité',
        'tutorial': 'Tutoriel',  // Nouvelle catégorie
        'other': 'Autre'
    };
    return categories[category] || 'Autre';
}
```

### Personnalisation des Paramètres
Les paramètres par défaut dans `script.js` :

```javascript
this.settings = {
    resultsPerPage: 10,
    fuzzySearch: true,
    autoSuggestions: true,
    theme: 'light',
    animations: true,
    autoSave: true
};
```

## 🔧 Configuration Avancée

### Améliorer l'Extraction d'URLs
Pour une vraie extraction, remplacez la fonction `extractFromURL()` par un appel à une API ou service backend.

### Stockage Alternatif
Remplacez localStorage par IndexedDB pour de gros volumes :

```javascript
// Au lieu de localStorage
localStorage.setItem('mingo_documents', JSON.stringify(documents));

// Utiliser IndexedDB
const db = await openDB('MingoDatabase', 1);
await db.put('documents', documents);
```

### Ajout de Formats de Fichiers
Étendez l'import pour supporter d'autres formats :

```javascript
// Support CSV, XML, etc.
handleFileImport(file) {
    if (file.type === 'text/csv') {
        // Logique CSV
    } else if (file.type === 'application/xml') {
        // Logique XML
    }
    // ... existing JSON logic
}
```

## 🌐 Déploiement

### Hébergement Statique
Mingo peut être hébergé sur :
- **GitHub Pages** : Gratuit, simple
- **Netlify** : Déploiement automatique
- **Vercel** : Optimisé pour les apps web
- **Serveur web** : Apache, Nginx, etc.

### Optimisations
- **Minification** : CSS et JS
- **Compression** : Gzip/Brotli
- **Cache** : Headers appropriés
- **PWA** : Service worker pour offline

## 🔍 Cas d'Usage

### Personnel
- **Base de connaissances** personnelle
- **Recherche dans documents**
- **Organisation de bookmarks**
- **Notes et mémos**

### Professionnel
- **Documentation d'équipe**
- **Base de connaissances produit**
- **Recherche dans FAQ**
- **Archive de contenu**

### Éducatif
- **Recherche dans cours**
- **Base de ressources pédagogiques**
- **Bibliothèque de références**
- **Archive de projets**

## 🚀 Évolutions Possibles

### Fonctionnalités Avancées
- **Recherche par facettes** (auteur, date, type)
- **Recherche géographique** avec cartes
- **Analyse de sentiment** du contenu
- **Clustering automatique** des documents
- **Recommandations** basées sur l'historique

### Intégrations
- **APIs externes** (Wikipedia, Google, etc.)
- **Lecteurs de flux RSS**
- **Synchronisation cloud** (Google Drive, Dropbox)
- **Extensions navigateur**
- **Applications mobiles**

### Performance
- **Web Workers** pour la recherche
- **Indexation incrémentale**
- **Mise en cache intelligente**
- **Lazy loading** des résultats
- **Optimisation mémoire**

## ❓ FAQ

**Q: Mes données sont-elles privées ?**
R: Oui, 100% ! Tout fonctionne dans votre navigateur, rien n'est envoyé sur internet.

**Q: Puis-je utiliser Mingo hors ligne ?**
R: Oui, une fois la page chargée, Mingo fonctionne entièrement hors ligne.

**Q: Y a-t-il une limite au nombre de documents ?**
R: La limite dépend de votre navigateur (quelques MB avec localStorage).

**Q: Puis-je synchroniser entre appareils ?**
R: Utilisez l'export/import JSON pour transférer vos données manuellement.

**Q: La recherche supporte-t-elle les expressions régulières ?**
R: Non actuellement, mais vous pouvez l'ajouter en modifiant le code.

## 🤝 Contribution

Mingo est open source ! Pour contribuer :

1. **Fork** le projet
2. **Créez** une branche feature
3. **Committez** vos changements
4. **Pushez** vers la branche
5. **Ouvrez** une Pull Request

### Idées de Contributions
- Nouvelles langues (internationalisation)
- Thèmes supplémentaires
- Algorithmes de recherche
- Formats d'import/export
- Optimisations performance

## 📄 Licence

MIT License - Libre d'utilisation, modification et distribution.

## 🆘 Support

Pour questions ou problèmes :
- Créez une **Issue** sur GitHub
- Consultez la **documentation**
- Vérifiez les **FAQ** ci-dessus

---

**Créé avec ❤️ pour rendre la recherche accessible à tous**

🔍 **Mingo v2.0** - Moteur de Recherche Web Moderne