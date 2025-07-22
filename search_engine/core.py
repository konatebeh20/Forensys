import os
import re
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MingoSearchEngine:
    """
    Moteur de recherche Mingo - Core Engine
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.index_file = os.path.join(data_dir, "index.json")
        self.documents = []
        self.vectorizer = None
        self.tfidf_matrix = None
        
        # Créer le répertoire de données s'il n'existe pas
        os.makedirs(data_dir, exist_ok=True)
        
        # Charger l'index existant
        self.load_index()
        
        # Télécharger les ressources NLTK nécessaires
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def preprocess_text(self, text: str) -> str:
        """Préprocesser le texte pour l'indexation"""
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les caractères spéciaux et garder seulement les lettres et espaces
        text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_content_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extraire le contenu d'une URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraire le titre
            title = soup.find('title')
            title = title.get_text().strip() if title else "Sans titre"
            
            # Extraire la description
            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                description = description.get('content', '')[:200]
            else:
                # Utiliser les premiers mots du contenu
                text = soup.get_text()
                description = ' '.join(text.split()[:30])
            
            # Extraire tout le texte
            content = soup.get_text()
            content = self.preprocess_text(content)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'indexed_at': datetime.now().isoformat(),
                'word_count': len(content.split()) if content else 0
            }
            
        except Exception as e:
            print(f"Erreur lors de l'extraction de {url}: {e}")
            return None
    
    def add_document(self, doc: Dict[str, Any]):
        """Ajouter un document à l'index"""
        # Vérifier si le document existe déjà
        existing_doc = next((d for d in self.documents if d['url'] == doc['url']), None)
        if existing_doc:
            # Mettre à jour le document existant
            existing_doc.update(doc)
        else:
            # Ajouter un nouvel ID
            doc['id'] = len(self.documents)
            self.documents.append(doc)
        
        # Reconstruire l'index TF-IDF
        self.build_index()
        
        # Sauvegarder
        self.save_index()
    
    def add_url(self, url: str) -> bool:
        """Indexer une URL"""
        doc = self.extract_content_from_url(url)
        if doc:
            self.add_document(doc)
            return True
        return False
    
    def add_text_document(self, title: str, content: str, url: str = None):
        """Ajouter un document texte manuel"""
        doc = {
            'url': url or f"doc_{len(self.documents)}",
            'title': title,
            'description': content[:200] if len(content) > 200 else content,
            'content': self.preprocess_text(content),
            'indexed_at': datetime.now().isoformat(),
            'word_count': len(content.split())
        }
        self.add_document(doc)
    
    def build_index(self):
        """Construire l'index TF-IDF"""
        if not self.documents:
            return
        
        # Préparer les textes pour TF-IDF
        texts = []
        for doc in self.documents:
            # Combiner titre et contenu avec poids différents
            text = f"{doc.get('title', '')} {doc.get('title', '')} {doc.get('content', '')}"
            texts.append(text)
        
        # Créer la matrice TF-IDF avec des paramètres adaptés au nombre de documents
        min_docs = min(2, len(texts))
        max_docs = max(1, int(len(texts) * 0.95))
        
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words=None,  # On gère nous-mêmes les mots vides
            ngram_range=(1, 2),  # Unigrammes et bigrammes
            min_df=1,
            max_df=max_docs if max_docs > min_docs else len(texts)
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Effectuer une recherche"""
        if not self.documents or not self.vectorizer:
            return []
        
        # Préprocesser la requête
        processed_query = self.preprocess_text(query)
        if not processed_query:
            return []
        
        # Vectoriser la requête
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculer la similarité cosinus
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Trier par pertinence
        ranked_indices = np.argsort(similarities)[::-1]
        
        results = []
        for i, idx in enumerate(ranked_indices[:max_results]):
            if similarities[idx] > 0:  # Seulement les résultats pertinents
                doc = self.documents[idx].copy()
                doc['score'] = float(similarities[idx])
                doc['rank'] = i + 1
                
                # Extraire un snippet pertinent
                doc['snippet'] = self.extract_snippet(doc['content'], processed_query)
                
                results.append(doc)
        
        return results
    
    def extract_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Extraire un snippet pertinent du contenu"""
        if not content or not query:
            return content[:max_length] if content else ""
        
        # Chercher la première occurrence des mots de la requête
        query_words = query.split()
        content_lower = content.lower()
        
        best_position = 0
        best_score = 0
        
        # Chercher la meilleure position pour le snippet
        for i in range(0, len(content) - max_length, 20):
            snippet = content[i:i + max_length].lower()
            score = sum(1 for word in query_words if word in snippet)
            if score > best_score:
                best_score = score
                best_position = i
        
        snippet = content[best_position:best_position + max_length]
        
        # Assurer que le snippet commence et finit proprement
        if best_position > 0:
            snippet = "..." + snippet
        if best_position + max_length < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de l'index"""
        total_words = sum(doc.get('word_count', 0) for doc in self.documents)
        
        return {
            'total_documents': len(self.documents),
            'total_words': total_words,
            'average_words_per_doc': total_words / len(self.documents) if self.documents else 0,
            'index_size': len(self.vectorizer.vocabulary_) if self.vectorizer else 0,
            'last_updated': max((doc.get('indexed_at', '') for doc in self.documents), default='')
        }
    
    def save_index(self):
        """Sauvegarder l'index sur disque"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def load_index(self):
        """Charger l'index depuis le disque"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                
                # Reconstruire l'index TF-IDF
                if self.documents:
                    self.build_index()
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            self.documents = []
    
    def clear_index(self):
        """Vider complètement l'index"""
        self.documents = []
        self.vectorizer = None
        self.tfidf_matrix = None
        
        if os.path.exists(self.index_file):
            os.remove(self.index_file)