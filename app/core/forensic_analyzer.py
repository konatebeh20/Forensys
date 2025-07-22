"""
Analyseur Forensique
Effectue des analyses de sécurité et forensiques sur les données
"""

import pandas as pd
import numpy as np
import os
import datetime
import hashlib
import re
import json
import logging
from collections import Counter
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

class ForensicAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.data = None
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """Charge les données pour l'analyse forensique"""
        if self.data is None:
            try:
                file_extension = self.filename.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    # Essai de différents encodages et séparateurs
                    encodings = ['utf-8', 'latin-1', 'cp1252']
                    separators = [',', ';', '\t']
                    
                    for encoding in encodings:
                        for sep in separators:
                            try:
                                self.data = pd.read_csv(self.filepath, encoding=encoding, sep=sep)
                                if len(self.data.columns) > 1:
                                    return
                            except:
                                continue
                                
                elif file_extension in ['xlsx', 'xls']:
                    self.data = pd.read_excel(self.filepath)
                    
                elif file_extension in ['db', 'sqlite']:
                    import sqlite3
                    conn = sqlite3.connect(self.filepath)
                    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                    if not tables.empty:
                        table_name = tables['name'].iloc[0]
                        self.data = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
                    conn.close()
                    
            except Exception as e:
                self.logger.error(f"Erreur chargement données forensiques: {str(e)}")
                raise
    
    def full_analysis(self):
        """Analyse forensique complète"""
        if self.data is None:
            self.load_data()
        
        analysis = {
            'file_metadata': self.get_file_metadata(),
            'data_integrity': self.check_data_integrity(),
            'suspicious_patterns': self.detect_suspicious_patterns(),
            'timestamp_analysis': self.analyze_timestamps(),
            'user_activity': self.analyze_user_activity(),
            'security_indicators': self.detect_security_indicators(),
            'data_manipulation': self.detect_data_manipulation(),
            'forensic_timeline': self.create_forensic_timeline()
        }
        
        return analysis
    
    def get_file_metadata(self):
        """Métadonnées détaillées du fichier"""
        stat = os.stat(self.filepath)
        
        metadata = {
            'filename': self.filename,
            'full_path': self.filepath,
            'size_bytes': stat.st_size,
            'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.datetime.fromtimestamp(stat.st_atime).isoformat(),
            'permissions': oct(stat.st_mode)[-3:],
            'md5_hash': self._calculate_hash('md5'),
            'sha1_hash': self._calculate_hash('sha1'),
            'sha256_hash': self._calculate_hash('sha256')
        }
        
        # Détection du type MIME
        if HAS_MAGIC:
            try:
                mime_type = magic.from_file(self.filepath, mime=True)
                metadata['mime_type'] = mime_type
            except:
                metadata['mime_type'] = 'unknown'
        else:
            metadata['mime_type'] = 'unknown'
        
        return metadata
    
    def _calculate_hash(self, algorithm):
        """Calcule le hash du fichier"""
        hash_obj = hashlib.new(algorithm)
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def check_data_integrity(self):
        """Vérification de l'intégrité des données"""
        integrity_issues = []
        
        # Vérification des colonnes dupliquées
        duplicate_columns = self.data.columns[self.data.columns.duplicated()].tolist()
        if duplicate_columns:
            integrity_issues.append(f"Colonnes dupliquées: {duplicate_columns}")
        
        # Vérification des lignes entièrement dupliquées
        duplicate_rows = self.data.duplicated().sum()
        if duplicate_rows > 0:
            integrity_issues.append(f"{duplicate_rows} lignes complètement dupliquées")
        
        # Vérification des valeurs impossibles/suspectes
        for col in self.data.columns:
            if self.data[col].dtype in ['int64', 'float64']:
                # Valeurs négatives dans des colonnes qui ne devraient pas en avoir
                if 'age' in col.lower() or 'count' in col.lower() or 'quantity' in col.lower():
                    negative_count = (self.data[col] < 0).sum()
                    if negative_count > 0:
                        integrity_issues.append(f"Valeurs négatives suspectes dans {col}: {negative_count}")
        
        # Incohérences de format
        format_issues = self._detect_format_inconsistencies()
        integrity_issues.extend(format_issues)
        
        return {
            'issues_count': len(integrity_issues),
            'issues': integrity_issues,
            'integrity_score': max(0, 100 - (len(integrity_issues) * 10))
        }
    
    def _detect_format_inconsistencies(self):
        """Détecte les incohérences de format"""
        issues = []
        
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                # Vérification des formats de date incohérents
                if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'modified']):
                    unique_formats = self._analyze_date_formats(self.data[col])
                    if len(unique_formats) > 1:
                        issues.append(f"Formats de date incohérents dans {col}: {unique_formats}")
                
                # Vérification des formats d'email
                if 'email' in col.lower() or 'mail' in col.lower():
                    invalid_emails = self._count_invalid_emails(self.data[col])
                    if invalid_emails > 0:
                        issues.append(f"Emails invalides dans {col}: {invalid_emails}")
        
        return issues
    
    def _analyze_date_formats(self, series):
        """Analyse les formats de date dans une série"""
        formats = set()
        for value in series.dropna().astype(str):
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                formats.add('YYYY-MM-DD')
            elif re.match(r'\d{2}/\d{2}/\d{4}', value):
                formats.add('MM/DD/YYYY')
            elif re.match(r'\d{2}-\d{2}-\d{4}', value):
                formats.add('MM-DD-YYYY')
        return list(formats)
    
    def _count_invalid_emails(self, series):
        """Compte les emails invalides"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_count = 0
        for email in series.dropna():
            if not re.match(email_pattern, str(email)):
                invalid_count += 1
        return invalid_count
    
    def detect_suspicious_patterns(self):
        """Détection de patterns suspects"""
        suspicious = []
        
        # Recherche de patterns d'injection SQL
        sql_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s",
            r"(?i)(script|javascript|onclick|onerror)",
            r"['\";].*(\||\||&|&&)",
            r"(?i)(exec|execute|sp_|xp_)"
        ]
        
        # Recherche de patterns XSS
        xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>"
        ]
        
        # Analyse de toutes les colonnes textuelles
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                col_data = self.data[col].astype(str)
                
                # Test des patterns SQL
                for pattern in sql_patterns:
                    matches = col_data.str.contains(pattern, regex=True, na=False).sum()
                    if matches > 0:
                        suspicious.append(f"Pattern SQL suspect dans {col}: {matches} occurrences")
                
                # Test des patterns XSS
                for pattern in xss_patterns:
                    matches = col_data.str.contains(pattern, regex=True, na=False).sum()
                    if matches > 0:
                        suspicious.append(f"Pattern XSS suspect dans {col}: {matches} occurrences")
                
                # Recherche de caractères suspects
                suspicious_chars = col_data.str.contains(r'[^\x00-\x7F]', regex=True, na=False).sum()
                if suspicious_chars > len(self.data) * 0.1:  # Plus de 10% de caractères non-ASCII
                    suspicious.append(f"Nombreux caractères non-ASCII dans {col}: {suspicious_chars}")
        
        return {
            'patterns_found': len(suspicious),
            'details': suspicious
        }
    
    def analyze_timestamps(self):
        """Analyse des timestamps pour détecter des anomalies"""
        timestamp_analysis = {}
        
        # Recherche de colonnes de dates/temps
        date_columns = []
        for col in self.data.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'modified', 'updated']):
                date_columns.append(col)
        
        for col in date_columns:
            try:
                # Conversion en datetime
                dates = pd.to_datetime(self.data[col], errors='coerce')
                valid_dates = dates.dropna()
                
                if len(valid_dates) > 0:
                    analysis = {
                        'earliest': valid_dates.min().isoformat(),
                        'latest': valid_dates.max().isoformat(),
                        'span_days': (valid_dates.max() - valid_dates.min()).days,
                        'invalid_dates': len(dates) - len(valid_dates)
                    }
                    
                    # Détection d'anomalies temporelles
                    anomalies = []
                    
                    # Dates futures
                    future_dates = (valid_dates > datetime.datetime.now()).sum()
                    if future_dates > 0:
                        anomalies.append(f"{future_dates} dates dans le futur")
                    
                    # Dates très anciennes (avant 1900)
                    old_dates = (valid_dates < datetime.datetime(1900, 1, 1)).sum()
                    if old_dates > 0:
                        anomalies.append(f"{old_dates} dates avant 1900")
                    
                    # Pics d'activité suspects
                    date_counts = valid_dates.value_counts()
                    if len(date_counts) > 0:
                        max_count = date_counts.max()
                        avg_count = date_counts.mean()
                        if max_count > avg_count * 10:  # Plus de 10x la moyenne
                            anomalies.append(f"Pic d'activité suspect: {max_count} entrées le même jour")
                    
                    analysis['anomalies'] = anomalies
                    timestamp_analysis[col] = analysis
                    
            except Exception as e:
                timestamp_analysis[col] = {'error': str(e)}
        
        return timestamp_analysis
    
    def analyze_user_activity(self):
        """Analyse de l'activité utilisateur"""
        user_analysis = {}
        
        # Recherche de colonnes utilisateur
        user_columns = []
        for col in self.data.columns:
            if any(keyword in col.lower() for keyword in ['user', 'username', 'login', 'email', 'account']):
                user_columns.append(col)
        
        for col in user_columns:
            user_data = self.data[col].dropna()
            
            if len(user_data) > 0:
                analysis = {
                    'unique_users': user_data.nunique(),
                    'total_activities': len(user_data),
                    'top_users': user_data.value_counts().head(10).to_dict()
                }
                
                # Détection d'activité suspecte
                suspicious_activity = []
                
                # Utilisateurs avec activité anormalement élevée
                user_counts = user_data.value_counts()
                if len(user_counts) > 0:
                    threshold = user_counts.quantile(0.95)
                    high_activity_users = user_counts[user_counts > threshold]
                    if len(high_activity_users) > 0:
                        suspicious_activity.append(f"{len(high_activity_users)} utilisateurs avec activité élevée")
                
                # Patterns de noms suspects
                suspicious_names = user_data[user_data.str.contains(r'(admin|root|test|demo|guest)', 
                                                                  case=False, na=False)].unique()
                if len(suspicious_names) > 0:
                    suspicious_activity.append(f"Noms d'utilisateurs suspects: {list(suspicious_names)[:5]}")
                
                analysis['suspicious_activity'] = suspicious_activity
                user_analysis[col] = analysis
        
        return user_analysis
    
    def detect_security_indicators(self):
        """Détection d'indicateurs de sécurité"""
        security_indicators = []
        
        # Recherche de mots-clés de sécurité
        security_keywords = [
            'password', 'passwd', 'secret', 'token', 'key', 'hash',
            'exploit', 'vulnerability', 'attack', 'malware', 'virus',
            'breach', 'compromise', 'unauthorized', 'suspicious'
        ]
        
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                col_data = self.data[col].astype(str)
                
                for keyword in security_keywords:
                    matches = col_data.str.contains(keyword, case=False, na=False).sum()
                    if matches > 0:
                        security_indicators.append({
                            'type': 'security_keyword',
                            'keyword': keyword,
                            'column': col,
                            'occurrences': matches
                        })
        
        # Recherche d'adresses IP suspectes
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                col_data = self.data[col].astype(str)
                ip_matches = col_data.str.extractall(ip_pattern)
                if not ip_matches.empty:
                    unique_ips = col_data.str.findall(ip_pattern).explode().unique()
                    security_indicators.append({
                        'type': 'ip_addresses',
                        'column': col,
                        'count': len(unique_ips),
                        'sample_ips': list(unique_ips)[:5]
                    })
        
        return security_indicators
    
    def detect_data_manipulation(self):
        """Détection de manipulation de données"""
        manipulation_indicators = []
        
        # Vérification des patterns de modification
        for col in self.data.columns:
            if self.data[col].dtype in ['int64', 'float64']:
                # Détection de valeurs arrondies suspectes (trop de zéros)
                rounded_values = self.data[col].dropna()
                if len(rounded_values) > 0:
                    # Valeurs se terminant par 00
                    ending_zeros = (rounded_values % 100 == 0).sum()
                    if ending_zeros > len(rounded_values) * 0.3:  # Plus de 30%
                        manipulation_indicators.append(f"Valeurs suspectes arrondies dans {col}: {ending_zeros}")
                    
                    # Valeurs identiques suspectes
                    value_counts = rounded_values.value_counts()
                    if len(value_counts) > 0:
                        most_common_count = value_counts.iloc[0]
                        if most_common_count > len(rounded_values) * 0.1:  # Plus de 10%
                            manipulation_indicators.append(f"Valeur répétée suspecte dans {col}: {most_common_count} fois")
        
        # Vérification des patterns de texte suspects
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                text_data = self.data[col].dropna().astype(str)
                
                # Textes identiques suspects
                if len(text_data) > 0:
                    text_counts = text_data.value_counts()
                    if len(text_counts) > 0:
                        most_common_count = text_counts.iloc[0]
                        if most_common_count > len(text_data) * 0.1:  # Plus de 10%
                            manipulation_indicators.append(f"Texte répété suspect dans {col}: '{text_counts.index[0][:50]}...'")
        
        return {
            'indicators_count': len(manipulation_indicators),
            'indicators': manipulation_indicators
        }
    
    def create_forensic_timeline(self):
        """Création d'une timeline forensique"""
        timeline_events = []
        
        # Métadonnées du fichier
        stat = os.stat(self.filepath)
        timeline_events.extend([
            {
                'timestamp': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'event': 'file_created',
                'description': f"Fichier {self.filename} créé"
            },
            {
                'timestamp': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'event': 'file_modified',
                'description': f"Fichier {self.filename} modifié"
            },
            {
                'timestamp': datetime.datetime.fromtimestamp(stat.st_atime).isoformat(),
                'event': 'file_accessed',
                'description': f"Fichier {self.filename} accédé"
            }
        ])
        
        # Événements basés sur les données
        date_columns = [col for col in self.data.columns 
                       if any(keyword in col.lower() for keyword in ['date', 'time', 'created'])]
        
        for col in date_columns[:1]:  # Prendre seulement la première colonne de date
            try:
                dates = pd.to_datetime(self.data[col], errors='coerce').dropna()
                if len(dates) > 0:
                    # Ajouter quelques événements représentatifs
                    sample_dates = dates.sample(min(10, len(dates))).sort_values()
                    for date in sample_dates:
                        timeline_events.append({
                            'timestamp': date.isoformat(),
                            'event': 'data_entry',
                            'description': f"Entrée de données dans {col}"
                        })
            except:
                continue
        
        # Trier par timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        return timeline_events
