from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, make_classification, load_wine
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns


def get_iris_data():
    iris = load_iris()
    X = iris.data
    y = iris.target
    return X, y, iris.feature_names, iris.target_names


def get_wine_data():
    wine = load_wine()
    X = wine.data
    y = wine.target
    return X, y, wine.feature_names, wine.target_names


def generate_synthetic_data(n_samples=1000, n_features=10, n_classes=3, random_state=42):
    X, y = make_classification(
        n_samples=n_samples, 
        n_features=n_features, 
        n_informative=n_features-2, 
        n_redundant=1, 
        n_classes=n_classes, 
        random_state=random_state
    )
    feature_names = [f"feature_{i}" for i in range(n_features)]
    target_names = [f"class_{i}" for i in range(n_classes)]
    return X, y, feature_names, target_names


def build_model(model_name: str) -> Pipeline:
    if model_name == "Random Forest":
        clf = RandomForestClassifier(n_estimators=200, random_state=42)
    elif model_name == "Gradient Boosting":
        clf = GradientBoostingClassifier(n_estimators=200, random_state=42)
    elif model_name == "AdaBoost":
        clf = AdaBoostClassifier(n_estimators=200, random_state=42)
    elif model_name == "SVM":
        clf = SVC(kernel='rbf', probability=True, random_state=42)
    elif model_name == "Neural Network":
        clf = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
    else:
        clf = LogisticRegression(max_iter=500)
    pipe = make_pipeline(StandardScaler(), clf)
    return pipe


def train_iris_model(model_name: str = "Logistic Regression", test_size: float = 0.2, random_state: int = 42, dataset: str = "iris"):
    if dataset == "iris":
        X, y, feature_names, target_names = get_iris_data()
    elif dataset == "wine":
        X, y, feature_names, target_names = get_wine_data()
    else:
        X, y, feature_names, target_names = generate_synthetic_data(random_state=random_state)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    model = build_model(model_name)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
    
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=target_names, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    # Cross-validation scores
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    
    # Feature importance (if available)
    feature_importance = None
    if hasattr(model.steps[-1][1], 'feature_importances_'):
        feature_importance = model.steps[-1][1].feature_importances_
    
    metrics = {
        "accuracy": acc, 
        "classification_report": report, 
        "target_names": target_names,
        "confusion_matrix": cm,
        "cv_scores": cv_scores,
        "cv_mean": cv_scores.mean(),
        "cv_std": cv_scores.std(),
        "feature_importance": feature_importance,
        "feature_names": feature_names
    }
    return model, metrics


def predict_iris(model: Pipeline, features: np.ndarray):
    if features.ndim == 1:
        features = features.reshape(1, -1)
    pred_idx = int(model.predict(features)[0])
    # Extract classes from the final estimator in the pipeline
    final_estimator = model.steps[-1][1]
    classes = final_estimator.classes_
    proba = model.predict_proba(features)[0]
    # Map probabilities to class indices
    label_probs = {int(cls): float(prob) for cls, prob in zip(classes, proba)}
    return pred_idx, label_probs


def perform_clustering(X: np.ndarray, algorithm: str = "kmeans", n_clusters: int = 3):
    """Perform clustering analysis"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if algorithm == "kmeans":
        clusterer = KMeans(n_clusters=n_clusters, random_state=42)
    elif algorithm == "dbscan":
        clusterer = DBSCAN(eps=0.5, min_samples=5)
    else:
        raise ValueError(f"Unknown clustering algorithm: {algorithm}")
    
    cluster_labels = clusterer.fit_predict(X_scaled)
    return cluster_labels, clusterer


def perform_dimensionality_reduction(X: np.ndarray, method: str = "pca", n_components: int = 2):
    """Perform dimensionality reduction for visualization"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if method == "pca":
        reducer = PCA(n_components=n_components, random_state=42)
    elif method == "tsne":
        reducer = TSNE(n_components=n_components, random_state=42)
    else:
        raise ValueError(f"Unknown reduction method: {method}")
    
    X_reduced = reducer.fit_transform(X_scaled)
    return X_reduced, reducer


def hyperparameter_tuning(model_name: str, X: np.ndarray, y: np.ndarray):
    """Perform hyperparameter tuning using GridSearchCV"""
    model = build_model(model_name)
    
    param_grids = {
        "Random Forest": {
            'randomforestclassifier__n_estimators': [50, 100, 200],
            'randomforestclassifier__max_depth': [None, 10, 20],
            'randomforestclassifier__min_samples_split': [2, 5, 10]
        },
        "SVM": {
            'svc__C': [0.1, 1, 10],
            'svc__gamma': ['scale', 'auto'],
            'svc__kernel': ['rbf', 'linear']
        },
        "Neural Network": {
            'mlpclassifier__hidden_layer_sizes': [(50,), (100,), (100, 50)],
            'mlpclassifier__alpha': [0.0001, 0.001, 0.01],
            'mlpclassifier__learning_rate': ['constant', 'adaptive']
        }
    }
    
    param_grid = param_grids.get(model_name, {})
    if not param_grid:
        return model, {}
    
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X, y)
    
    return grid_search.best_estimator_, grid_search.best_params_
