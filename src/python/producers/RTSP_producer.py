# producer.py

import cv2
import base64
import json
import time
from datetime import datetime
from kafka import KafkaProducer

# Kafka 설정
KAFKA_BROKER = 'localhost:9092'
TOPIC = 'fire-frames'

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# RTSP 스트림 주소
RTSP_URL = 'rtsp://<user>:<pass>@<ip>:<port>/stream'
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("RTSP 연결 실패")
    exit()

print("RTSP 프레임 전송 시작...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # JPG 인코딩 및 base64 변환
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_base64 = base64.b64encode(buffer).decode('utf-8')

    # 메시지 구성 (카메라 GPS 포함)
    message = {
        "timestamp": datetime.now().isoformat(),
        "camera_id": "cam01",
        "location": {
            "latitude": 37.12345,
            "longitude": 127.45678
        },
        "frame": jpg_base64
    }

    producer.send(TOPIC, value=message)
    print(f"[{message['timestamp']}] 프레임 전송 완료")

    time.sleep(0.2)

cap.release()
