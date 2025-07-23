// Mingo Search Engine - Version Web JavaScript
// Moteur de recherche complet côté client

class MingoSearchEngine {
    constructor() {
        this.documents = [];
        this.settings = {
            resultsPerPage: 10,
            fuzzySearch: true,
            autoSuggestions: true,
            theme: 'light',
            animations: true,
            autoSave: true
        };
        this.currentPage = 1;
        this.currentQuery = '';
        this.currentResults = [];
        this.extractedContent = null;
        
        // Initialisation
        this.loadData();
        this.loadSettings();
        this.initializeEvents();
        this.initializeKeyboardShortcuts();
        this.updateStats();
        this.checkWelcomeScreen();
        this.applyTheme();
    }

    // === GESTION DES DONNÉES ===
    
    loadData() {
        try {
            const saved = localStorage.getItem('mingo_documents');
            if (saved) {
                this.documents = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Erreur chargement données:', error);
            this.documents = [];
        }
    }

    saveData() {
        if (this.settings.autoSave) {
            try {
                localStorage.setItem('mingo_documents', JSON.stringify(this.documents));
            } catch (error) {
                console.error('Erreur sauvegarde:', error);
                this.showNotification('Erreur lors de la sauvegarde', 'error');
            }
        }
    }

    loadSettings() {
        try {
            const saved = localStorage.getItem('mingo_settings');
            if (saved) {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.error('Erreur chargement paramètres:', error);
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('mingo_settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Erreur sauvegarde paramètres:', error);
        }
    }

    // === MOTEUR DE RECHERCHE ===

    preprocessText(text) {
        if (!text) return '';
        return text.toLowerCase()
                  .normalize('NFD')
                  .replace(/[\u0300-\u036f]/g, '') // Supprime les accents
                  .replace(/[^\w\s]/g, ' ')
                  .replace(/\s+/g, ' ')
                  .trim();
    }

    calculateTfIdf(documents, query) {
        const queryTerms = this.preprocessText(query).split(' ').filter(term => term.length > 0);
        const documentTexts = documents.map(doc => 
            this.preprocessText(`${doc.title} ${doc.title} ${doc.content}`)
        );

        // Calculer TF-IDF pour chaque document
        return documents.map((doc, docIndex) => {
            const docText = documentTexts[docIndex];
            const docTerms = docText.split(' ');
            let score = 0;

            queryTerms.forEach(queryTerm => {
                // Term Frequency (TF)
                const termCount = docTerms.filter(term => 
                    this.settings.fuzzySearch ? 
                    this.fuzzyMatch(term, queryTerm) : 
                    term === queryTerm
                ).length;
                const tf = termCount / docTerms.length;

                if (tf > 0) {
                    // Inverse Document Frequency (IDF)
                    const documentsWithTerm = documentTexts.filter(text => 
                        this.settings.fuzzySearch ?
                        text.split(' ').some(term => this.fuzzyMatch(term, queryTerm)) :
                        text.includes(queryTerm)
                    ).length;
                    const idf = Math.log(documents.length / (documentsWithTerm + 1));

                    // Score TF-IDF
                    score += tf * idf;
                }
            });

            return {
                ...doc,
                score: score,
                snippet: this.extractSnippet(doc.content, query)
            };
        });
    }

    fuzzyMatch(str1, str2, threshold = 0.8) {
        if (str1 === str2) return true;
        if (str1.length < 3 || str2.length < 3) return str1 === str2;
        
        const similarity = this.jaccardSimilarity(str1, str2);
        return similarity >= threshold;
    }

    jaccardSimilarity(str1, str2) {
        const set1 = new Set(str1);
        const set2 = new Set(str2);
        const intersection = new Set([...set1].filter(x => set2.has(x)));
        const union = new Set([...set1, ...set2]);
        return intersection.size / union.size;
    }

    extractSnippet(content, query, maxLength = 200) {
        if (!content || !query) return content ? content.substring(0, maxLength) : '';
        
        const queryTerms = this.preprocessText(query).split(' ');
        const contentLower = this.preprocessText(content);
        
        // Trouve la meilleure position pour le snippet
        let bestPosition = 0;
        let bestScore = 0;
        
        for (let i = 0; i <= content.length - maxLength; i += 20) {
            const snippet = content.substring(i, i + maxLength);
            const snippetLower = this.preprocessText(snippet);
            
            const score = queryTerms.reduce((acc, term) => {
                return acc + (snippetLower.includes(term) ? 1 : 0);
            }, 0);
            
            if (score > bestScore) {
                bestScore = score;
                bestPosition = i;
            }
        }
        
        let snippet = content.substring(bestPosition, bestPosition + maxLength);
        
        if (bestPosition > 0) snippet = '...' + snippet;
        if (bestPosition + maxLength < content.length) snippet = snippet + '...';
        
        return snippet;
    }

    search(query, page = 1) {
        if (!query || !query.trim()) {
            return {
                results: [],
                totalResults: 0,
                totalPages: 0,
                currentPage: page,
                searchTime: 0
            };
        }

        const startTime = performance.now();
        
        // Filtrer les documents et calculer les scores
        const scoredResults = this.calculateTfIdf(this.documents, query)
            .filter(doc => doc.score > 0)
            .sort((a, b) => b.score - a.score)
            .map((doc, index) => ({
                ...doc,
                rank: index + 1,
                scorePercent: Math.round(doc.score * 100)
            }));

        const endTime = performance.now();
        const searchTime = (endTime - startTime) / 1000;

        // Pagination
        const startIndex = (page - 1) * this.settings.resultsPerPage;
        const endIndex = startIndex + this.settings.resultsPerPage;
        const paginatedResults = scoredResults.slice(startIndex, endIndex);

        return {
            results: paginatedResults,
            totalResults: scoredResults.length,
            totalPages: Math.ceil(scoredResults.length / this.settings.resultsPerPage),
            currentPage: page,
            searchTime: searchTime.toFixed(3),
            allResults: scoredResults
        };
    }

    // === GESTION DES DOCUMENTS ===

    addDocument(title, content, url = '', category = '') {
        if (!title.trim() || !content.trim()) {
            throw new Error('Le titre et le contenu sont obligatoires');
        }

        const doc = {
            id: Date.now() + Math.random(),
            title: title.trim(),
            content: content.trim(),
            url: url.trim() || `doc_${this.documents.length + 1}`,
            category: category || 'other',
            dateAdded: new Date().toISOString(),
            wordCount: content.trim().split(/\s+/).length
        };

        this.documents.push(doc);
        this.saveData();
        this.updateStats();
        
        return doc;
    }

    deleteDocument(id) {
        const index = this.documents.findIndex(doc => doc.id === id);
        if (index !== -1) {
            this.documents.splice(index, 1);
            this.saveData();
            this.updateStats();
            return true;
        }
        return false;
    }

    updateDocument(id, updates) {
        const doc = this.documents.find(doc => doc.id === id);
        if (doc) {
            Object.assign(doc, updates);
            if (updates.content) {
                doc.wordCount = updates.content.trim().split(/\s+/).length;
            }
            this.saveData();
            this.updateStats();
            return true;
        }
        return false;
    }

    // === EXTRACTION DE CONTENU WEB ===

    async extractFromURL(url) {
        if (!url || !this.isValidURL(url)) {
            throw new Error('URL invalide');
        }

        try {
            // Pour une vraie application, il faudrait un service backend
            // Ici on simule l'extraction pour la démonstration
            this.showLoading(true, 'Extraction du contenu...');
            
            // Simulation d'extraction
            await this.delay(1500);
            
            const extractedData = {
                title: this.extractTitleFromURL(url),
                content: `Contenu extrait de ${url}. Dans une vraie implémentation, ceci contiendrait le texte extrait de la page web. Le moteur de recherche Mingo permet d'indexer facilement du contenu web pour des recherches rapides et précises.`,
                url: url,
                category: 'article'
            };

            this.extractedContent = extractedData;
            return extractedData;
        } catch (error) {
            throw new Error(`Erreur d'extraction: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    extractTitleFromURL(url) {
        try {
            const domain = new URL(url).hostname;
            return `Page de ${domain}`;
        } catch {
            return 'Page web extraite';
        }
    }

    isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch {
            return false;
        }
    }

    // === INTERFACE UTILISATEUR ===

    initializeEvents() {
        // Recherche
        const searchInput = document.getElementById('search-input');
        const searchBtn = document.getElementById('search-btn');
        const clearBtn = document.getElementById('clear-btn');

        searchInput.addEventListener('input', (e) => {
            const value = e.target.value;
            if (value) {
                clearBtn.style.display = 'flex';
                if (this.settings.autoSuggestions) {
                    this.showSuggestions(value);
                }
            } else {
                clearBtn.style.display = 'none';
                this.hideSuggestions();
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        searchBtn.addEventListener('click', () => this.performSearch());
        clearBtn.addEventListener('click', () => this.clearSearch());

        // Tri des résultats
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.sortResults(e.target.value);
        });

        // Import de fichier
        document.getElementById('import-file').addEventListener('change', (e) => {
            this.handleFileImport(e.target.files[0]);
        });

        // Paramètres
        this.initializeSettingsEvents();
    }

    initializeSettingsEvents() {
        // Paramètres de recherche
        document.getElementById('results-per-page').addEventListener('change', (e) => {
            this.settings.resultsPerPage = parseInt(e.target.value);
            this.saveSettings();
        });

        document.getElementById('fuzzy-search').addEventListener('change', (e) => {
            this.settings.fuzzySearch = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('auto-suggestions').addEventListener('change', (e) => {
            this.settings.autoSuggestions = e.target.checked;
            this.saveSettings();
        });

        // Paramètres d'interface
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.settings.theme = e.target.value;
            this.saveSettings();
            this.applyTheme();
        });

        document.getElementById('animations').addEventListener('change', (e) => {
            this.settings.animations = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('auto-save').addEventListener('change', (e) => {
            this.settings.autoSave = e.target.checked;
            this.saveSettings();
        });

        // Initialiser les valeurs
        document.getElementById('results-per-page').value = this.settings.resultsPerPage;
        document.getElementById('fuzzy-search').checked = this.settings.fuzzySearch;
        document.getElementById('auto-suggestions').checked = this.settings.autoSuggestions;
        document.getElementById('theme-select').value = this.settings.theme;
        document.getElementById('animations').checked = this.settings.animations;
        document.getElementById('auto-save').checked = this.settings.autoSave;
    }

    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+K : Focus recherche
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                document.getElementById('search-input').focus();
            }
            
            // Ctrl+, : Ouvrir paramètres
            if (e.ctrlKey && e.key === ',') {
                e.preventDefault();
                this.toggleAdmin();
                this.showTab('settings');
            }
            
            // Échap : Fermer modales
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    // === RECHERCHE ET AFFICHAGE ===

    performSearch(page = 1) {
        const query = document.getElementById('search-input').value.trim();
        if (!query) {
            this.showNotification('Veuillez saisir une requête', 'warning');
            return;
        }

        this.currentQuery = query;
        this.currentPage = page;

        const searchResult = this.search(query, page);
        this.currentResults = searchResult.allResults;

        this.displayResults(searchResult);
        this.hideWelcomeScreen();
    }

    displayResults(searchResult) {
        const resultsContainer = document.getElementById('results-container');
        const resultsList = document.getElementById('results-list');
        const noResults = document.getElementById('no-results');
        const resultsCount = document.getElementById('results-count');
        const searchTime = document.getElementById('search-time');

        if (searchResult.results.length === 0) {
            resultsContainer.style.display = 'none';
            noResults.style.display = 'block';
            return;
        }

        noResults.style.display = 'none';
        resultsContainer.style.display = 'block';

        // Informations sur la recherche
        resultsCount.textContent = `${searchResult.totalResults} résultat${searchResult.totalResults > 1 ? 's' : ''} pour "${this.currentQuery}"`;
        searchTime.textContent = `${searchResult.searchTime}s`;

        // Afficher les résultats
        resultsList.innerHTML = '';
        searchResult.results.forEach((result, index) => {
            const resultElement = this.createResultElement(result, index);
            resultsList.appendChild(resultElement);
        });

        // Pagination
        this.displayPagination(searchResult);

        // Scroll vers les résultats
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    createResultElement(result, index) {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const categoryText = result.category && result.category !== 'other' ? 
            `<span class="result-category">${this.getCategoryLabel(result.category)}</span>` : '';

        resultItem.innerHTML = `
            <a href="${result.url}" class="result-title" target="_blank" rel="noopener">
                ${this.escapeHtml(result.title)}
            </a>
            <div class="result-url">${this.escapeHtml(result.url)}</div>
            <div class="result-snippet">${this.highlightQuery(this.escapeHtml(result.snippet), this.currentQuery)}</div>
            <div class="result-meta">
                <span class="result-score">Score: ${result.scorePercent}%</span>
                <span>Rang: #${result.rank}</span>
                <span>Mots: ${result.wordCount}</span>
                <span>Ajouté: ${new Date(result.dateAdded).toLocaleDateString('fr-FR')}</span>
                ${categoryText}
            </div>
        `;

        // Animation d'apparition
        if (this.settings.animations) {
            resultItem.style.opacity = '0';
            resultItem.style.transform = 'translateY(20px)';
            setTimeout(() => {
                resultItem.style.transition = 'all 0.3s ease';
                resultItem.style.opacity = '1';
                resultItem.style.transform = 'translateY(0)';
            }, index * 100);
        }

        return resultItem;
    }

    highlightQuery(text, query) {
        if (!query) return text;
        
        const queryTerms = query.split(' ').filter(term => term.length > 0);
        let highlightedText = text;
        
        queryTerms.forEach(term => {
            const regex = new RegExp(`(${this.escapeRegex(term)})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
        });
        
        return highlightedText;
    }

    displayPagination(searchResult) {
        const pagination = document.getElementById('pagination');
        
        if (searchResult.totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // Bouton précédent
        paginationHTML += `
            <button class="page-btn" ${searchResult.currentPage === 1 ? 'disabled' : ''} 
                    onclick="mingoEngine.performSearch(${searchResult.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;
        
        // Numéros de page
        const maxVisiblePages = 5;
        let startPage = Math.max(1, searchResult.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(searchResult.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="page-btn ${i === searchResult.currentPage ? 'active' : ''}" 
                        onclick="mingoEngine.performSearch(${i})">
                    ${i}
                </button>
            `;
        }
        
        // Bouton suivant
        paginationHTML += `
            <button class="page-btn" ${searchResult.currentPage === searchResult.totalPages ? 'disabled' : ''} 
                    onclick="mingoEngine.performSearch(${searchResult.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
        
        pagination.innerHTML = paginationHTML;
    }

    sortResults(sortBy) {
        if (!this.currentResults.length) return;

        let sortedResults = [...this.currentResults];

        switch (sortBy) {
            case 'relevance':
                sortedResults.sort((a, b) => b.score - a.score);
                break;
            case 'date':
                sortedResults.sort((a, b) => new Date(b.dateAdded) - new Date(a.dateAdded));
                break;
            case 'title':
                sortedResults.sort((a, b) => a.title.localeCompare(b.title));
                break;
        }

        // Réafficher avec le nouveau tri
        const startIndex = (this.currentPage - 1) * this.settings.resultsPerPage;
        const endIndex = startIndex + this.settings.resultsPerPage;
        const paginatedResults = sortedResults.slice(startIndex, endIndex);

        const searchResult = {
            results: paginatedResults,
            totalResults: sortedResults.length,
            totalPages: Math.ceil(sortedResults.length / this.settings.resultsPerPage),
            currentPage: this.currentPage,
            searchTime: '0.000'
        };

        this.currentResults = sortedResults;
        this.displayResults(searchResult);
    }

    // === SUGGESTIONS ===

    showSuggestions(query) {
        if (!this.settings.autoSuggestions || query.length < 2) {
            this.hideSuggestions();
            return;
        }

        const suggestions = this.generateSuggestions(query);
        const suggestionsEl = document.getElementById('suggestions');
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        suggestionsEl.innerHTML = '';
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <i class="fas fa-search"></i>
                <span>${this.escapeHtml(suggestion)}</span>
            `;
            item.onclick = () => {
                document.getElementById('search-input').value = suggestion;
                this.hideSuggestions();
                this.performSearch();
            };
            suggestionsEl.appendChild(item);
        });

        suggestionsEl.style.display = 'block';
    }

    generateSuggestions(query) {
        const queryLower = query.toLowerCase();
        const suggestions = new Set();

        // Suggestions basées sur les titres
        this.documents.forEach(doc => {
            const title = doc.title.toLowerCase();
            if (title.includes(queryLower)) {
                suggestions.add(doc.title);
            }
            
            // Suggestions de mots du titre
            const words = doc.title.split(' ');
            words.forEach(word => {
                if (word.toLowerCase().startsWith(queryLower) && word.length > query.length) {
                    suggestions.add(word);
                }
            });
        });

        return Array.from(suggestions).slice(0, 5);
    }

    hideSuggestions() {
        document.getElementById('suggestions').style.display = 'none';
    }

    clearSearch() {
        document.getElementById('search-input').value = '';
        document.getElementById('clear-btn').style.display = 'none';
        this.hideSuggestions();
        this.hideResults();
        this.checkWelcomeScreen();
    }

    hideResults() {
        document.getElementById('results-container').style.display = 'none';
        document.getElementById('no-results').style.display = 'none';
    }

    // === GESTION DES MODALES ET INTERFACE ===

    toggleAdmin() {
        const adminPanel = document.getElementById('admin-panel');
        const isVisible = adminPanel.style.display === 'flex';
        adminPanel.style.display = isVisible ? 'none' : 'flex';
        
        if (!isVisible) {
            this.refreshDocuments();
            this.updateAdminStats();
        }
    }

    showTab(tabName) {
        // Désactiver tous les onglets
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Activer l'onglet sélectionné
        document.getElementById(`${tabName}-tab`).classList.add('active');
        event.target.classList.add('active');
    }

    closeAllModals() {
        document.getElementById('admin-panel').style.display = 'none';
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    toggleTheme() {
        const currentTheme = this.settings.theme;
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.settings.theme = newTheme;
        this.saveSettings();
        this.applyTheme();
    }

    applyTheme() {
        const theme = this.settings.theme === 'auto' ? 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') :
            this.settings.theme;
        
        document.documentElement.setAttribute('data-theme', theme);
        
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    checkWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcome-screen');
        const hasDocuments = this.documents.length > 0;
        const hasQuery = document.getElementById('search-input').value.trim().length > 0;
        
        welcomeScreen.style.display = (!hasDocuments && !hasQuery) ? 'block' : 'none';
    }

    hideWelcomeScreen() {
        document.getElementById('welcome-screen').style.display = 'none';
    }

    updateStats() {
        const docCount = this.documents.length;
        const wordCount = this.documents.reduce((sum, doc) => sum + (doc.wordCount || 0), 0);
        
        document.getElementById('doc-count').textContent = docCount;
        document.getElementById('word-count').textContent = wordCount.toLocaleString();
    }

    updateAdminStats() {
        document.getElementById('admin-doc-count').textContent = this.documents.length;
    }

    // === GESTION DES DOCUMENTS (ADMIN) ===

    refreshDocuments() {
        const container = document.getElementById('documents-list');
        container.innerHTML = '';
        
        if (this.documents.length === 0) {
            container.innerHTML = '<div class="loading">Aucun document indexé</div>';
            return;
        }

        this.documents.forEach(doc => {
            const docElement = this.createDocumentElement(doc);
            container.appendChild(docElement);
        });
    }

    createDocumentElement(doc) {
        const docItem = document.createElement('div');
        docItem.className = 'document-item';
        
        const categoryLabel = this.getCategoryLabel(doc.category);
        const dateAdded = new Date(doc.dateAdded).toLocaleDateString('fr-FR');
        
        docItem.innerHTML = `
            <input type="checkbox" class="document-checkbox" data-id="${doc.id}">
            <div class="document-info">
                <div class="document-title">${this.escapeHtml(doc.title)}</div>
                <div class="document-meta">
                    <span>URL: ${this.escapeHtml(doc.url)}</span>
                    <span>Catégorie: ${categoryLabel}</span>
                    <span>Mots: ${doc.wordCount}</span>
                    <span>Ajouté: ${dateAdded}</span>
                </div>
            </div>
            <div class="document-actions">
                <button class="btn-small" onclick="mingoEngine.editDocument('${doc.id}')" title="Éditer">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-small btn-danger" onclick="mingoEngine.confirmDeleteDocument('${doc.id}')" title="Supprimer">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        return docItem;
    }

    getCategoryLabel(category) {
        const categories = {
            'article': 'Article',
            'guide': 'Guide',
            'reference': 'Référence',
            'news': 'Actualité',
            'other': 'Autre'
        };
        return categories[category] || 'Autre';
    }

    // === ACTIONS D'ADMINISTRATION ===

    addQuickDocument() {
        const title = document.getElementById('quick-title').value.trim();
        const content = document.getElementById('quick-content').value.trim();
        const url = document.getElementById('quick-url').value.trim();
        const category = document.getElementById('quick-category').value;

        if (!title || !content) {
            this.showNotification('Le titre et le contenu sont obligatoires', 'warning');
            return;
        }

        try {
            this.addDocument(title, content, url, category);
            
            // Réinitialiser le formulaire
            document.getElementById('quick-title').value = '';
            document.getElementById('quick-content').value = '';
            document.getElementById('quick-url').value = '';
            document.getElementById('quick-category').value = '';
            
            this.showNotification('Document ajouté avec succès!', 'success');
            this.refreshDocuments();
            this.updateAdminStats();
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async extractFromURL() {
        const url = document.getElementById('url-input').value.trim();
        
        if (!url) {
            this.showNotification('Veuillez saisir une URL', 'warning');
            return;
        }

        try {
            const extracted = await this.extractFromURL(url);
            this.showExtractedContent(extracted);
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    showExtractedContent(content) {
        const preview = document.getElementById('crawler-preview');
        const contentDiv = document.getElementById('extracted-content');
        
        contentDiv.innerHTML = `
            <div class="form-section">
                <h4>Titre: ${this.escapeHtml(content.title)}</h4>
                <p><strong>URL:</strong> ${this.escapeHtml(content.url)}</p>
                <p><strong>Aperçu du contenu:</strong></p>
                <div style="max-height: 150px; overflow-y: auto; background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius); margin-top: 0.5rem;">
                    ${this.escapeHtml(content.content.substring(0, 500))}${content.content.length > 500 ? '...' : ''}
                </div>
            </div>
        `;
        
        preview.style.display = 'block';
    }

    saveExtractedContent() {
        if (!this.extractedContent) {
            this.showNotification('Aucun contenu à sauvegarder', 'warning');
            return;
        }

        try {
            this.addDocument(
                this.extractedContent.title,
                this.extractedContent.content,
                this.extractedContent.url,
                this.extractedContent.category
            );
            
            this.showNotification('Contenu extrait sauvegardé!', 'success');
            document.getElementById('url-input').value = '';
            document.getElementById('crawler-preview').style.display = 'none';
            this.extractedContent = null;
            this.refreshDocuments();
            this.updateAdminStats();
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    addBatchDocuments() {
        const batchContent = document.getElementById('batch-content').value.trim();
        
        if (!batchContent) {
            this.showNotification('Veuillez saisir du contenu', 'warning');
            return;
        }

        const lines = batchContent.split('\n').filter(line => line.trim());
        let successCount = 0;
        let errorCount = 0;

        lines.forEach((line, index) => {
            const parts = line.split('|').map(part => part.trim());
            
            if (parts.length >= 2) {
                try {
                    const title = parts[0];
                    const content = parts[1];
                    const url = parts[2] || `batch_doc_${index + 1}`;
                    
                    this.addDocument(title, content, url, 'other');
                    successCount++;
                } catch (error) {
                    errorCount++;
                }
            } else {
                errorCount++;
            }
        });

        document.getElementById('batch-content').value = '';
        
        if (successCount > 0) {
            this.showNotification(`${successCount} document(s) ajouté(s) avec succès`, 'success');
            this.refreshDocuments();
            this.updateAdminStats();
        }
        
        if (errorCount > 0) {
            this.showNotification(`${errorCount} ligne(s) ignorée(s) (format invalide)`, 'warning');
        }
    }

    confirmDeleteDocument(id) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
            this.deleteDocument(id);
            this.showNotification('Document supprimé', 'success');
            this.refreshDocuments();
            this.updateAdminStats();
        }
    }

    selectAllDocuments() {
        const checkboxes = document.querySelectorAll('.document-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(cb => {
            cb.checked = !allChecked;
        });
    }

    deleteSelectedDocuments() {
        const checkedBoxes = document.querySelectorAll('.document-checkbox:checked');
        
        if (checkedBoxes.length === 0) {
            this.showNotification('Aucun document sélectionné', 'warning');
            return;
        }

        if (!confirm(`Supprimer ${checkedBoxes.length} document(s) sélectionné(s) ?`)) {
            return;
        }

        checkedBoxes.forEach(checkbox => {
            this.deleteDocument(checkbox.dataset.id);
        });

        this.showNotification(`${checkedBoxes.length} document(s) supprimé(s)`, 'success');
        this.refreshDocuments();
        this.updateAdminStats();
    }

    clearAllData() {
        if (!confirm('Êtes-vous sûr de vouloir supprimer TOUTES les données ? Cette action est irréversible.')) {
            return;
        }

        this.documents = [];
        this.saveData();
        this.updateStats();
        this.updateAdminStats();
        this.refreshDocuments();
        this.hideResults();
        this.checkWelcomeScreen();
        
        this.showNotification('Toutes les données ont été supprimées', 'success');
    }

    // === IMPORT/EXPORT ===

    exportData() {
        const data = {
            documents: this.documents,
            settings: this.settings,
            exportDate: new Date().toISOString(),
            version: '2.0'
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `mingo_backup_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Données exportées avec succès', 'success');
    }

    handleFileImport(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                this.importData(data);
            } catch (error) {
                this.showNotification('Fichier JSON invalide', 'error');
            }
        };
        reader.readAsText(file);
    }

    importData(data) {
        if (!data.documents || !Array.isArray(data.documents)) {
            this.showNotification('Format de données invalide', 'error');
            return;
        }

        const confirmMessage = `Importer ${data.documents.length} document(s) ? Les données existantes seront remplacées.`;
        if (!confirm(confirmMessage)) return;

        this.documents = data.documents;
        if (data.settings) {
            this.settings = { ...this.settings, ...data.settings };
        }

        this.saveData();
        this.saveSettings();
        this.updateStats();
        this.updateAdminStats();
        this.refreshDocuments();
        this.checkWelcomeScreen();
        
        this.showNotification(`${data.documents.length} document(s) importé(s)`, 'success');
    }

    loadSampleData() {
        const sampleDocuments = [
            {
                id: Date.now() + 1,
                title: "Bienvenue sur Mingo",
                content: "Mingo est un moteur de recherche moderne et intelligent développé en JavaScript. Il fonctionne entièrement côté client, garantissant la confidentialité de vos données. Avec des fonctionnalités avancées comme la recherche floue, le scoring TF-IDF et une interface utilisateur intuitive, Mingo rend la recherche de contenu rapide et précise.",
                url: "mingo://welcome",
                category: "guide",
                dateAdded: new Date().toISOString(),
                wordCount: 52
            },
            {
                id: Date.now() + 2,
                title: "Guide d'utilisation",
                content: "Pour utiliser Mingo efficacement, commencez par ajouter du contenu via le panneau d'administration. Vous pouvez indexer des documents texte manuellement ou extraire du contenu depuis des URLs. Une fois vos documents indexés, utilisez la barre de recherche pour trouver rapidement l'information que vous cherchez. Mingo supporte la recherche floue pour gérer les fautes de frappe et offre des suggestions automatiques.",
                url: "mingo://guide",
                category: "guide",
                dateAdded: new Date().toISOString(),
                wordCount: 78
            },
            {
                id: Date.now() + 3,
                title: "Fonctionnalités avancées",
                content: "Mingo offre de nombreuses fonctionnalités avancées : recherche TF-IDF pour un scoring précis, recherche floue avec algorithme de similarité Jaccard, suggestions automatiques basées sur le contenu existant, support de multiples catégories de documents, thèmes clair et sombre, interface responsive pour mobile et desktop, import/export de données au format JSON, et bien plus encore.",
                url: "mingo://features",
                category: "reference",
                dateAdded: new Date().toISOString(),
                wordCount: 65
            },
            {
                id: Date.now() + 4,
                title: "Algorithmes de recherche",
                content: "Le moteur de Mingo utilise l'algorithme TF-IDF (Term Frequency-Inverse Document Frequency) pour calculer la pertinence des documents. Cet algorithme considère à la fois la fréquence d'un terme dans un document (TF) et sa rareté dans l'ensemble de la collection (IDF). Plus un terme est fréquent dans un document spécifique et rare dans la collection globale, plus son score de pertinence est élevé.",
                url: "mingo://algorithm",
                category: "reference",
                dateAdded: new Date().toISOString(),
                wordCount: 71
            },
            {
                id: Date.now() + 5,
                title: "Conseils d'optimisation",
                content: "Pour optimiser vos recherches avec Mingo, utilisez des mots-clés spécifiques plutôt que des termes génériques. Profitez de la recherche floue pour gérer les variations orthographiques. Organisez vos documents en catégories pour faciliter le filtrage. Utilisez des titres descriptifs pour vos documents car ils ont un poids plus important dans le calcul de pertinence. N'hésitez pas à utiliser les suggestions automatiques pour découvrir du contenu connexe.",
                url: "mingo://tips",
                category: "guide",
                dateAdded: new Date().toISOString(),
                wordCount: 84
            }
        ];

        this.documents = sampleDocuments;
        this.saveData();
        this.updateStats();
        this.updateAdminStats();
        this.refreshDocuments();
        this.checkWelcomeScreen();
        
        this.showNotification(`${sampleDocuments.length} documents d'exemple chargés`, 'success');
    }

    exportResults() {
        if (!this.currentResults.length) {
            this.showNotification('Aucun résultat à exporter', 'warning');
            return;
        }

        const exportData = {
            query: this.currentQuery,
            searchDate: new Date().toISOString(),
            totalResults: this.currentResults.length,
            results: this.currentResults.map(result => ({
                title: result.title,
                url: result.url,
                snippet: result.snippet,
                score: result.score,
                rank: result.rank,
                category: result.category
            }))
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `mingo_search_${this.currentQuery.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Résultats exportés', 'success');
    }

    // === ACTIONS RAPIDES ===

    performQuickSearch(query) {
        document.getElementById('search-input').value = query;
        this.performSearch();
    }

    showAllDocuments() {
        if (this.documents.length === 0) {
            this.showNotification('Aucun document à afficher', 'warning');
            return;
        }

        // Recherche avec une requête vide pour afficher tous les documents
        document.getElementById('search-input').value = '*';
        
        const allResults = this.documents.map((doc, index) => ({
            ...doc,
            score: 1,
            rank: index + 1,
            scorePercent: 100,
            snippet: doc.content.substring(0, 200) + (doc.content.length > 200 ? '...' : '')
        }));

        const searchResult = {
            results: allResults.slice(0, this.settings.resultsPerPage),
            totalResults: allResults.length,
            totalPages: Math.ceil(allResults.length / this.settings.resultsPerPage),
            currentPage: 1,
            searchTime: '0.001',
            allResults: allResults
        };

        this.currentQuery = 'Tous les documents';
        this.currentResults = allResults;
        this.currentPage = 1;
        
        this.displayResults(searchResult);
        this.hideWelcomeScreen();
    }

    // === UTILITAIRES ===

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    showLoading(show, text = 'Chargement...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        if (loadingText) {
            loadingText.textContent = text;
        }
        
        overlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
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

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// === FONCTIONS GLOBALES POUR LES ÉVÉNEMENTS HTML ===

function toggleAdmin() {
    mingoEngine.toggleAdmin();
}

function showTab(tabName) {
    mingoEngine.showTab(tabName);
}

function toggleTheme() {
    mingoEngine.toggleTheme();
}

function addQuickDocument() {
    mingoEngine.addQuickDocument();
}

function extractFromURL() {
    mingoEngine.extractFromURL();
}

function saveExtractedContent() {
    mingoEngine.saveExtractedContent();
}

function addBatchDocuments() {
    mingoEngine.addBatchDocuments();
}

function refreshDocuments() {
    mingoEngine.refreshDocuments();
}

function selectAllDocuments() {
    mingoEngine.selectAllDocuments();
}

function deleteSelectedDocuments() {
    mingoEngine.deleteSelectedDocuments();
}

function clearAllData() {
    mingoEngine.clearAllData();
}

function exportData() {
    mingoEngine.exportData();
}

function loadSampleData() {
    mingoEngine.loadSampleData();
}

function exportResults() {
    mingoEngine.exportResults();
}

function performQuickSearch(query) {
    mingoEngine.performQuickSearch(query);
}

function showAllDocuments() {
    mingoEngine.showAllDocuments();
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// === INITIALISATION ===

// Initialiser Mingo quand le DOM est chargé
let mingoEngine;

document.addEventListener('DOMContentLoaded', function() {
    mingoEngine = new MingoSearchEngine();
    
    // Détection du thème système
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (mingoEngine.settings.theme === 'auto') {
                mingoEngine.applyTheme();
            }
        });
    }
    
    console.log('🔍 Mingo Search Engine v2.0 initialisé');
});