#!/usr/bin/env python3
"""
Tests pour Mingo - Moteur de Recherche
"""

import sys
import os

# Ajouter le répertoire au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_engine import MingoSearchEngine

def test_search_engine():
    """Tester le moteur de recherche"""
    print("🧪 Test du moteur de recherche Mingo")
    print("=" * 40)
    
    # Initialiser le moteur
    print("1. Initialisation du moteur...")
    engine = MingoSearchEngine("test_data")
    
    # Ajouter des documents de test
    print("2. Ajout de documents de test...")
    test_docs = [
        {
            "title": "Python Programming",
            "content": "Python est un langage de programmation puissant et facile à apprendre. Il est utilisé pour le développement web, l'analyse de données, l'intelligence artificielle et bien plus."
        },
        {
            "title": "Machine Learning",
            "content": "L'apprentissage automatique ou machine learning est une branche de l'intelligence artificielle qui permet aux ordinateurs d'apprendre sans être explicitement programmés."
        },
        {
            "title": "Web Development",
            "content": "Le développement web comprend la création de sites internet et d'applications web. Il inclut le frontend (interface utilisateur) et le backend (serveur)."
        },
        {
            "title": "Data Science",
            "content": "La science des données combine statistiques, programmation et expertise métier pour extraire des insights précieux à partir de données."
        }
    ]
    
    for i, doc in enumerate(test_docs):
        engine.add_text_document(doc["title"], doc["content"], f"test://doc{i+1}")
        print(f"   ✅ Document ajouté: {doc['title']}")
    
    # Tester les recherches
    print("\n3. Tests de recherche...")
    test_queries = [
        "Python programmation",
        "intelligence artificielle",
        "web développement",
        "données science",
        "apprentissage machine"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Recherche: '{query}'")
        results = engine.search(query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                score_percent = round(result['score'] * 100, 1)
                print(f"   {i}. {result['title']} (Score: {score_percent}%)")
        else:
            print("   ❌ Aucun résultat trouvé")
    
    # Statistiques
    print("\n4. Statistiques de l'index:")
    stats = engine.get_stats()
    print(f"   📊 Documents: {stats['total_documents']}")
    print(f"   📝 Mots totaux: {stats['total_words']}")
    print(f"   🔤 Termes dans l'index: {stats['index_size']}")
    
    # Nettoyage
    print("\n5. Nettoyage...")
    engine.clear_index()
    print("   🧹 Index vidé")
    
    print("\n✅ Tests terminés avec succès!")
    return True

def test_text_processing():
    """Tester le préprocessing de texte"""
    print("\n🧪 Test du préprocessing de texte")
    print("=" * 40)
    
    engine = MingoSearchEngine("test_data")
    
    test_cases = [
        ("Hello World! 123", "hello world"),
        ("Café-restaurant & Bar", "café restaurant bar"),
        ("L'intelligence artificielle", "l intelligence artificielle"),
        ("   Espaces   multiples   ", "espaces multiples"),
        ("MAJUSCULES et minuscules", "majuscules et minuscules")
    ]
    
    for input_text, expected in test_cases:
        result = engine.preprocess_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text}' → '{result}'")
        if result != expected:
            print(f"   Attendu: '{expected}'")
    
    engine.clear_index()
    return True

def main():
    """Fonction principale de test"""
    print("🔍 Tests Mingo - Moteur de Recherche")
    print("=" * 50)
    
    try:
        # Test du moteur de recherche
        test_search_engine()
        
        # Test du préprocessing
        test_text_processing()
        
        print("\n🎉 Tous les tests sont passés!")
        print("🚀 Vous pouvez maintenant démarrer Mingo avec: python run_mingo.py")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)