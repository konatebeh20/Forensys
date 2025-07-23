"""
Analyseur de bases de données
Gère l'analyse de fichiers CSV, Excel et SQL
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import hashlib
import plotly.express as px
import plotly.graph_objs as go
import plotly
import json
from sqlalchemy import create_engine
import logging

class DatabaseAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.file_extension = self.filename.split('.')[-1].lower()
        self.data = None
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """Charge les données selon le type de fichier"""
        try:
            if self.file_extension in ['csv']:
                # Tentative de détection de l'encodage et du séparateur
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                separators = [',', ';', '\t', '|']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            self.data = pd.read_csv(self.filepath, encoding=encoding, sep=sep)
                            if len(self.data.columns) > 1:  # Si plus d'une colonne, c'est probablement bon
                                break
                        except:
                            continue
                    if self.data is not None and len(self.data.columns) > 1:
                        break
                        
            elif self.file_extension in ['xlsx', 'xls']:
                self.data = pd.read_excel(self.filepath)
                
            elif self.file_extension in ['db', 'sqlite', 'sql']:
                conn = sqlite3.connect(self.filepath)
                # Obtenir la liste des tables
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                if not tables.empty:
                    # Charger la première table ou la plus grande
                    table_name = tables['name'].iloc[0]
                    self.data = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
                conn.close()
                
            if self.data is None or self.data.empty:
                raise ValueError("Impossible de charger les données du fichier")
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement: {str(e)}")
            raise
    
    def analyze(self):
        """Analyse de base des données"""
        if self.data is None:
            self.load_data()
            
        analysis = {
            'file_info': self.get_file_info(),
            'data_summary': self.get_data_summary(),
            'column_analysis': self.get_column_analysis(),
            'data_quality': self.assess_data_quality(),
            'statistics': self.get_statistics()
        }
        
        return analysis
    
    def get_file_info(self):
        """Informations sur le fichier"""
        stat = os.stat(self.filepath)
        return {
            'filename': self.filename,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024*1024), 2),
            'extension': self.file_extension,
            'modified': stat.st_mtime,
            'hash_md5': self.calculate_hash('md5'),
            'hash_sha256': self.calculate_hash('sha256')
        }
    
    def calculate_hash(self, algorithm='md5'):
        """Calcule le hash du fichier"""
        hash_obj = hashlib.new(algorithm)
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def get_data_summary(self):
        """Résumé des données"""
        return {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'memory_usage_mb': round(self.data.memory_usage(deep=True).sum() / (1024*1024), 2),
            'column_names': list(self.data.columns),
            'data_types': self.data.dtypes.astype(str).to_dict()
        }
    
    def get_column_analysis(self):
        """Analyse détaillée des colonnes"""
        analysis = {}
        
        for col in self.data.columns:
            col_data = self.data[col]
            analysis[col] = {
                'type': str(col_data.dtype),
                'non_null_count': col_data.count(),
                'null_count': col_data.isnull().sum(),
                'null_percentage': round((col_data.isnull().sum() / len(col_data)) * 100, 2),
                'unique_count': col_data.nunique(),
                'unique_percentage': round((col_data.nunique() / len(col_data)) * 100, 2)
            }
            
            # Analyse spécifique selon le type
            if pd.api.types.is_numeric_dtype(col_data):
                analysis[col].update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': round(col_data.mean(), 2) if not col_data.isnull().all() else None,
                    'std': round(col_data.std(), 2) if not col_data.isnull().all() else None,
                    'outliers_count': self.detect_outliers(col_data)
                })
            elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
                analysis[col].update({
                    'avg_length': round(col_data.astype(str).str.len().mean(), 2),
                    'min_length': col_data.astype(str).str.len().min(),
                    'max_length': col_data.astype(str).str.len().max(),
                    'most_common': col_data.value_counts().head(5).to_dict()
                })
        
        return analysis
    
    def detect_outliers(self, series, method='iqr'):
        """Détection d'outliers"""
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            return len(outliers)
        return 0
    
    def assess_data_quality(self):
        """Évaluation de la qualité des données"""
        total_cells = len(self.data) * len(self.data.columns)
        null_cells = self.data.isnull().sum().sum()
        
        quality_score = max(0, 100 - (null_cells / total_cells * 100))
        
        issues = []
        
        # Détection des problèmes
        if null_cells > 0:
            issues.append(f"{null_cells} valeurs manquantes détectées")
        
        # Colonnes avec trop de valeurs nulles
        high_null_cols = []
        for col in self.data.columns:
            null_pct = (self.data[col].isnull().sum() / len(self.data)) * 100
            if null_pct > 50:
                high_null_cols.append(f"{col} ({null_pct:.1f}%)")
        
        if high_null_cols:
            issues.append(f"Colonnes avec >50% de valeurs nulles: {', '.join(high_null_cols)}")
        
        # Doublons
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            issues.append(f"{duplicates} lignes dupliquées")
        
        return {
            'quality_score': round(quality_score, 2),
            'total_cells': total_cells,
            'null_cells': null_cells,
            'duplicate_rows': duplicates,
            'issues': issues
        }
    
    def get_statistics(self):
        """Statistiques descriptives"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            return {
                'numeric_summary': self.data[numeric_cols].describe().round(2).to_dict(),
                'correlations': self.data[numeric_cols].corr().round(3).to_dict() if len(numeric_cols) > 1 else {}
            }
        
        return {'numeric_summary': {}, 'correlations': {}}
    
    def generate_visualizations(self):
        """Génération des visualisations"""
        if self.data is None:
            self.load_data()
        
        visualizations = {}
        
        try:
            # Graphique 1: Distribution des valeurs nulles
            null_counts = self.data.isnull().sum()
            if null_counts.sum() > 0:
                fig_nulls = px.bar(
                    x=null_counts.index, 
                    y=null_counts.values,
                    title="Valeurs manquantes par colonne",
                    labels={'x': 'Colonnes', 'y': 'Nombre de valeurs manquantes'}
                )
                visualizations['null_distribution'] = json.dumps(fig_nulls, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Graphique 2: Distribution des types de données
            dtype_counts = self.data.dtypes.value_counts()
            fig_types = px.pie(
                values=dtype_counts.values,
                names=dtype_counts.index.astype(str),
                title="Distribution des types de données"
            )
            visualizations['data_types'] = json.dumps(fig_types, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Graphique 3: Corrélations pour les colonnes numériques
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = self.data[numeric_cols].corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    title="Matrice de corrélation",
                    color_continuous_scale='RdBu_r',
                    aspect="auto"
                )
                visualizations['correlations'] = json.dumps(fig_corr, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Graphique 4: Histogrammes des colonnes numériques (première colonne)
            if len(numeric_cols) > 0:
                first_numeric_col = numeric_cols[0]
                fig_hist = px.histogram(
                    self.data,
                    x=first_numeric_col,
                    title=f"Distribution de {first_numeric_col}",
                    nbins=30
                )
                visualizations['first_numeric_distribution'] = json.dumps(fig_hist, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            self.logger.error(f"Erreur génération visualisations: {str(e)}")
        
        return visualizations
