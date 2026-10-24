import cv2
import mediapipe as mp

# Current MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Hand tracking configuration
options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6,
)

# Create hand detector
detector = HandLandmarker.create_from_options(options)

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

print("🥷 Shinobi Vision started!")
print("Show your hand to the camera.")
print("Press Q to quit.")

while True:
    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read webcam frame.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # OpenCV uses BGR, MediaPipe expects RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Detect hands
    result = detector.detect(mp_image)

    # Draw landmarks
    if result.hand_landmarks:
        for hand in result.hand_landmarks:

            for landmark in hand:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

            # Draw connections
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (0, 9), (9, 10), (10, 11), (11, 12),
                (0, 13), (13, 14), (14, 15), (15, 16),
                (0, 17), (17, 18), (18, 19), (19, 20),
                (5, 9), (9, 13), (13, 17)
            ]

            for start, end in connections:
                x1 = int(hand[start].x * frame.shape[1])
                y1 = int(hand[start].y * frame.shape[0])

                x2 = int(hand[end].x * frame.shape[1])
                y2 = int(hand[end].y * frame.shape[0])

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

    cv2.imshow("Shinobi Vision - Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
detector.close()
cv2.destroyAllWindows()