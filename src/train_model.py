import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/processed/dataset_part_3.csv")
y = pd.read_csv("data/processed/dataset_part_2.csv")['Class']

X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)

# salvar dados para o evaluation nb
os.makedirs("data/interim", exist_ok=True)
X_test.to_csv("data/interim/X_test.csv", index=False)
y_test.to_csv("data/interim/y_test.csv", index=False)

os.makedirs("models", exist_ok=True)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, "models/scaler.pkl")

# Logistic Regression
logreg = LogisticRegression()
logreg.fit(X_train_scaled, y_train)
joblib.dump(logreg, "models/logreg_model.pkl")

# SVM
svm = SVC()
svm.fit(X_train_scaled, y_train)
joblib.dump(svm, "models/svm_model.pkl")

# KNN
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
joblib.dump(knn, "models/knn_model.pkl")

# Decision Tree
tree = DecisionTreeClassifier()
tree.fit(X_train_scaled, y_train)
joblib.dump(tree, "models/tree_model.pkl")

print("Modelos Treinados e Salvos")