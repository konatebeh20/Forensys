// Configuration globale
const API_BASE = '/api';
let currentQuery = '';
let currentResults = [];
let isLoading = false;

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Configurer les événements
    setupEventListeners();
    
    // Charger les statistiques initiales
    loadStats();
    
    // Focus sur la barre de recherche
    document.getElementById('search-input').focus();
}

function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    
    // Recherche par Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Recherche par clic
    searchBtn.addEventListener('click', performSearch);
    
    // Fermer le panneau admin avec Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const adminPanel = document.getElementById('admin-panel');
            if (adminPanel.style.display === 'flex') {
                toggleAdmin();
            }
        }
    });
}

// Gestion des recherches
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    
    if (!query) {
        showNotification('Veuillez saisir une requête de recherche', 'warning');
        return;
    }
    
    if (isLoading) return;
    
    currentQuery = query;
    isLoading = true;
    
    showLoading(true);
    hideResults();
    
    try {
        const maxResults = document.getElementById('results-per-page')?.value || 10;
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&max_results=${maxResults}`);
        
        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        currentResults = data.results;
        
        displayResults(data);
        
    } catch (error) {
        console.error('Erreur de recherche:', error);
        showNotification(`Erreur lors de la recherche: ${error.message}`, 'error');
        showNoResults();
    } finally {
        showLoading(false);
        isLoading = false;
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    const resultsList = document.getElementById('results-list');
    const resultsInfo = document.getElementById('results-info');
    const searchTime = document.getElementById('search-time');
    const noResults = document.getElementById('no-results');
    
    // Masquer le message "aucun résultat"
    noResults.style.display = 'none';
    
    if (data.results.length === 0) {
        showNoResults();
        return;
    }
    
    // Afficher les informations de recherche
    resultsInfo.textContent = `${data.total_results} résultat${data.total_results > 1 ? 's' : ''} pour "${data.query}"`;
    searchTime.textContent = `${data.search_time}s`;
    
    // Vider la liste précédente
    resultsList.innerHTML = '';
    
    // Ajouter chaque résultat
    data.results.forEach(result => {
        const resultElement = createResultElement(result);
        resultsList.appendChild(resultElement);
    });
    
    // Afficher le conteneur de résultats
    resultsContainer.style.display = 'block';
    
    // Faire défiler vers les résultats
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

function createResultElement(result) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    const scorePercentage = Math.round(result.score * 100);
    const wordCount = result.word_count || 0;
    const indexedDate = result.indexed_at ? new Date(result.indexed_at).toLocaleDateString('fr-FR') : 'N/A';
    
    resultItem.innerHTML = `
        <a href="${result.url}" class="result-title" target="_blank" rel="noopener">
            ${escapeHtml(result.title)}
        </a>
        <div class="result-url">${escapeHtml(result.url)}</div>
        <div class="result-snippet">${escapeHtml(result.snippet || result.description || '')}</div>
        <div class="result-meta">
            <span class="result-score">Score: ${scorePercentage}%</span>
            <span>Mots: ${wordCount}</span>
            <span>Indexé: ${indexedDate}</span>
            <span>Rang: #${result.rank}</span>
        </div>
    `;
    
    return resultItem;
}

function showNoResults() {
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('no-results').style.display = 'block';
}

function hideResults() {
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('no-results').style.display = 'none';
}

// Gestion du loading
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// Gestion du panneau d'administration
function toggleAdmin() {
    const adminPanel = document.getElementById('admin-panel');
    const isVisible = adminPanel.style.display === 'flex';
    
    adminPanel.style.display = isVisible ? 'none' : 'flex';
    
    if (!isVisible) {
        // Charger les documents quand on ouvre le panneau
        refreshDocuments();
    }
}

function showTab(tabName) {
    // Masquer tous les onglets
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher l'onglet sélectionné
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Gestion de l'indexation
async function indexURL() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();
    
    if (!url) {
        showNotification('Veuillez saisir une URL valide', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/index/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('URL indexée avec succès!', 'success');
            urlInput.value = '';
            loadStats();
            refreshDocuments();
        } else {
            throw new Error(data.detail || 'Erreur lors de l\'indexation');
        }
        
    } catch (error) {
        console.error('Erreur d\'indexation:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function indexText() {
    const title = document.getElementById('doc-title').value.trim();
    const content = document.getElementById('doc-content').value.trim();
    const url = document.getElementById('doc-url').value.trim();
    
    if (!title || !content) {
        showNotification('Veuillez remplir le titre et le contenu', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const requestBody = { title, content };
        if (url) requestBody.url = url;
        
        const response = await fetch(`${API_BASE}/index/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Document indexé avec succès!', 'success');
            document.getElementById('doc-title').value = '';
            document.getElementById('doc-content').value = '';
            document.getElementById('doc-url').value = '';
            loadStats();
            refreshDocuments();
        } else {
            throw new Error(data.detail || 'Erreur lors de l\'indexation');
        }
        
    } catch (error) {
        console.error('Erreur d\'indexation:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Gestion des documents
async function refreshDocuments() {
    const container = document.getElementById('documents-container');
    
    try {
        container.innerHTML = '<div class="loading">Chargement des documents...</div>';
        
        const response = await fetch(`${API_BASE}/documents?limit=50`);
        const data = await response.json();
        
        if (response.ok) {
            displayDocuments(data.documents);
        } else {
            throw new Error('Erreur lors du chargement des documents');
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="error">Erreur lors du chargement des documents</div>';
    }
}

function displayDocuments(documents) {
    const container = document.getElementById('documents-container');
    
    if (documents.length === 0) {
        container.innerHTML = '<div class="loading">Aucun document indexé</div>';
        return;
    }
    
    container.innerHTML = '';
    
    documents.forEach(doc => {
        const docElement = document.createElement('div');
        docElement.className = 'document-item';
        
        const indexedDate = doc.indexed_at ? new Date(doc.indexed_at).toLocaleDateString('fr-FR') : 'N/A';
        
        docElement.innerHTML = `
            <div class="document-title">${escapeHtml(doc.title)}</div>
            <div class="document-meta">
                <span>URL: ${escapeHtml(doc.url)}</span>
                <span>Mots: ${doc.word_count || 0}</span>
                <span>Indexé: ${indexedDate}</span>
            </div>
        `;
        
        container.appendChild(docElement);
    });
}

// Gestion des statistiques
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        if (response.ok) {
            displayStats(stats);
        }
    } catch (error) {
        console.error('Erreur de chargement des stats:', error);
        document.getElementById('stats-info').textContent = 'Stats indisponibles';
    }
}

function displayStats(stats) {
    const statsInfo = document.getElementById('stats-info');
    const totalDocs = stats.total_documents || 0;
    const totalWords = stats.total_words || 0;
    const indexSize = stats.index_size || 0;
    
    statsInfo.textContent = `${totalDocs} documents • ${totalWords.toLocaleString()} mots • Index: ${indexSize} termes`;
}

// Gestion des paramètres
async function clearIndex() {
    if (!confirm('Êtes-vous sûr de vouloir vider complètement l\'index ? Cette action est irréversible.')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/index`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Index vidé avec succès', 'success');
            loadStats();
            refreshDocuments();
            hideResults();
        } else {
            throw new Error(data.detail || 'Erreur lors de la suppression');
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Système de notifications
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    notifications.appendChild(notification);
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
    
    // Permettre la suppression par clic
    notification.addEventListener('click', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}

// Utilitaires
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    return num.toLocaleString('fr-FR');
}

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    showNotification('Une erreur inattendue s\'est produite', 'error');
});

// Gestion des erreurs de requêtes
window.addEventListener('unhandledrejection', function(e) {
    console.error('Promesse rejetée:', e.reason);
    showNotification('Erreur de connexion au serveur', 'error');
});

// Export des fonctions pour les tests (si nécessaire)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        performSearch,
        indexURL,
        indexText,
        loadStats,
        showNotification
    };
}