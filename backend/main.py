import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Ajouter le répertoire parent au path pour importer search_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search_engine import MingoSearchEngine

# Configuration de l'application
app = FastAPI(
    title="Mingo Search Engine API",
    description="API pour le moteur de recherche Mingo",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le moteur de recherche
search_engine = MingoSearchEngine()

# Modèles Pydantic
class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    total_results: int
    search_time: float
    stats: dict

class IndexURLRequest(BaseModel):
    url: str

class IndexTextRequest(BaseModel):
    title: str
    content: str
    url: Optional[str] = None

class StatsResponse(BaseModel):
    total_documents: int
    total_words: int
    average_words_per_doc: float
    index_size: int
    last_updated: str

# Routes API
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Servir la page d'accueil"""
    try:
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Mingo Search Engine</title></head>
            <body>
                <h1>🔍 Mingo Search Engine</h1>
                <p>Interface web en cours de chargement...</p>
                <p>API disponible à <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

@app.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Requête de recherche"),
    max_results: int = Query(10, ge=1, le=100, description="Nombre maximum de résultats")
):
    """Effectuer une recherche"""
    import time
    
    start_time = time.time()
    
    if not q.strip():
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")
    
    try:
        results = search_engine.search(q, max_results)
        search_time = time.time() - start_time
        stats = search_engine.get_stats()
        
        return SearchResponse(
            query=q,
            results=results,
            total_results=len(results),
            search_time=round(search_time, 3),
            stats=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")

@app.post("/api/index/url")
async def index_url(request: IndexURLRequest):
    """Indexer une URL"""
    try:
        success = search_engine.add_url(request.url)
        if success:
            return {"message": f"URL {request.url} indexée avec succès", "success": True}
        else:
            raise HTTPException(status_code=400, detail="Impossible d'indexer cette URL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation: {str(e)}")

@app.post("/api/index/text")
async def index_text(request: IndexTextRequest):
    """Indexer un document texte"""
    try:
        search_engine.add_text_document(request.title, request.content, request.url)
        return {"message": "Document texte indexé avec succès", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation: {str(e)}")

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Obtenir les statistiques de l'index"""
    try:
        stats = search_engine.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")

@app.delete("/api/index")
async def clear_index():
    """Vider complètement l'index"""
    try:
        search_engine.clear_index()
        return {"message": "Index vidé avec succès", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@app.get("/api/documents")
async def get_documents(
    limit: int = Query(50, ge=1, le=1000, description="Nombre de documents à retourner"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
):
    """Obtenir la liste des documents indexés"""
    try:
        total = len(search_engine.documents)
        documents = search_engine.documents[offset:offset + limit]
        
        # Retourner seulement les métadonnées, pas le contenu complet
        simplified_docs = []
        for doc in documents:
            simplified_docs.append({
                'id': doc.get('id'),
                'url': doc.get('url'),
                'title': doc.get('title'),
                'description': doc.get('description'),
                'word_count': doc.get('word_count'),
                'indexed_at': doc.get('indexed_at')
            })
        
        return {
            "documents": simplified_docs,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

# Route pour servir les fichiers statiques
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Servir les fichiers statiques"""
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "static", file_path)
    if os.path.exists(static_path):
        return FileResponse(static_path)
    raise HTTPException(status_code=404, detail="Fichier non trouvé")

# Initialisation avec quelques documents exemple
@app.on_event("startup")
async def startup_event():
    """Initialiser l'application avec des données exemple"""
    try:
        # Ajouter quelques documents exemple si l'index est vide
        if len(search_engine.documents) == 0:
            print("🔧 Initialisation avec des documents exemple...")
            
            sample_docs = [
                {
                    "title": "Bienvenue sur Mingo",
                    "content": "Mingo est un moteur de recherche moderne et rapide développé en Python. Il utilise des techniques avancées de recherche textuelle comme TF-IDF et la similarité cosinus pour fournir des résultats pertinents.",
                    "url": "mingo://welcome"
                },
                {
                    "title": "Guide d'utilisation",
                    "content": "Pour utiliser Mingo, saisissez simplement votre requête dans la barre de recherche. Le moteur analysera votre demande et retournera les résultats les plus pertinents triés par score de similarité.",
                    "url": "mingo://guide"
                },
                {
                    "title": "Fonctionnalités avancées",
                    "content": "Mingo supporte l'indexation d'URLs web, de documents texte, et offre une API REST complète. Il peut traiter le français et gérer des requêtes complexes avec des bigrammes.",
                    "url": "mingo://features"
                }
            ]
            
            for doc in sample_docs:
                search_engine.add_text_document(doc["title"], doc["content"], doc["url"])
            
            print(f"✅ {len(sample_docs)} documents exemple ajoutés")
        else:
            print(f"📚 {len(search_engine.documents)} documents déjà indexés")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage du serveur Mingo...")
    print("📍 Interface web: http://localhost:8000")
    print("📚 Documentation API: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )