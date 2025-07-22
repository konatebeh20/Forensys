#!/usr/bin/env python3
"""
Script de démonstration pour l'application Forensics & Data Mining
"""

import subprocess
import sys
import os
import time
import webbrowser

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    try:
        import flask, pandas, numpy, sklearn, plotly, openpyxl, sqlalchemy
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

def start_application():
    """Lance l'application Flask"""
    if not check_dependencies():
        print("Veuillez installer les dépendances avec: pip install -r requirements.txt")
        return False
    
    try:
        print("🚀 Lancement de l'application Forensics & Data Mining...")
        print("�� Création des dossiers nécessaires...")
        
        # Créer les dossiers nécessaires
        os.makedirs('app/static/uploads', exist_ok=True)
        
        print("🌐 L'application sera accessible sur: http://localhost:5000")
        print("�� Fichier d'exemple disponible: sample_data.csv")
        print("\n" + "="*50)
        print("COMMENT UTILISER L'APPLICATION:")
        print("="*50)
        print("1. Ouvrez http://localhost:5000 dans votre navigateur")
        print("2. Uploadez le fichier sample_data.csv fourni")
        print("3. Explorez les différents onglets d'analyse")
        print("4. Exportez votre rapport d'analyse")
        print("="*50)
        
        # Lancer l'application
        import app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False

if __name__ == "__main__":
    start_application()
