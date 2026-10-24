from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
from collections import deque, Counter
import threading


app = Flask(__name__)


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "gesture_model.pkl"
)

LANDMARK_MODEL = os.path.join(
    BASE_DIR,
    "backend",
    "hand_landmarker.task"
)


# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load(MODEL_PATH)

print("🥷 SHINOBI VISION")
print("=================")
print("AI model loaded.")
print("Classes:", model.classes_)


# ==========================================
# MEDIAPIPE
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=LANDMARK_MODEL
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

detector = HandLandmarker.create_from_options(
    options
)


# ==========================================
# CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

camera.set(cv2.CAP_PROP_FPS, 30)

# Reduce camera buffering
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)


if not camera.isOpened():

    print("ERROR: Could not open webcam.")


# ==========================================
# STATE
# ==========================================

state_lock = threading.Lock()

current_prediction = "WAITING"

current_confidence = 0.0

current_hands = []

probabilities = {
    gesture: 0.0
    for gesture in model.classes_
}

prediction_history = deque(
    maxlen=5
)


# ==========================================
# NORMALIZE HAND
# ==========================================

def normalize_hand(hand):

    landmarks = np.array(
        [
            [lm.x, lm.y, lm.z]
            for lm in hand
        ],
        dtype=np.float32
    )

    wrist = landmarks[0].copy()

    landmarks = landmarks - wrist

    distances = np.linalg.norm(
        landmarks,
        axis=1
    )

    scale = np.max(distances)

    if scale < 0.0001:
        scale = 1.0

    landmarks = landmarks / scale

    return landmarks.flatten()


# ==========================================
# FEATURES
# ==========================================

def create_features(left_hand, right_hand):

    left = normalize_hand(left_hand)

    right = normalize_hand(right_hand)

    features = np.concatenate([
        left,
        right
    ])

    print("🟢 TWO HANDS DETECTED")
    print("Feature shape:", features.shape)

    return features.reshape(1, -1)


# ==========================================
# HAND CONNECTIONS
# ==========================================

connections = [

    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (0, 9), (9, 10), (10, 11), (11, 12),

    (0, 13), (13, 14), (14, 15), (15, 16),

    (0, 17), (17, 18), (18, 19), (19, 20),

    (5, 9),
    (9, 13),
    (13, 17)
]


# ==========================================
# CAMERA STREAM
# ==========================================

def generate_frames():

    global current_prediction
    global current_confidence
    global probabilities
    global current_hands

    frame_count = 0

    while True:

        success, frame = camera.read()

        if not success:
            continue


        frame_count += 1


        # Mirror camera
        frame = cv2.flip(frame, 1)


        # ==================================
        # PROCESS EVERY 2ND FRAME
        # ==================================

        should_process = (
            frame_count % 2 == 0
        )


        if should_process:

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

            print("HANDS DETECTED:", len(hands))


            # ==================================
            # TWO HANDS
            # ==================================

            if len(hands) >= 2:

                hands_sorted = sorted(
                    hands[:2],
                    key=lambda hand: hand[0].x
                )

                left_hand = hands_sorted[0]

                right_hand = hands_sorted[1]

                current_hands = [
                    {
                        "x": float(hand[0].x),
                        "y": float(hand[0].y)
                    }
                    for hand in hands_sorted
                ]


                features = create_features(
                    left_hand,
                    right_hand
                )


                probs = model.predict_proba(
                    features
                )[0]

                print("🤖 AI PREDICTED:", model.classes_[np.argmax(probs[0])])
                print("📊 CONFIDENCE:", float(np.max(probs[0])))


                best_index = np.argmax(probs)

                prediction = model.classes_[
                    best_index
                ]

                confidence = float(
                    probs[best_index]
                )


                # ==================================
                # SMOOTHING
                # ==================================

                if confidence >= 0.50:

                    prediction_history.append(
                        prediction
                    )


                if prediction_history:

                    stable_prediction = Counter(
                        prediction_history
                    ).most_common(1)[0][0]

                else:

                    stable_prediction = "UNKNOWN"


                with state_lock:

                    current_prediction = (
                        stable_prediction
                    )

                    current_confidence = (
                        confidence
                    )

                    probabilities = {
                        model.classes_[i]:
                        float(probs[i])

                        for i in range(
                            len(model.classes_)
                        )
                    }


            else:

                prediction_history.clear()

                with state_lock:

                    current_prediction = (
                        "SHOW BOTH HANDS"
                    )

                    current_confidence = 0.0

                    current_hands = []

                    probabilities = {
                        gesture: 0.0
                        for gesture in model.classes_
                    }


        # ==================================
        # DRAW LANDMARKS
        # ==================================

        # We still run detection only every
        # second frame, so this remains light.

        if should_process and len(hands) >= 2:

            for hand in hands[:2]:

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
                        3,
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
                        1
                    )


        # ==================================
        # SMALL STATUS OVERLAY
        # ==================================

        with state_lock:

            display_prediction = (
                current_prediction
            )

            display_confidence = (
                current_confidence
            )


        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 55),
            (15, 15, 15),
            -1
        )

        cv2.putText(
            frame,
            display_prediction.upper(),
            (15, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{display_confidence * 100:.0f}%",
            (15, 47),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 220, 180),
            1
        )


        # ==================================
        # JPEG
        # ==================================

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                70
            ]
        )

        if not success:
            continue


        frame_bytes = buffer.tobytes()


        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )


@app.route("/status")
def status():

    with state_lock:

        return jsonify({
            "prediction":
                current_prediction,

            "confidence":
                current_confidence,

            "probabilities":
                probabilities,

            "hands":
                current_hands
        })


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    print()
    print(
        "Open:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )