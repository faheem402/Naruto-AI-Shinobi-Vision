import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
from collections import deque, Counter


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "gesture_model.pkl"
    )
)

MODEL = joblib.load(MODEL_PATH)

print("🥷 Shinobi Vision AI loaded!")
print("Classes:", MODEL.classes_)


# ==========================================
# NORMALIZATION
# ==========================================

def normalize_hand(hand):

    landmarks = np.array(
        [
            [lm.x, lm.y, lm.z]
            for lm in hand
        ],
        dtype=np.float32
    )

    # Wrist = landmark 0
    wrist = landmarks[0].copy()

    # Move wrist to origin
    landmarks = landmarks - wrist

    # Normalize hand size
    distances = np.linalg.norm(
        landmarks,
        axis=1
    )

    scale = np.max(distances)

    if scale < 0.0001:
        scale = 1.0

    landmarks = landmarks / scale

    return landmarks.flatten()


def create_features(left_hand, right_hand):

    left_features = normalize_hand(
        left_hand
    )

    right_features = normalize_hand(
        right_hand
    )

    features = np.concatenate([
        left_features,
        right_features
    ])

    return features.reshape(1, -1)


# ==========================================
# MEDIAPIPE
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=os.path.join(
            BASE_DIR,
            "hand_landmarker.task"
        )
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6,
)

detector = HandLandmarker.create_from_options(
    options
)


# ==========================================
# PREDICTION SETTINGS
# ==========================================

prediction_history = deque(
    maxlen=7
)

CONFIDENCE_THRESHOLD = 0.55


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Could not open webcam.")
    exit()

print()
print("Camera started.")
print("Show both hands.")
print("Press Q to quit.")
print()


# ==========================================
# HAND CONNECTIONS
# ==========================================

connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = cap.read()

    if not success:
        print("Could not read camera.")
        break

    frame = cv2.flip(
        frame,
        1
    )

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = detector.detect(
        mp_image
    )

    hands = result.hand_landmarks


    # ======================================
    # DRAW HANDS
    # ======================================

    if hands:

        for hand in hands:

            for landmark in hand:

                x = int(
                    landmark.x *
                    frame.shape[1]
                )

                y = int(
                    landmark.y *
                    frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

            for start, end in connections:

                x1 = int(
                    hand[start].x *
                    frame.shape[1]
                )

                y1 = int(
                    hand[start].y *
                    frame.shape[0]
                )

                x2 = int(
                    hand[end].x *
                    frame.shape[1]
                )

                y2 = int(
                    hand[end].y *
                    frame.shape[0]
                )

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


    # ======================================
    # TWO HAND RECOGNITION
    # ======================================

    if len(hands) >= 2:

        # Sort by wrist X position
        hands_sorted = sorted(
            hands[:2],
            key=lambda hand: hand[0].x
        )

        left_hand = hands_sorted[0]
        right_hand = hands_sorted[1]


        # ==================================
        # FEATURES
        # ==================================

        features = create_features(
            left_hand,
            right_hand
        )


        # ==================================
        # PREDICTION
        # ==================================

        probabilities = MODEL.predict_proba(
            features
        )[0]

        best_index = np.argmax(
            probabilities
        )

        prediction = MODEL.classes_[
            best_index
        ]

        confidence = probabilities[
            best_index
        ]


        # ==================================
        # SMOOTHING
        # ==================================

        if confidence >= CONFIDENCE_THRESHOLD:

            prediction_history.append(
                prediction
            )

        if prediction_history:

            stable_prediction = Counter(
                prediction_history
            ).most_common(1)[0][0]

        else:

            stable_prediction = "UNKNOWN"


        # ==================================
        # TOP BAR
        # ==================================

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 75),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            "SHINOBI VISION AI",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "DIAGNOSTIC MODE",
            (20, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


        # ==================================
        # MAIN PREDICTION
        # ==================================

        cv2.rectangle(
            frame,
            (10, 90),
            (430, 190),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            "CURRENT SIGN",
            (25, 118),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            stable_prediction.upper(),
            (25, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 255),
            3
        )


        # ==================================
        # PROBABILITY PANEL
        # ==================================

        panel_x = 10
        panel_y = 205

        panel_width = 430
        panel_height = 260

        cv2.rectangle(
            frame,
            (
                panel_x,
                panel_y
            ),
            (
                panel_x + panel_width,
                panel_y + panel_height
            ),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            "AI PROBABILITIES",
            (
                panel_x + 15,
                panel_y + 28
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )


        # ==================================
        # EACH CLASS
        # ==================================

        for i, class_name in enumerate(
            MODEL.classes_
        ):

            probability = probabilities[i]

            percentage = probability * 100

            y = (
                panel_y
                + 55
                + i * 32
            )

            # Name
            cv2.putText(
                frame,
                class_name.upper(),
                (
                    panel_x + 15,
                    y
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1
            )

            # Percentage
            cv2.putText(
                frame,
                f"{percentage:5.1f}%",
                (
                    panel_x + 105,
                    y
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1
            )

            # Bar background
            bar_x = panel_x + 180
            bar_y = y - 12

            bar_width = 220
            bar_height = 12

            cv2.rectangle(
                frame,
                (
                    bar_x,
                    bar_y
                ),
                (
                    bar_x + bar_width,
                    bar_y + bar_height
                ),
                (60, 60, 60),
                -1
            )

            # Bar value
            filled_width = int(
                bar_width * probability
            )

            if filled_width > 0:

                cv2.rectangle(
                    frame,
                    (
                        bar_x,
                        bar_y
                    ),
                    (
                        bar_x + filled_width,
                        bar_y + bar_height
                    ),
                    (0, 255, 0),
                    -1
                )


        # ==================================
        # LIVE CONFIDENCE
        # ==================================

        cv2.putText(
            frame,
            f"Winner confidence: "
            f"{confidence * 100:.1f}%",
            (
                20,
                frame.shape[0] - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2
        )


    else:

        prediction_history.clear()

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 75),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            "SHINOBI VISION AI",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "SHOW BOTH HANDS",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # ======================================
    # SHOW
    # ======================================

    cv2.imshow(
        "Shinobi Vision - Diagnostic",
        frame
    )


    # ======================================
    # QUIT
    # ======================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# ==========================================
# CLEANUP
# ==========================================

cap.release()

detector.close()

cv2.destroyAllWindows()

print("Shinobi Vision stopped.")