#!/usr/bin/env python3
"""
Script de démarrage pour Mingo - Moteur de Recherche
"""

import os
import sys
import subprocess
import signal
import time

def check_dependencies():
    """Vérifier que les dépendances sont installées"""
    try:
        import fastapi
        import uvicorn
        import requests
        import beautifulsoup4
        import nltk
        import sklearn
        import numpy
        import pandas
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installez les dépendances avec: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Installer les dépendances automatiquement"""
    print("📦 Installation des dépendances...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def start_mingo():
    """Démarrer le serveur Mingo"""
    print("🚀 Démarrage de Mingo...")
    print("=" * 50)
    print("🔍 Mingo - Moteur de Recherche")
    print("=" * 50)
    print("📍 Interface web: http://localhost:8000")
    print("📚 Documentation API: http://localhost:8000/docs")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    
    # Changer vers le répertoire backend
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    try:
        # Démarrer le serveur
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de Mingo...")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🔍 Initialisation de Mingo...")
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n🤔 Voulez-vous installer les dépendances automatiquement ? (y/n)")
        response = input().lower().strip()
        
        if response in ['y', 'yes', 'o', 'oui']:
            if not install_dependencies():
                print("❌ Impossible d'installer les dépendances. Installez-les manuellement.")
                return
        else:
            print("📝 Installez les dépendances avec: pip install -r requirements.txt")
            return
    
    # Démarrer Mingo
    start_mingo()

if __name__ == "__main__":
    main()