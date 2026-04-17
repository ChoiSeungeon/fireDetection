import base64
import json
from datetime import datetime
from pathlib import Path

import cv2
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
TOPIC = "fire-frames"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGE_PATH = PROJECT_ROOT / "test_images" / "test_fire.jpg"

CAMERA_ID = "cam_test"
LOCATION = {"latitude": 37.12345, "longitude": 127.56789}

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

image = cv2.imread(str(IMAGE_PATH))
if image is None:
    print(f"이미지 파일을 열 수 없습니다: {IMAGE_PATH}")
    exit()

_, buffer = cv2.imencode(".jpg", image)
jpg_base64 = base64.b64encode(buffer).decode("utf-8")

message = {
    "timestamp": datetime.now().isoformat(),
    "camera_id": CAMERA_ID,
    "location": LOCATION,
    "frame": jpg_base64,
}

producer.send(TOPIC, value=message)
producer.flush()

print("🖼️ 이미지 1장 전송 완료!")

