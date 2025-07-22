#!/bin/bash

echo "🔍 Démarrage de Mingo - Moteur de Recherche"
echo "=========================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
if ! python3 -c "import fastapi, uvicorn, requests, beautifulsoup4, nltk, sklearn" 2>/dev/null; then
    echo "⚠️  Installation des dépendances..."
    pip install --break-system-packages -r requirements.txt
fi

# Lancer les tests
echo "🧪 Lancement des tests..."
if python3 test_mingo.py; then
    echo "✅ Tests réussis !"
else
    echo "❌ Tests échoués"
    exit 1
fi

echo ""
echo "🚀 Démarrage du serveur Mingo..."
echo "📍 Interface web: http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo "🛑 Appuyez sur Ctrl+C pour arrêter"
echo ""

# Démarrer le serveur
python3 run_mingo.py