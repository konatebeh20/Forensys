"""
Détecteur de patterns pour l'analyse forensique
Identifie des motifs récurrents et suspects dans les données
"""

import pandas as pd
import numpy as np
import re
from collections import Counter, defaultdict
import logging

class PatternDetector:
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
    
    def detect_patterns(self):
        """Détection de tous les types de patterns"""
        if self.data is None:
            self.load_data()
        
        patterns = {
            'sequential_patterns': self.detect_sequential_patterns(),
            'repetitive_patterns': self.detect_repetitive_patterns(),
            'frequency_patterns': self.detect_frequency_patterns(),
            'text_patterns': self.detect_text_patterns(),
            'numerical_patterns': self.detect_numerical_patterns(),
            'temporal_patterns': self.detect_temporal_patterns(),
            'correlation_patterns': self.detect_correlation_patterns()
        }
        
        return patterns
    
    def detect_sequential_patterns(self):
        """Détection de patterns séquentiels"""
        sequential_patterns = []
        
        for col in self.data.columns:
            if self.data[col].dtype in ['int64', 'float64']:
                values = self.data[col].dropna()
                if len(values) > 3:
                    # Vérification des séquences arithmétiques
                    diffs = values.diff().dropna()
                    if len(diffs.unique()) <= 3:  # Peu de différences uniques
                        most_common_diff = diffs.mode().iloc[0] if not diffs.mode().empty else None
                        if most_common_diff and (diffs == most_common_diff).sum() > len(diffs) * 0.7:
                            sequential_patterns.append({
                                'column': col,
                                'type': 'arithmetic_sequence',
                                'difference': most_common_diff,
                                'confidence': (diffs == most_common_diff).sum() / len(diffs)
                            })
                    
                    # Vérification des séquences géométriques
                    if (values > 0).all():
                        ratios = (values / values.shift(1)).dropna()
                        if len(ratios.unique()) <= 3:
                            most_common_ratio = ratios.mode().iloc[0] if not ratios.mode().empty else None
                            if most_common_ratio and (ratios == most_common_ratio).sum() > len(ratios) * 0.7:
                                sequential_patterns.append({
                                    'column': col,
                                    'type': 'geometric_sequence',
                                    'ratio': most_common_ratio,
                                    'confidence': (ratios == most_common_ratio).sum() / len(ratios)
                                })
        
        return sequential_patterns
    
    def detect_repetitive_patterns(self):
        """Détection de patterns répétitifs"""
        repetitive_patterns = []
        
        for col in self.data.columns:
            values = self.data[col].dropna()
            if len(values) > 0:
                value_counts = values.value_counts()
                
                # Valeurs très répétitives
                for value, count in value_counts.head(5).items():
                    frequency = count / len(values)
                    if frequency > 0.1:  # Plus de 10% des valeurs
                        repetitive_patterns.append({
                            'column': col,
                            'type': 'high_frequency_value',
                            'value': str(value)[:100],  # Limiter la longueur
                            'count': count,
                            'frequency': frequency
                        })
                
                # Patterns cycliques
                if self.data[col].dtype == 'object':
                    # Recherche de patterns cycliques dans les chaînes
                    cyclical = self._detect_cyclical_text_patterns(values)
                    if cyclical:
                        repetitive_patterns.extend(cyclical)
        
        return repetitive_patterns
    
    def _detect_cyclical_text_patterns(self, series):
        """Détecte les patterns cycliques dans le texte"""
        patterns = []
        text_values = series.astype(str).tolist()
        
        # Recherche de répétitions de sous-chaînes
        for i in range(min(len(text_values), 100)):  # Limite pour la performance
            text = text_values[i]
            if len(text) > 4:
                # Recherche de répétitions internes
                for length in range(2, min(len(text)//2, 10)):
                    substring = text[:length]
                    if text.count(substring) > 2:
                        patterns.append({
                            'column': series.name,
                            'type': 'cyclical_substring',
                            'pattern': substring,
                            'repetitions': text.count(substring),
                            'example': text[:50]
                        })
                        break
        
        return patterns
    
    def detect_frequency_patterns(self):
        """Analyse des patterns de fréquence"""
        frequency_patterns = []
        
        for col in self.data.columns:
            values = self.data[col].dropna()
            if len(values) > 10:
                value_counts = values.value_counts()
                
                # Distribution de fréquence
                freq_distribution = value_counts.value_counts()
                
                # Détection de distributions anormales
                if len(freq_distribution) > 1:
                    max_freq = freq_distribution.max()
                    total_unique = len(value_counts)
                    
                    # Beaucoup de valeurs avec la même fréquence (suspect)
                    if max_freq > total_unique * 0.3:
                        most_common_frequency = freq_distribution.idxmax()
                        frequency_patterns.append({
                            'column': col,
                            'type': 'uniform_frequency_distribution',
                            'frequency': most_common_frequency,
                            'count_values_with_frequency': max_freq,
                            'suspicion_level': 'high' if max_freq > total_unique * 0.5 else 'medium'
                        })
                
                # Analyse de la distribution Zipf (loi de Zipf)
                zipf_analysis = self._analyze_zipf_distribution(value_counts)
                if zipf_analysis['deviation'] > 0.3:
                    frequency_patterns.append({
                        'column': col,
                        'type': 'zipf_deviation',
                        'deviation_score': zipf_analysis['deviation'],
                        'expected_vs_actual': 'significant_deviation'
                    })
        
        return frequency_patterns
    
    def _analyze_zipf_distribution(self, value_counts):
        """Analyse la conformité à la loi de Zipf"""
        if len(value_counts) < 3:
            return {'deviation': 0}
        
        sorted_counts = value_counts.sort_values(ascending=False)
        ranks = np.arange(1, len(sorted_counts) + 1)
        
        # Calcul de la distribution Zipf attendue
        expected = sorted_counts.iloc[0] / ranks
        actual = sorted_counts.values
        
        # Calcul de la déviation
        deviation = np.mean(np.abs(actual - expected) / expected)
        
        return {'deviation': deviation}
    
    def detect_text_patterns(self):
        """Détection de patterns dans le texte"""
        text_patterns = []
        
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                text_values = self.data[col].dropna().astype(str)
                
                if len(text_values) > 0:
                    # Patterns d'expression régulière communs
                    patterns_to_check = {
                        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                        'phone': r'^[\+]?[1-9][\d]{0,15}$',
                        'url': r'^https?://',
                        'ip_address': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
                        'credit_card': r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$',
                        'social_security': r'^\d{3}-\d{2}-\d{4}$',
                        'hex_code': r'^[0-9a-fA-F]+$',
                        'base64': r'^[A-Za-z0-9+/]*={0,2}$'
                    }
                    
                    for pattern_name, regex in patterns_to_check.items():
                        matches = text_values.str.match(regex, na=False).sum()
                        if matches > 0:
                            percentage = matches / len(text_values) * 100
                            text_patterns.append({
                                'column': col,
                                'pattern_type': pattern_name,
                                'matches': matches,
                                'percentage': percentage,
                                'examples': text_values[text_values.str.match(regex, na=False)].head(3).tolist()
                            })
                    
                    # Analyse de la longueur des chaînes
                    lengths = text_values.str.len()
                    length_analysis = {
                        'min_length': lengths.min(),
                        'max_length': lengths.max(),
                        'avg_length': lengths.mean(),
                        'std_length': lengths.std()
                    }
                    
                    # Détection de longueurs suspectes
                    if length_analysis['std_length'] < 1 and len(text_values.unique()) > 1:
                        text_patterns.append({
                            'column': col,
                            'pattern_type': 'uniform_length',
                            'length': length_analysis['avg_length'],
                            'suspicion': 'strings_same_length_suspicious'
                        })
                    
                    # Analyse des caractères utilisés
                    char_analysis = self._analyze_character_usage(text_values)
                    if char_analysis['suspicious']:
                        text_patterns.append({
                            'column': col,
                            'pattern_type': 'character_analysis',
                            'findings': char_analysis
                        })
        
        return text_patterns
    
    def _analyze_character_usage(self, series):
        """Analyse l'utilisation des caractères"""
        all_text = ' '.join(series.astype(str))
        char_counter = Counter(all_text)
        
        # Détection de caractères suspects
        suspicious_chars = []
        for char, count in char_counter.items():
            if ord(char) > 127:  # Caractères non-ASCII
                suspicious_chars.append(char)
        
        # Calcul de la diversité des caractères
        total_chars = len(all_text)
        unique_chars = len(char_counter)
        diversity = unique_chars / total_chars if total_chars > 0 else 0
        
        return {
            'suspicious': len(suspicious_chars) > 0 or diversity < 0.1,
            'non_ascii_chars': suspicious_chars[:10],
            'character_diversity': diversity,
            'most_common_chars': dict(char_counter.most_common(10))
        }
    
    def detect_numerical_patterns(self):
        """Détection de patterns numériques"""
        numerical_patterns = []
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = self.data[col].dropna()
            if len(values) > 3:
                # Patterns mathématiques
                mathematical_patterns = self._detect_mathematical_patterns(values, col)
                numerical_patterns.extend(mathematical_patterns)
                
                # Analyse des digits
                digit_analysis = self._analyze_digit_patterns(values, col)
                if digit_analysis:
                    numerical_patterns.extend(digit_analysis)
                
                # Détection de distributions anormales
                distribution_analysis = self._analyze_numerical_distribution(values, col)
                if distribution_analysis:
                    numerical_patterns.extend(distribution_analysis)
        
        return numerical_patterns
    
    def _detect_mathematical_patterns(self, series, column_name):
        """Détecte les patterns mathématiques"""
        patterns = []
        
        # Suite de Fibonacci
        if self._is_fibonacci_like(series):
            patterns.append({
                'column': column_name,
                'type': 'fibonacci_like',
                'confidence': 'high'
            })
        
        # Nombres premiers
        if len(series) > 5:
            prime_percentage = self._calculate_prime_percentage(series)
            if prime_percentage > 0.7:
                patterns.append({
                    'column': column_name,
                    'type': 'high_prime_percentage',
                    'percentage': prime_percentage
                })
        
        # Puissances de 2
        powers_of_2 = self._count_powers_of_2(series)
        if powers_of_2 > len(series) * 0.3:
            patterns.append({
                'column': column_name,
                'type': 'powers_of_2',
                'count': powers_of_2,
                'percentage': powers_of_2 / len(series)
            })
        
        return patterns
    
    def _is_fibonacci_like(self, series):
        """Vérifie si la série ressemble à Fibonacci"""
        if len(series) < 3:
            return False
        
        values = series.sort_values().values
        fibonacci_matches = 0
        
        for i in range(2, min(len(values), 10)):
            if abs(values[i] - (values[i-1] + values[i-2])) < 1:
                fibonacci_matches += 1
        
        return fibonacci_matches >= len(values) * 0.6
    
    def _calculate_prime_percentage(self, series):
        """Calcule le pourcentage de nombres premiers"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        integers = series[series == series.astype(int)].astype(int)
        primes = integers[integers.apply(is_prime)]
        
        return len(primes) / len(integers) if len(integers) > 0 else 0
    
    def _count_powers_of_2(self, series):
        """Compte les puissances de 2"""
        powers_of_2 = 0
        for value in series:
            if value > 0 and (value & (value - 1)) == 0:
                powers_of_2 += 1
        return powers_of_2
    
    def _analyze_digit_patterns(self, series, column_name):
        """Analyse les patterns de digits"""
        patterns = []
        
        # Conversion en chaînes pour analyser les digits
        str_values = series.astype(str)
        
        # Analyse de Benford's Law (premier digit)
        first_digits = []
        for val in str_values:
            if val[0].isdigit() and val[0] != '0':
                first_digits.append(int(val[0]))
        
        if len(first_digits) > 30:  # Assez de données pour Benford
            benford_analysis = self._analyze_benford_law(first_digits)
            if benford_analysis['deviation'] > 0.1:
                patterns.append({
                    'column': column_name,
                    'type': 'benford_law_deviation',
                    'deviation': benford_analysis['deviation'],
                    'suspicion_level': 'high' if benford_analysis['deviation'] > 0.2 else 'medium'
                })
        
        return patterns
    
    def _analyze_benford_law(self, first_digits):
        """Analyse la conformité à la loi de Benford"""
        benford_expected = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
        
        digit_counts = Counter(first_digits)
        total = len(first_digits)
        
        observed_percentages = []
        for i in range(1, 10):
            observed_percentages.append((digit_counts.get(i, 0) / total) * 100)
        
        # Calcul de la déviation
        deviations = []
        for i in range(9):
            deviations.append(abs(observed_percentages[i] - benford_expected[i]))
        
        avg_deviation = np.mean(deviations) / 100  # Normaliser
        
        return {'deviation': avg_deviation}
    
    def _analyze_numerical_distribution(self, series, column_name):
        """Analyse la distribution numérique"""
        patterns = []
        
        # Détection de distributions trop uniformes
        hist, bins = np.histogram(series, bins=10)
        uniformity = np.std(hist) / np.mean(hist) if np.mean(hist) > 0 else 0
        
        if uniformity < 0.2:  # Distribution très uniforme
            patterns.append({
                'column': column_name,
                'type': 'too_uniform_distribution',
                'uniformity_score': uniformity,
                'suspicion': 'artificial_data_generation'
            })
        
        return patterns
    
    def detect_temporal_patterns(self):
        """Détection de patterns temporels"""
        temporal_patterns = []
        
        # Recherche de colonnes de dates
        date_columns = []
        for col in self.data.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'modified']):
                date_columns.append(col)
        
        for col in date_columns:
            try:
                dates = pd.to_datetime(self.data[col], errors='coerce').dropna()
                if len(dates) > 5:
                    # Analyse des intervals
                    interval_analysis = self._analyze_time_intervals(dates, col)
                    if interval_analysis:
                        temporal_patterns.extend(interval_analysis)
                    
                    # Analyse des patterns de jour/heure
                    if dates.dt.hour.nunique() > 1:  # Si on a des heures
                        hour_patterns = self._analyze_hour_patterns(dates, col)
                        if hour_patterns:
                            temporal_patterns.extend(hour_patterns)
                    
                    # Analyse des patterns de jour de la semaine
                    weekday_patterns = self._analyze_weekday_patterns(dates, col)
                    if weekday_patterns:
                        temporal_patterns.extend(weekday_patterns)
                        
            except Exception as e:
                self.logger.error(f"Erreur analyse temporelle {col}: {str(e)}")
        
        return temporal_patterns
    
    def _analyze_time_intervals(self, dates, column_name):
        """Analyse les intervalles de temps"""
        patterns = []
        
        sorted_dates = dates.sort_values()
        intervals = sorted_dates.diff().dropna()
        
        if len(intervals) > 3:
            # Intervalles très réguliers
            interval_counts = intervals.value_counts()
            if len(interval_counts) <= 3:  # Peu de variabilité
                most_common_interval = interval_counts.index[0]
                frequency = interval_counts.iloc[0] / len(intervals)
                
                if frequency > 0.5:  # Plus de 50% des intervalles identiques
                    patterns.append({
                        'column': column_name,
                        'type': 'regular_intervals',
                        'interval': str(most_common_interval),
                        'frequency': frequency,
                        'suspicion': 'automated_generation'
                    })
        
        return patterns
    
    def _analyze_hour_patterns(self, dates, column_name):
        """Analyse les patterns d'heures"""
        patterns = []
        
        hour_counts = dates.dt.hour.value_counts()
        
        # Activité concentrée sur certaines heures
        max_hour_count = hour_counts.max()
        total_entries = len(dates)
        
        if max_hour_count > total_entries * 0.3:  # Plus de 30% sur une seule heure
            peak_hour = hour_counts.idxmax()
            patterns.append({
                'column': column_name,
                'type': 'concentrated_hour_activity',
                'peak_hour': peak_hour,
                'percentage': (max_hour_count / total_entries) * 100
            })
        
        # Activité uniquement pendant les heures de bureau
        business_hours = hour_counts[(hour_counts.index >= 9) & (hour_counts.index <= 17)]
        business_percentage = business_hours.sum() / total_entries
        
        if business_percentage > 0.9:  # Plus de 90% pendant les heures de bureau
            patterns.append({
                'column': column_name,
                'type': 'business_hours_only',
                'percentage': business_percentage * 100
            })
        
        return patterns
    
    def _analyze_weekday_patterns(self, dates, column_name):
        """Analyse les patterns de jours de la semaine"""
        patterns = []
        
        weekday_counts = dates.dt.dayofweek.value_counts()
        
        # Activité concentrée sur les jours de semaine
        weekdays = weekday_counts[weekday_counts.index < 5].sum()  # Lundi-Vendredi
        weekends = weekday_counts[weekday_counts.index >= 5].sum()  # Samedi-Dimanche
        
        total = weekdays + weekends
        if total > 0:
            weekday_percentage = weekdays / total
            
            if weekday_percentage > 0.9:  # Plus de 90% en semaine
                patterns.append({
                    'column': column_name,
                    'type': 'weekdays_only_pattern',
                    'weekday_percentage': weekday_percentage * 100
                })
            elif weekday_percentage < 0.1:  # Plus de 90% en weekend
                patterns.append({
                    'column': column_name,
                    'type': 'weekends_only_pattern',
                    'weekend_percentage': (1 - weekday_percentage) * 100
                })
        
        return patterns
    
    def detect_correlation_patterns(self):
        """Détection de patterns de corrélation"""
        correlation_patterns = []
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            correlation_matrix = self.data[numeric_cols].corr()
            
            # Recherche de corrélations parfaites ou suspectes
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j:  # Éviter les doublons
                        corr_value = correlation_matrix.loc[col1, col2]
                        
                        if abs(corr_value) > 0.95 and abs(corr_value) < 1.0:
                            correlation_patterns.append({
                                'column1': col1,
                                'column2': col2,
                                'correlation': corr_value,
                                'type': 'high_correlation',
                                'suspicion': 'derived_or_duplicated_data'
                            })
                        elif abs(corr_value) == 1.0:
                            correlation_patterns.append({
                                'column1': col1,
                                'column2': col2,
                                'correlation': corr_value,
                                'type': 'perfect_correlation',
                                'suspicion': 'identical_or_linear_transformation'
                            })
            
            # Détection de patterns de corrélation multiple
            high_corr_cols = []
            for col in numeric_cols:
                high_corrs = (correlation_matrix[col].abs() > 0.8).sum() - 1  # -1 pour exclure self
                if high_corrs > len(numeric_cols) * 0.3:
                    high_corr_cols.append(col)
            
            if len(high_corr_cols) > 0:
                correlation_patterns.append({
                    'type': 'multiple_high_correlations',
                    'columns': high_corr_cols,
                    'suspicion': 'data_redundancy_or_artificial_generation'
                })
        
        return correlation_patterns
