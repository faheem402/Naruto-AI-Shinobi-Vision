import cv2
import mediapipe as mp
import csv
import os
import time


# ==========================================
# SETTINGS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "dataset"
    )
)

SAMPLES_TO_CAPTURE = 40


GESTURES = {
    "1": "tiger",
    "2": "snake",
    "3": "horse",
    "4": "dragon",
    "5": "ram",
    "6": "bird"
}


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
    min_tracking_confidence=0.6
)


detector = HandLandmarker.create_from_options(
    options
)


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Could not open webcam.")
    exit()


# ==========================================
# MAIN MENU
# ==========================================

print()
print("🥷 SHINOBI VISION DATA COLLECTOR")
print("================================")
print()
print("Choose a gesture:")
print()
print("1 → Tiger")
print("2 → Snake")
print("3 → Horse")
print("4 → Dragon")
print("5 → Ram")
print("6 → Bird")
print()
print("Q → Quit")
print()


while True:

    key = input(
        "Enter gesture number: "
    ).strip().lower()

    if key == "q":
        break

    if key not in GESTURES:

        print("Invalid choice.")
        continue


    gesture = GESTURES[key]

    folder = os.path.join(
        DATASET_DIR,
        gesture
    )

    os.makedirs(
        folder,
        exist_ok=True
    )


    # ======================================
    # COUNT EXISTING FILES
    # ======================================

    existing_files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv")
    ]

    print()
    print(
        f"Selected: {gesture.upper()}"
    )

    print(
        f"Existing samples: "
        f"{len(existing_files)}"
    )

    print(
        f"New samples: "
        f"{SAMPLES_TO_CAPTURE}"
    )

    print()


    # ======================================
    # COUNTDOWN
    # ======================================

    print("Get ready...")

    for number in [3, 2, 1]:

        print(number)

        time.sleep(1)


    print()
    print(
        f"CAPTURING {SAMPLES_TO_CAPTURE} "
        f"{gesture.upper()} SAMPLES"
    )

    print()


    captured = 0


    # ======================================
    # CAPTURE
    # ======================================

    while captured < SAMPLES_TO_CAPTURE:

        success, frame = cap.read()

        if not success:
            continue

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


        # ==================================
        # DRAW HANDS
        # ==================================

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


        # ==================================
        # REQUIRE TWO HANDS
        # ==================================

        if len(hands) >= 2:

            # Sort hands consistently
            hands_sorted = sorted(
                hands[:2],
                key=lambda hand: hand[0].x
            )

            left_hand = hands_sorted[0]
            right_hand = hands_sorted[1]


            # ==============================
            # LANDMARK FEATURES
            # ==============================

            features = []

            for hand in [
                left_hand,
                right_hand
            ]:

                for landmark in hand:

                    features.extend([
                        landmark.x,
                        landmark.y,
                        landmark.z
                    ])


            # ==============================
            # SAVE SAMPLE
            # ==============================

            filename = (
                f"sample_"
                f"{int(time.time() * 1000)}"
                f"_{captured}.csv"
            )

            filepath = os.path.join(
                folder,
                filename
            )

            with open(
                filepath,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(
                    file
                )

                writer.writerow(
                    features
                )


            captured += 1


        # ==================================
        # UI
        # ==================================

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 80),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            f"CAPTURING: {gesture.upper()}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{captured}/{SAMPLES_TO_CAPTURE}",
            (20, 62),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        cv2.imshow(
            "Shinobi Vision - Data Collection",
            frame
        )


        # ==================================
        # ESCAPE
        # ==================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            print()
            print("Capture cancelled.")
            break


    print()

    if captured == SAMPLES_TO_CAPTURE:

        print(
            f"✓ {captured} {gesture.upper()} "
            f"samples captured!"
        )

    print()


# ==========================================
# CLEANUP
# ==========================================

cap.release()

detector.close()

cv2.destroyAllWindows()

print("Collector stopped.")