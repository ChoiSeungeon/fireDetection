import base64
import json
import time
from datetime import datetime
from pathlib import Path

import cv2
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
TOPIC = "fire-frames"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
VIDEO_PATH = PROJECT_ROOT / "test_videos" / "test_fire.mp4"
FRAME_INTERVAL = 10
frame_index = 0

CAMERA_ID = "cam_test"
LOCATION = {"latitude": 37.12345, "longitude": 127.56789}

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

cap = cv2.VideoCapture(str(VIDEO_PATH))
if not cap.isOpened():
    print("영상 파일을 열 수 없습니다.")
    exit()

print("🎥 영상 전송 시작...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("영상 전송 완료")
        break

    if frame_index % FRAME_INTERVAL == 0:
        _, buffer = cv2.imencode(".jpg", frame)
        jpg_base64 = base64.b64encode(buffer).decode("utf-8")

        message = {
            "timestamp": datetime.now().isoformat(),
            "camera_id": CAMERA_ID,
            "location": LOCATION,
            "frame": jpg_base64,
            "sent_timestamp": time.time(),
        }

        producer.send(TOPIC, value=message)
        print(f"전송 + 저장 완료: frame_{frame_index:04d}.jpg")

    frame_index += 1

cap.release()
producer.flush()
