import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)
from xgboost import XGBClassifier
import joblib
import os
import numpy as np

if __name__ == '__main__':
    # Load features
    try:
        features_df = pd.read_csv('../data/features.csv')
    except FileNotFoundError:
        print("Error: 'data/features.csv' not found. Run 'extract_features.py' first.")
        exit()

    print(f"Loaded {len(features_df)} records.")

    # ── Handle missing values (-1 from failed WHOIS/SSL lookups) ──────────────
    features_df.replace(-1, np.nan, inplace=True)
    features_df.fillna(features_df.median(), inplace=True)

    X = features_df.drop('label', axis=1)
    y = features_df['label']
    feature_names = list(X.columns)

    print(f"Class distribution:\n{y.value_counts()}\n")

    # ── Train/Test Split ───────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Define Models ──────────────────────────────────────────────────────────
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    xgb = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    )

    # Stacking: RF + XGB → Logistic Regression as meta-learner
    stacking_model = StackingClassifier(
        estimators=[('rf', rf), ('xgb', xgb)],
        final_estimator=LogisticRegression(),
        cv=5,
        n_jobs=-1
    )

    # ── Train & Evaluate All Three ─────────────────────────────────────────────
    models = {
        'RandomForest': rf,
        'XGBoost': xgb,
        'Stacking (RF+XGB)': stacking_model
    }

    results = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        results[name] = {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
        }

        print(f"\n── {name} ──")
        print(f"  Accuracy:  {results[name]['accuracy']:.4f}")
        print(f"  Precision: {results[name]['precision']:.4f}")
        print(f"  Recall:    {results[name]['recall']:.4f}")
        print(f"  F1-Score:  {results[name]['f1']:.4f}")
        print(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

    # ── Pick Best Model by F1 ──────────────────────────────────────────────────
    best_name = max(results, key=lambda k: results[k]['f1'])
    best_model = results[best_name]['model']
    print(f"\nBest model: {best_name} (F1: {results[best_name]['f1']:.4f})")

    # ── Cross-validation on best model ────────────────────────────────────────
    print(f"\nRunning 5-fold cross-validation on {best_name}...")
    cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='f1', n_jobs=-1)
    print(f"CV F1 scores: {cv_scores}")
    print(f"Mean CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # ── Feature Importance (RF or XGB only) ───────────────────────────────────
    if best_name in ['RandomForest', 'XGBoost']:
        importances = best_model.feature_importances_
        feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        print(f"\nTop 10 Features:")
        for feat, imp in feat_imp[:10]:
            print(f"  {feat}: {imp:.4f}")

    # ── Save ───────────────────────────────────────────────────────────────────
    models_dir = '../models'
    os.makedirs(models_dir, exist_ok=True)

    joblib.dump(best_model, os.path.join(models_dir, 'phishguard_model.joblib'))
    joblib.dump(feature_names, os.path.join(models_dir, 'feature_names.joblib'))

    # Save all results for reference
    summary = {k: {m: v for m, v in r.items() if m != 'model'} for k, r in results.items()}
    joblib.dump(summary, os.path.join(models_dir, 'training_summary.joblib'))

    print(f"\nSaved best model ({best_name}) to '{models_dir}/'")