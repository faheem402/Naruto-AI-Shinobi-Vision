import os
import csv
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# ==========================================
# SETTINGS
# ==========================================

DATASET_DIR = "dataset"
MODEL_FILE = "gesture_model.pkl"

GESTURES = [
    "tiger",
    "snake",
    "horse",
    "dragon",
    "ram",
    "bird"
]

# Two hands × 21 landmarks × 3 coordinates
EXPECTED_VALUES_PER_HAND = 63
EXPECTED_TOTAL_VALUES = 126


# ==========================================
# NORMALIZE ONE HAND
# ==========================================

def normalize_hand(values):
    """
    Convert 63 raw landmark values into
    position/scale normalized coordinates.
    """

    landmarks = np.array(values).reshape(21, 3)

    # Wrist = landmark 0
    wrist = landmarks[0].copy()

    # Move wrist to origin
    landmarks = landmarks - wrist

    # Calculate hand size using the
    # largest distance from wrist
    distances = np.linalg.norm(
        landmarks,
        axis=1
    )

    scale = np.max(distances)

    # Prevent division by zero
    if scale < 0.0001:
        scale = 1.0

    landmarks = landmarks / scale

    return landmarks.flatten()


# ==========================================
# NORMALIZE TWO HANDS
# ==========================================

def normalize_sample(values):

    left_hand = values[:63]
    right_hand = values[63:126]

    left_normalized = normalize_hand(
        left_hand
    )

    right_normalized = normalize_hand(
        right_hand
    )

    return np.concatenate([
        left_normalized,
        right_normalized
    ])


# ==========================================
# LOAD DATA
# ==========================================

X = []
y = []

print()
print("🥷 SHINOBI VISION - NORMALIZED TRAINING")
print("=======================================")
print()

for gesture in GESTURES:

    folder = os.path.join(
        DATASET_DIR,
        gesture
    )

    files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv")
    ]

    valid_count = 0
    bad_count = 0

    for filename in files:

        filepath = os.path.join(
            folder,
            filename
        )

        try:

            with open(
                filepath,
                "r"
            ) as file:

                reader = csv.reader(file)
                row = next(reader)

            values = [
                float(v)
                for v in row
            ]

            # Make sure this is a
            # two-hand sample
            if len(values) != EXPECTED_TOTAL_VALUES:

                print(
                    f"⚠ Skipping invalid file: "
                    f"{gesture}/{filename}"
                )

                print(
                    f"  Expected {EXPECTED_TOTAL_VALUES}, "
                    f"got {len(values)}"
                )

                bad_count += 1
                continue

            normalized = normalize_sample(
                values
            )

            X.append(normalized)
            y.append(gesture)

            valid_count += 1

        except Exception as e:

            print(
                f"⚠ Could not read: "
                f"{gesture}/{filename}"
            )

            print(f"  Error: {e}")

            bad_count += 1

    print(
        f"{gesture.upper():8} → "
        f"{valid_count} valid samples"
    )

    if bad_count:

        print(
            f"           "
            f"{bad_count} invalid skipped"
        )


# ==========================================
# NUMPY ARRAYS
# ==========================================

X = np.array(
    X,
    dtype=np.float32
)

y = np.array(y)

print()
print(
    f"Total valid samples: {len(X)}"
)

print(
    f"Features per sample: {X.shape[1]}"
)

print()


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42,

    stratify=y
)


print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples:  {len(X_test)}"
)

print()


# ==========================================
# TRAIN RANDOM FOREST
# ==========================================

print("Training normalized AI...")

model = RandomForestClassifier(

    n_estimators=200,

    max_depth=None,

    random_state=42,

    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)


# ==========================================
# EVALUATION
# ==========================================

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print()
print("=======================================")

print(
    f"Normalized accuracy: "
    f"{accuracy * 100:.2f}%"
)

print("=======================================")

print()

print(
    classification_report(
        y_test,
        predictions
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_FILE
)

print()
print(
    f"✓ Normalized model saved as: "
    f"{MODEL_FILE}"
)

print()