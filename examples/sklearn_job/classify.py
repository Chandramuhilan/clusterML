"""Simple sklearn classification example for ClusterML."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-estimators", type=int, default=100)
    args = parser.parse_args()

    print(f"Training RandomForest with n_estimators={args.n_estimators}")

    X, y = load_iris(return_X_y=True)
    clf = RandomForestClassifier(n_estimators=args.n_estimators, random_state=42)

    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"Cross-validation scores: {scores}")
    print(f"Mean accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")

    # Final fit
    clf.fit(X, y)

    result = {
        "model": "RandomForestClassifier",
        "n_estimators": args.n_estimators,
        "cv_mean_accuracy": round(scores.mean(), 4),
        "cv_std": round(scores.std(), 4),
    }
    print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
