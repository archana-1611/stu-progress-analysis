import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("training_dataset.csv")

# Encode labels
le = LabelEncoder()
df["final_label"] = le.fit_transform(df["final_label"])

X = df[["attendance", "internal_marks", "assignment_score"]]
y = df["final_label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train models
dt_model = DecisionTreeClassifier()
nb_model = GaussianNB()

dt_model.fit(X_train, y_train)
nb_model.fit(X_train, y_train)

# Evaluate
dt_acc = accuracy_score(y_test, dt_model.predict(X_test))
nb_acc = accuracy_score(y_test, nb_model.predict(X_test))

print("Decision Tree Accuracy:", dt_acc)
print("Naive Bayes Accuracy:", nb_acc)

# Save best model
best_model = dt_model if dt_acc >= nb_acc else nb_model

joblib.dump(best_model, "student_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Model trained & saved successfully")