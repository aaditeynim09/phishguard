import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

if __name__ == '__main__':
    # Load the features dataset
    try:
        features_df = pd.read_csv('../data/features.csv')
    except FileNotFoundError:
        print("Error: 'data/features.csv' not found. Run 'extract_features.py' first.")
        exit()

    print(f"Loaded {len(features_df)} records from 'data/features.csv'.")

    # Separate features (X) and labels (y)
    X = features_df.drop('label', axis=1)
    y = features_df['label']
    
    # Save feature names for later use in the API
    feature_names = list(X.columns)

    # Split the data into training and testing sets (80/20 split)
    # Using stratify to ensure the same proportion of labels in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")

    # Initialize and train the RandomForestClassifier
    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("Model training complete.")

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model's performance
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\nModel Evaluation:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    # Ensure the models directory exists
    models_dir = '../models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    # Save the trained model and the feature names
    model_path = os.path.join(models_dir, 'phishguard_model.joblib')
    features_path = os.path.join(models_dir, 'feature_names.joblib')

    joblib.dump(model, model_path)
    joblib.dump(feature_names, features_path)

    print(f"\nModel saved to '{model_path}'")
    print(f"Feature names saved to '{features_path}'")
