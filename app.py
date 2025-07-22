#!/usr/bin/env python3
"""
Application de Forensics et Data Mining
Analyse de bases de données (SQL, Excel, CSV)
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pandas as pd
import numpy as np
import sqlite3
import os
import io
import base64
import plotly.graph_objs as go
import plotly.express as px
import plotly
import json
from werkzeug.utils import secure_filename
import hashlib
import datetime
import logging
import sys

# Ajouter le répertoire app au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Imports locaux - gestion des erreurs d'import
try:
    from core.database_analyzer import DatabaseAnalyzer
    from core.forensic_analyzer import ForensicAnalyzer
    from analyzers.pattern_detector import PatternDetector
    from analyzers.anomaly_detector import AnomalyDetector
except ImportError as e:
    print(f"Erreur d'import: {e}")
    # Créer des classes de base pour éviter les erreurs
    class DatabaseAnalyzer:
        def __init__(self, filepath): self.filepath = filepath
        def analyze(self): return {"error": "Module non disponible"}
        def generate_visualizations(self): return {}
    
    class ForensicAnalyzer:
        def __init__(self, filepath): self.filepath = filepath
        def full_analysis(self): return {"error": "Module non disponible"}
        def get_file_metadata(self): return {}
    
    class PatternDetector:
        def __init__(self, filepath): self.filepath = filepath
        def detect_patterns(self): return {"error": "Module non disponible"}
    
    class AnomalyDetector:
        def __init__(self, filepath): self.filepath = filepath
        def detect_anomalies(self): return {"error": "Module non disponible"}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forensic_app_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'sql', 'db', 'sqlite'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload et analyse initiale du fichier"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Analyse initiale du fichier
            analyzer = DatabaseAnalyzer(filepath)
            analysis_result = analyzer.analyze()
            
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': analysis_result
            })
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {str(e)}")
            return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500
    
    return jsonify({'error': 'Type de fichier non autorisé'}), 400

@app.route('/analyze/<filename>')
def analyze_file(filename):
    """Page d'analyse détaillée"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('Fichier non trouvé', 'error')
        return redirect(url_for('index'))
    
    return render_template('analyze.html', filename=filename)

@app.route('/api/basic_analysis/<filename>')
def basic_analysis(filename):
    """API pour l'analyse de base"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analyzer = DatabaseAnalyzer(filepath)
        analysis = analyzer.analyze()
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Erreur analyse de base: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/forensic_analysis/<filename>')
def forensic_analysis(filename):
    """API pour l'analyse forensique"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        forensic = ForensicAnalyzer(filepath)
        analysis = forensic.full_analysis()
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Erreur analyse forensique: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pattern_analysis/<filename>')
def pattern_analysis(filename):
    """API pour la détection de patterns"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        detector = PatternDetector(filepath)
        patterns = detector.detect_patterns()
        return jsonify(patterns)
    except Exception as e:
        logger.error(f"Erreur détection patterns: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomaly_detection/<filename>')
def anomaly_detection(filename):
def anomaly_detection(filename):
    """API pour la détection d'anomalies"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        detector = AnomalyDetector(filepath)
        anomalies = detector.detect_anomalies()
        return jsonify(anomalies)
    except Exception as e:
        logger.error(f"Erreur détection anomalies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/<filename>')
def get_visualizations(filename):
    """API pour générer les visualisations"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analyzer = DatabaseAnalyzer(filepath)
        visualizations = analyzer.generate_visualizations()
        return jsonify(visualizations)
    except Exception as e:
        logger.error(f"Erreur génération visualisations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_report/<filename>')
def export_report(filename):
    """Export du rapport d'analyse"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Génération du rapport complet
        analyzer = DatabaseAnalyzer(filepath)
        forensic = ForensicAnalyzer(filepath)
        
        report = {
            'filename': filename,
            'timestamp': datetime.datetime.now().isoformat(),
            'basic_analysis': analyzer.analyze(),
            'forensic_analysis': forensic.full_analysis(),
            'metadata': forensic.get_file_metadata()
        }
        
        # Sauvegarde du rapport
        report_filename = f"report_{filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return send_file(report_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Erreur export rapport: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
