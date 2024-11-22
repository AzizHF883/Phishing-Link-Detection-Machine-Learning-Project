import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import pickle
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
data = pd.read_csv("input_test.csv")

# Drop the URL column if it exists
if 'URL' in data.columns:
    data = data.drop(columns=['URL'])

# Define features (X) and target (y)
X = data.drop(columns=['Status'])
y = data['Status']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# List of models to train
models = {
    "Random Forest": RandomForestClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "XGBoost": XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
    "AdaBoost": AdaBoostClassifier(random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42)
}

# Train, evaluate, and save each model
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{name} Accuracy: {accuracy:.4f}")
    print(
        f"{name} Classification Report:\n{classification_report(y_test, y_pred, target_names=['General URL', 'Phishing URL'])}")

    # Save the trained model
    with open(f"{name.replace(' ', '_')}_model.pkl", "wb") as file:
        pickle.dump(model, file)
    print(f"{name} model saved as {name.replace(' ', '_')}_model.pkl\n")
