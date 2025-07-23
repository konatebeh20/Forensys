"""
Détecteur d'anomalies pour l'analyse forensique
Utilise des techniques de machine learning pour détecter des anomalies
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging

class AnomalyDetector:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """Charge les données"""
        if self.data is None:
            try:
                file_extension = self.filepath.split('.')[-1].lower()
                
                if file_extension == 'csv':
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
                self.logger.error(f"Erreur chargement données: {str(e)}")
                raise
    
    def detect_anomalies(self):
        """Détection complète d'anomalies"""
        if self.data is None:
            self.load_data()
        
        anomalies = {
            'statistical_outliers': self.detect_statistical_outliers(),
            'isolation_forest_anomalies': self.detect_isolation_forest_anomalies(),
            'clustering_anomalies': self.detect_clustering_anomalies(),
            'pattern_based_anomalies': self.detect_pattern_based_anomalies(),
            'temporal_anomalies': self.detect_temporal_anomalies(),
            'text_anomalies': self.detect_text_anomalies(),
            'summary': self.generate_anomaly_summary()
        }
        
        return anomalies
    
    def detect_statistical_outliers(self):
        """Détection d'outliers statistiques"""
        outliers = {}
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            if len(col_data) > 10:
                # Méthode IQR
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                
                # Méthode Z-score
                z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                zscore_outliers = col_data[z_scores > 3]
                
                # Méthode modified Z-score (plus robuste)
                median = col_data.median()
                mad = np.median(np.abs(col_data - median))
                modified_z_scores = 0.6745 * (col_data - median) / mad
                modified_zscore_outliers = col_data[np.abs(modified_z_scores) > 3.5]
                
                outliers[col] = {
                    'iqr_outliers': {
                        'count': len(iqr_outliers),
                        'percentage': len(iqr_outliers) / len(col_data) * 100,
                        'values': iqr_outliers.head(10).tolist(),
                        'bounds': {'lower': lower_bound, 'upper': upper_bound}
                    },
                    'zscore_outliers': {
                        'count': len(zscore_outliers),
                        'percentage': len(zscore_outliers) / len(col_data) * 100,
                        'values': zscore_outliers.head(10).tolist()
                    },
                    'modified_zscore_outliers': {
                        'count': len(modified_zscore_outliers),
                        'percentage': len(modified_zscore_outliers) / len(col_data) * 100,
                        'values': modified_zscore_outliers.head(10).tolist()
                    }
                }
        
        return outliers
    
    def detect_isolation_forest_anomalies(self):
        """Détection d'anomalies avec Isolation Forest"""
        try:
            numeric_data = self.data.select_dtypes(include=[np.number])
            
            if numeric_data.empty or len(numeric_data) < 10:
                return {'error': 'Pas assez de données numériques'}
            
            # Préparation des données
            numeric_data_clean = numeric_data.dropna()
            if len(numeric_data_clean) < 10:
                return {'error': 'Pas assez de données après nettoyage'}
            
            # Standardisation
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data_clean)
            
            # Isolation Forest
            isolation_forest = IsolationForest(
                contamination=0.1,  # 10% d'anomalies attendues
                random_state=42,
                n_estimators=100
            )
            
            anomaly_labels = isolation_forest.fit_predict(scaled_data)
            anomaly_scores = isolation_forest.decision_function(scaled_data)
            
            # Identification des anomalies
            anomalies_mask = anomaly_labels == -1
            anomalous_indices = numeric_data_clean.index[anomalies_mask]
            
            # Analyse des anomalies
            anomaly_analysis = []
            for idx in anomalous_indices[:20]:  # Limiter à 20 pour la performance
                row_data = self.data.loc[idx]
                score = anomaly_scores[numeric_data_clean.index.get_loc(idx)]
                
                anomaly_analysis.append({
                    'index': int(idx),
                    'anomaly_score': float(score),
                    'data_sample': {col: str(row_data[col])[:100] for col in row_data.index[:5]}
                })
            
            return {
                'total_anomalies': len(anomalous_indices),
                'percentage': len(anomalous_indices) / len(numeric_data_clean) * 100,
                'anomaly_details': anomaly_analysis,
                'feature_importance': self._calculate_feature_importance(
                    scaled_data, anomaly_labels, numeric_data_clean.columns
                )
            }
            
        except Exception as e:
            self.logger.error(f"Erreur Isolation Forest: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_feature_importance(self, data, labels, feature_names):
        """Calcule l'importance des features pour les anomalies"""
        try:
            anomalies = data[labels == -1]
            normal = data[labels == 1]
            
            if len(anomalies) == 0 or len(normal) == 0:
                return {}
            
            importance = {}
            for i, feature in enumerate(feature_names):
                # Différence de moyenne entre anomalies et données normales
                anomaly_mean = np.mean(anomalies[:, i])
                normal_mean = np.mean(normal[:, i])
                importance[feature] = abs(anomaly_mean - normal_mean)
            
            # Normalisation
            max_importance = max(importance.values()) if importance.values() else 1
            importance = {k: v/max_importance for k, v in importance.items()}
            
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        except:
            return {}
    
    def detect_clustering_anomalies(self):
        """Détection d'anomalies par clustering"""
        try:
            numeric_data = self.data.select_dtypes(include=[np.number]).dropna()
            
            if numeric_data.empty or len(numeric_data) < 10:
                return {'error': 'Pas assez de données numériques'}
            
            # Standardisation
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # Réduction de dimensionnalité si nécessaire
            if scaled_data.shape[1] > 5:
                pca = PCA(n_components=min(5, scaled_data.shape[1]))
                scaled_data = pca.fit_transform(scaled_data)
            
            # DBSCAN clustering
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            cluster_labels = dbscan.fit_predict(scaled_data)
            
            # Identification des anomalies (points avec label -1)
            anomalies_mask = cluster_labels == -1
            anomalous_indices = numeric_data.index[anomalies_mask]
            
            # Analyse des clusters
            unique_labels = set(cluster_labels)
            cluster_info = {}
            
            for label in unique_labels:
                if label != -1:  # Exclure les anomalies
                    cluster_mask = cluster_labels == label
                    cluster_size = np.sum(cluster_mask)
                    cluster_info[f'cluster_{label}'] = {
                        'size': int(cluster_size),
                        'percentage': float(cluster_size / len(cluster_labels) * 100)
                    }
            
            return {
                'total_anomalies': len(anomalous_indices),
                'percentage': len(anomalous_indices) / len(numeric_data) * 100,
                'anomalous_indices': anomalous_indices[:20].tolist(),
                'cluster_info': cluster_info,
                'total_clusters': len(unique_labels) - (1 if -1 in unique_labels else 0)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur clustering: {str(e)}")
            return {'error': str(e)}
    
    def detect_pattern_based_anomalies(self):
        """Détection d'anomalies basée sur les patterns"""
        pattern_anomalies = []
        
        # Anomalies de fréquence
        for col in self.data.columns:
            col_data = self.data[col].dropna()
            if len(col_data) > 10:
                value_counts = col_data.value_counts()
                
                # Valeurs uniques dans un dataset avec beaucoup de répétitions
                if len(value_counts) > 1:
                    singleton_count = (value_counts == 1).sum()
                    singleton_percentage = singleton_count / len(value_counts) * 100
                    
                    if singleton_percentage < 10 and singleton_count > 0:
                        singletons = value_counts[value_counts == 1].index.tolist()
                        pattern_anomalies.append({
                            'column': col,
                            'type': 'rare_values',
                            'count': singleton_count,
                            'percentage': singleton_percentage,
                            'examples': singletons[:5]
                        })
                
                # Valeurs extrêmement fréquentes
                max_frequency = value_counts.iloc[0]
                if max_frequency > len(col_data) * 0.8:  # Plus de 80%
                    pattern_anomalies.append({
                        'column': col,
                        'type': 'dominant_value',
                        'value': str(value_counts.index[0])[:100],
                        'frequency': max_frequency,
                        'percentage': max_frequency / len(col_data) * 100
                    })
        
        # Anomalies de longueur pour les chaînes
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                text_data = self.data[col].dropna().astype(str)
                if len(text_data) > 0:
                    lengths = text_data.str.len()
                    
                    # Chaînes anormalement longues ou courtes
                    mean_length = lengths.mean()
                    std_length = lengths.std()
                    
                    if std_length > 0:
                        z_scores = np.abs((lengths - mean_length) / std_length)
                        length_anomalies = text_data[z_scores > 3]
                        
                        if len(length_anomalies) > 0:
                            pattern_anomalies.append({
                                'column': col,
                                'type': 'abnormal_length',
                                'count': len(length_anomalies),
                                'examples': length_anomalies.head(3).tolist(),
                                'mean_length': mean_length,
                                'anomaly_lengths': lengths[z_scores > 3].tolist()[:5]
                            })
        
        return pattern_anomalies
    
    def detect_temporal_anomalies(self):
        """Détection d'anomalies temporelles"""
        temporal_anomalies = []
        
        # Recherche de colonnes de dates
        date_columns = []
        for col in self.data.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'modified']):
                date_columns.append(col)
        
        for col in date_columns:
            try:
                dates = pd.to_datetime(self.data[col], errors='coerce').dropna()
                if len(dates) > 5:
                    # Détection de gaps temporels importants
                    sorted_dates = dates.sort_values()
                    intervals = sorted_dates.diff().dropna()
                    
                    if len(intervals) > 3:
                        # Intervalles anormalement longs
                        mean_interval = intervals.mean()
                        std_interval = intervals.std()
                        
                        if std_interval > pd.Timedelta(0):
                            threshold = mean_interval + 3 * std_interval
                            large_gaps = intervals[intervals > threshold]
                            
                            if len(large_gaps) > 0:
                                temporal_anomalies.append({
                                    'column': col,
                                    'type': 'temporal_gaps',
                                    'count': len(large_gaps),
                                    'largest_gap': str(large_gaps.max()),
                                    'mean_interval': str(mean_interval),
                                    'gap_locations': [str(d) for d in sorted_dates[intervals > threshold][:3]]
                                })
                    
                    # Détection de bursts (beaucoup d'activité en peu de temps)
                    date_counts = dates.dt.date.value_counts()
                    if len(date_counts) > 1:
                        mean_daily_count = date_counts.mean()
                        std_daily_count = date_counts.std()
                        
                        if std_daily_count > 0:
                            burst_threshold = mean_daily_count + 3 * std_daily_count
                            burst_days = date_counts[date_counts > burst_threshold]
                            
                            if len(burst_days) > 0:
                                temporal_anomalies.append({
                                    'column': col,
                                    'type': 'activity_bursts',
                                    'count': len(burst_days),
                                    'burst_days': [str(d) for d in burst_days.index[:3]],
                                    'max_daily_activity': int(burst_days.max()),
                                    'mean_daily_activity': float(mean_daily_count)
                                })
                        
            except Exception as e:
                self.logger.error(f"Erreur analyse temporelle {col}: {str(e)}")
        
        return temporal_anomalies
    
    def detect_text_anomalies(self):
        """Détection d'anomalies dans le texte"""
        text_anomalies = []
        
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                text_data = self.data[col].dropna().astype(str)
                
                if len(text_data) > 10:
                    # Détection d'encoding/caractères suspects
                    encoding_issues = []
                    for idx, text in text_data.items():
                        try:
                            # Vérification des caractères non-printables
                            non_printable = sum(1 for c in text if ord(c) < 32 and c not in '\t\n\r')
                            if non_printable > 0:
                                encoding_issues.append({
                                    'index': idx,
                                    'text_preview': text[:50],
                                    'non_printable_count': non_printable
                                })
                        except:
                            encoding_issues.append({
                                'index': idx,
                                'text_preview': str(text)[:50],
                                'error': 'encoding_error'
                            })
                    
                    if len(encoding_issues) > 0:
                        text_anomalies.append({
                            'column': col,
                            'type': 'encoding_anomalies',
                            'count': len(encoding_issues),
                            'examples': encoding_issues[:5]
                        })
                    
                    # Détection de patterns de hash/encoded data
                    potential_hashes = []
                    for text in text_data:
                        # Vérification de patterns hex
                        if len(text) in [32, 40, 64] and all(c in '0123456789abcdefABCDEF' for c in text):
                            potential_hashes.append(text)
                        # Vérification de patterns base64
                        elif len(text) % 4 == 0 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in text):
                            if len(text) > 20:  # Assez long pour être un hash
                                potential_hashes.append(text)
                    
                    if len(potential_hashes) > len(text_data) * 0.1:  # Plus de 10%
                        text_anomalies.append({
                            'column': col,
                            'type': 'encoded_data',
                            'count': len(potential_hashes),
                            'percentage': len(potential_hashes) / len(text_data) * 100,
                            'examples': potential_hashes[:3]
                        })
                    
                    # Détection de texte très répétitif
                    repetitive_texts = []
                    for text in text_data:
                        if len(text) > 10:
                            # Vérification de caractères répétés
                            max_char_repeat = max([text.count(c) for c in set(text)] + [0])
                            if max_char_repeat > len(text) * 0.5:  # Plus de 50% du même caractère
                                repetitive_texts.append(text[:50])
                    
                    if len(repetitive_texts) > 0:
                        text_anomalies.append({
                            'column': col,
                            'type': 'repetitive_text',
                            'count': len(repetitive_texts),
                            'examples': repetitive_texts[:3]
                        })
        
        return text_anomalies
    
    def generate_anomaly_summary(self):
        """Génère un résumé des anomalies détectées"""
        if self.data is None:
            return {}
        
        total_rows = len(self.data)
        total_cols = len(self.data.columns)
        
        # Calcul rapide d'anomalies de base
        null_percentage = (self.data.isnull().sum().sum() / (total_rows * total_cols)) * 100
        duplicate_rows = self.data.duplicated().sum()
        
        summary = {
            'dataset_info': {
                'total_rows': total_rows,
                'total_columns': total_cols,
                'null_percentage': round(null_percentage, 2),
                'duplicate_rows': duplicate_rows
            },
            'anomaly_indicators': {
                'high_null_percentage': null_percentage > 20,
                'many_duplicates': duplicate_rows > total_rows * 0.1,
                'suspicious_uniformity': self._check_suspicious_uniformity(),
                'encoding_issues': self._check_encoding_issues()
            },
            'risk_assessment': self._assess_overall_risk()
        }
        
        return summary
    
    def _check_suspicious_uniformity(self):
        """Vérifie l'uniformité suspecte des données"""
        uniform_columns = 0
        total_columns = 0
        
        for col in self.data.columns:
            if len(self.data[col].dropna()) > 10:
                total_columns += 1
                unique_ratio = self.data[col].nunique() / len(self.data[col].dropna())
                
                # Très peu de valeurs uniques ou toutes identiques
                if unique_ratio < 0.1:
                    uniform_columns += 1
        
        return uniform_columns > total_columns * 0.3 if total_columns > 0 else False
    
    def _check_encoding_issues(self):
        """Vérifie les problèmes d'encodage"""
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                text_sample = self.data[col].dropna().astype(str).head(100)
                for text in text_sample:
                    try:
                        # Vérification de caractères suspects
                        if any(ord(c) > 127 for c in text[:100]):
                            non_ascii_ratio = sum(1 for c in text[:100] if ord(c) > 127) / len(text[:100])
                            if non_ascii_ratio > 0.5:  # Plus de 50% de caractères non-ASCII
                                return True
                    except:
                        return True
        return False
    
    def _assess_overall_risk(self):
        """Évalue le risque global basé sur les indicateurs"""
        risk_score = 0
        risk_factors = []
        
        # Facteurs de risque basiques
        null_percentage = (self.data.isnull().sum().sum() / (len(self.data) * len(self.data.columns))) * 100
        if null_percentage > 30:
            risk_score += 2
            risk_factors.append("High percentage of missing data")
        elif null_percentage > 10:
            risk_score += 1
            risk_factors.append("Moderate missing data")
        
        duplicate_percentage = (self.data.duplicated().sum() / len(self.data)) * 100
        if duplicate_percentage > 20:
            risk_score += 2
            risk_factors.append("High percentage of duplicate rows")
        elif duplicate_percentage > 5:
            risk_score += 1
            risk_factors.append("Some duplicate rows")
        
        # Uniformité suspecte
        if self._check_suspicious_uniformity():
            risk_score += 3
            risk_factors.append("Suspicious data uniformity")
        
        # Problèmes d'encodage
        if self._check_encoding_issues():
            risk_score += 2
            risk_factors.append("Potential encoding issues")
        
        # Évaluation finale
        if risk_score >= 6:
            risk_level = "High"
        elif risk_score >= 3:
            risk_level = "Medium"
        elif risk_score >= 1:
            risk_level = "Low"
        else:
            risk_level = "Very Low"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level):
        """Retourne des recommandations basées sur le niveau de risque"""
        recommendations = {
            "Very Low": "Data appears normal. Continue with standard analysis.",
            "Low": "Minor issues detected. Review identified anomalies.",
            "Medium": "Several anomalies detected. Investigate data sources and collection methods.",
            "High": "Significant anomalies detected. Recommend thorough forensic investigation and data validation."
        }
        return recommendations.get(risk_level, "Unknown risk level")
