"""
Data Science and Big Data Analytics Module
Demonstrates data processing, analysis, and visualization capabilities
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import json
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')


class DataGenerator:
    """Generate synthetic datasets for demonstration"""
    
    @staticmethod
    def generate_iot_data(n_samples: int = 10000, n_devices: int = 50) -> pd.DataFrame:
        """Generate IoT sensor data with temporal patterns"""
        devices = [f"Device_{i:03d}" for i in range(n_devices)]
        start_time = datetime.now() - timedelta(days=30)
        
        data = []
        for i in range(n_samples):
            timestamp = start_time + timedelta(minutes=i*5)
            device = np.random.choice(devices)
            
            # Simulate different device types with different patterns
            if device.startswith("Device_0"):  # Temperature sensors
                base_temp = 20 + 10 * np.sin(i / 288.0)  # Daily pattern
                value = base_temp + np.random.normal(0, 2)
                metric = "temperature"
                unit = "°C"
            elif device.startswith("Device_1"):  # Pressure sensors
                base_pressure = 101.3 + 5 * np.sin(i / 144.0)  # 12-hour pattern
                value = base_pressure + np.random.normal(0, 1)
                metric = "pressure"
                unit = "kPa"
            elif device.startswith("Device_2"):  # Flow sensors
                value = np.random.gamma(2, 2) * (1 + 0.3 * np.sin(i / 72.0))  # 6-hour pattern
                metric = "flow_rate"
                unit = "L/min"
            else:  # Generic sensors
                value = np.random.normal(50, 10)
                metric = "generic"
                unit = "units"
            
            data.append({
                "timestamp": timestamp,
                "device_id": device,
                "metric": metric,
                "value": value,
                "unit": unit,
                "location": f"Location_{np.random.randint(1, 6)}"
            })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_manufacturing_data(n_batches: int = 1000) -> pd.DataFrame:
        """Generate manufacturing batch data"""
        data = []
        for i in range(n_batches):
            batch_id = f"B{i+1:06d}"
            product_line = np.random.choice(["Line_A", "Line_B", "Line_C"])
            
            # Process parameters with some correlation
            temperature = np.random.normal(85, 3)
            pressure = np.random.normal(100, 2)
            humidity = np.random.normal(45, 5)
            
            # Quality influenced by process parameters
            quality_factor = 1.0
            if abs(temperature - 85) > 5:
                quality_factor *= 0.95
            if abs(pressure - 100) > 3:
                quality_factor *= 0.97
            if abs(humidity - 45) > 10:
                quality_factor *= 0.98
            
            quality_score = np.clip(np.random.normal(0.95, 0.05) * quality_factor, 0, 1)
            defect_rate = 1.0 - quality_score
            
            data.append({
                "batch_id": batch_id,
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 720)),
                "product_line": product_line,
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity,
                "quality_score": quality_score,
                "defect_rate": defect_rate,
                "cycle_time": np.random.normal(5.2, 0.8),
                "energy_consumption": np.random.normal(12.5, 2.0)
            })
        
        return pd.DataFrame(data)


class DataAnalyzer:
    """Advanced data analysis capabilities"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
    
    def basic_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        stats = {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "numeric_summary": {}
        }
        
        for col in numeric_cols:
            stats["numeric_summary"][col] = {
                "count": int(self.data[col].count()),
                "mean": float(self.data[col].mean()),
                "std": float(self.data[col].std()),
                "min": float(self.data[col].min()),
                "25%": float(self.data[col].quantile(0.25)),
                "50%": float(self.data[col].median()),
                "75%": float(self.data[col].quantile(0.75)),
                "max": float(self.data[col].max())
            }
        
        return stats
    
    def correlation_analysis(self) -> Dict[str, Any]:
        """Perform correlation analysis"""
        numeric_data = self.data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            return {"error": "No numeric columns found"}
        
        correlation_matrix = numeric_data.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "variable1": correlation_matrix.columns[i],
                        "variable2": correlation_matrix.columns[j],
                        "correlation": float(corr_val)
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations
        }
    
    def clustering_analysis(self, features: List[str], n_clusters: int = 3) -> Dict[str, Any]:
        """Perform clustering analysis"""
        if not all(col in self.data.columns for col in features):
            return {"error": "Some features not found in data"}
        
        X = self.data[features].dropna()
        
        if len(X) < n_clusters:
            return {"error": "Not enough data points for clustering"}
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        
        # Analyze clusters
        cluster_analysis = {}
        for i in range(n_clusters):
            cluster_data = X[cluster_labels == i]
            cluster_analysis[f"cluster_{i}"] = {
                "size": len(cluster_data),
                "percentage": len(cluster_data) / len(X) * 100,
                "centroid": cluster_data.mean().to_dict()
            }
        
        return {
            "n_clusters": n_clusters,
            "silhouette_score": silhouette_avg,
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "cluster_analysis": cluster_analysis,
            "labels": cluster_labels.tolist()
        }
    
    def anomaly_detection(self, features: List[str], contamination: float = 0.1) -> Dict[str, Any]:
        """Detect anomalies using Isolation Forest"""
        if not all(col in self.data.columns for col in features):
            return {"error": "Some features not found in data"}
        
        X = self.data[features].dropna()
        
        if len(X) < 10:
            return {"error": "Not enough data for anomaly detection"}
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        # -1 indicates anomaly, 1 indicates normal
        anomalies = X[anomaly_labels == -1]
        normal_points = X[anomaly_labels == 1]
        
        return {
            "total_points": len(X),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(X),
            "anomaly_indices": X.index[anomaly_labels == -1].tolist(),
            "anomaly_summary": anomalies.describe().to_dict() if not anomalies.empty else {}
        }
    
    def time_series_analysis(self, timestamp_col: str, value_col: str) -> Dict[str, Any]:
        """Basic time series analysis"""
        if timestamp_col not in self.data.columns or value_col not in self.data.columns:
            return {"error": "Timestamp or value column not found"}
        
        # Convert timestamp to datetime if needed
        ts_data = self.data.copy()
        if not pd.api.types.is_datetime64_any_dtype(ts_data[timestamp_col]):
            ts_data[timestamp_col] = pd.to_datetime(ts_data[timestamp_col])
        
        # Sort by timestamp
        ts_data = ts_data.sort_values(timestamp_col)
        
        # Calculate basic time series statistics
        values = ts_data[value_col].dropna()
        
        # Trend analysis (simple linear regression on time)
        time_numeric = np.arange(len(values))
        trend_coef = np.polyfit(time_numeric, values, 1)[0]
        
        # Seasonality detection (simplified - check for periodic patterns)
        if len(values) > 24:  # Need enough data points
            # Simple autocorrelation for seasonality
            autocorr = [values.autocorr(lag=i) for i in range(1, min(25, len(values)//4))]
            significant_lags = [i+1 for i, corr in enumerate(autocorr) if abs(corr) > 0.3]
        else:
            significant_lags = []
        
        return {
            "start_time": ts_data[timestamp_col].min(),
            "end_time": ts_data[timestamp_col].max(),
            "total_observations": len(values),
            "trend_coefficient": trend_coef,
            "trend_direction": "increasing" if trend_coef > 0 else "decreasing" if trend_coef < 0 else "stable",
            "significant_seasonal_lags": significant_lags,
            "summary_stats": {
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max())
            }
        }


class BigDataProcessor:
    """Simulate big data processing capabilities"""
    
    def __init__(self):
        self.processed_data = {}
        self.performance_metrics = {}
    
    def process_streaming_data(self, data_stream: List[Dict], window_size: int = 100) -> Dict[str, Any]:
        """Process streaming data with sliding window"""
        if not data_stream:
            return {"error": "No data stream provided"}
        
        # Convert to DataFrame
        df = pd.DataFrame(data_stream)
        
        # Simulate processing metrics
        start_time = datetime.now()
        
        # Sliding window analysis
        window_results = []
        for i in range(0, len(df), window_size):
            window = df.iloc[i:i+window_size]
            
            if 'value' in window.columns:
                window_stats = {
                    "window_start": i,
                    "window_end": min(i + window_size, len(df)),
                    "mean": float(window['value'].mean()),
                    "std": float(window['value'].std()),
                    "min": float(window['value'].min()),
                    "max": float(window['value'].max()),
                    "count": len(window)
                }
                window_results.append(window_stats)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.performance_metrics["streaming_processing"] = {
            "processing_time_seconds": processing_time,
            "data_points_processed": len(df),
            "throughput_points_per_second": len(df) / processing_time if processing_time > 0 else 0
        }
        
        return {
            "total_windows": len(window_results),
            "window_analysis": window_results,
            "overall_stats": {
                "total_points": len(df),
                "overall_mean": float(df['value'].mean()) if 'value' in df.columns else None,
                "overall_std": float(df['value'].std()) if 'value' in df.columns else None
            }
        }
    
    def aggregate_analysis(self, data: pd.DataFrame, group_by: List[str], agg_functions: Dict[str, str]) -> Dict[str, Any]:
        """Perform aggregation analysis"""
        if not all(col in data.columns for col in group_by):
            return {"error": "Some group_by columns not found"}
        
        if not all(col in data.columns for col in agg_functions.keys()):
            return {"error": "Some aggregation columns not found"}
        
        start_time = datetime.now()
        
        # Perform aggregation
        try:
            grouped = data.groupby(group_by).agg(agg_functions)
            result = grouped.to_dict()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.performance_metrics["aggregation"] = {
                "processing_time_seconds": processing_time,
                "groups_created": len(grouped),
                "records_processed": len(data)
            }
            
            return {
                "aggregation_result": result,
                "group_count": len(grouped),
                "performance": self.performance_metrics["aggregation"]
            }
            
        except Exception as e:
            return {"error": f"Aggregation failed: {str(e)}"}
    
    def data_quality_assessment(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality metrics"""
        quality_report = {
            "total_records": len(data),
            "total_columns": len(data.columns),
            "completeness": {},
            "uniqueness": {},
            "consistency": {},
            "validity": {}
        }
        
        # Completeness analysis
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            quality_report["completeness"][col] = {
                "missing_count": int(missing_count),
                "missing_percentage": float(missing_count / len(data) * 100),
                "completeness_score": float((len(data) - missing_count) / len(data) * 100)
            }
        
        # Uniqueness analysis
        for col in data.columns:
            unique_count = data[col].nunique()
            quality_report["uniqueness"][col] = {
                "unique_count": int(unique_count),
                "unique_percentage": float(unique_count / len(data) * 100),
                "duplicate_count": int(len(data) - unique_count)
            }
        
        # Consistency checks (basic)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Check for negative values where inappropriate
            if col in ['temperature', 'pressure', 'flow_rate', 'quality_score']:
                negative_count = (data[col] < 0).sum()
                quality_report["consistency"][col] = {
                    "negative_values": int(negative_count),
                    "consistency_score": float((len(data) - negative_count) / len(data) * 100)
                }
        
        # Overall quality score
        completeness_scores = [v["completeness_score"] for v in quality_report["completeness"].values()]
        overall_quality = np.mean(completeness_scores) if completeness_scores else 0
        
        quality_report["overall_quality_score"] = overall_quality
        
        return quality_report


def create_visualization_data(analyzer: DataAnalyzer, analysis_type: str = "correlation") -> Dict[str, Any]:
    """Prepare data for visualizations"""
    numeric_data = analyzer.data.select_dtypes(include=[np.number])
    
    if analysis_type == "correlation":
        corr_matrix = numeric_data.corr()
        return {
            "type": "correlation_heatmap",
            "data": corr_matrix.round(3).to_dict(),
            "columns": corr_matrix.columns.tolist()
        }
    
    elif analysis_type == "distribution":
        dist_data = {}
        for col in numeric_data.columns:
            dist_data[col] = {
                "histogram": np.histogram(numeric_data[col].dropna(), bins=20),
                "boxplot": {
                    "min": float(numeric_data[col].min()),
                    "q1": float(numeric_data[col].quantile(0.25)),
                    "median": float(numeric_data[col].median()),
                    "q3": float(numeric_data[col].quantile(0.75)),
                    "max": float(numeric_data[col].max())
                }
            }
        return {
            "type": "distribution_analysis",
            "data": dist_data
        }
    
    elif analysis_type == "time_series":
        # Find timestamp columns
        timestamp_cols = analyzer.data.select_dtypes(include=['datetime64']).columns
        if len(timestamp_cols) > 0:
            ts_col = timestamp_cols[0]
            value_cols = numeric_data.columns
            
            ts_data = {}
            for col in value_cols:
                if col != ts_col:
                    ts_data[col] = {
                        "timestamps": analyzer.data[ts_col].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                        "values": analyzer.data[col].fillna(0).tolist()
                    }
            
            return {
                "type": "time_series",
                "data": ts_data,
                "timestamp_column": ts_col
            }
    
    return {"error": "Unknown analysis type or no data available"}
