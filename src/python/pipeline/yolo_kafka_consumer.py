import base64
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import torch
from kafka import KafkaConsumer, KafkaProducer

from yolo_utils import letterbox, non_max_suppression, scale_coords

PROJECT_ROOT = Path(__file__).resolve().parents[3]
YOLO_ROOT = PROJECT_ROOT / "yolov5"
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"
ANNOTATED_DIR = PROJECT_ROOT / "consumer_annotated_frames"

os.makedirs(ANNOTATED_DIR, exist_ok=True)

KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "fire-frames"
OUTPUT_TOPIC = "fire-results"

frame_index = 0

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="fire-group",
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

last_sent_time = {"fire": None, "smoke": None}

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = torch.hub.load(str(YOLO_ROOT), "custom", path=str(MODEL_PATH), source="local", autoshape=False)
model.to(device)
model.eval()

print("🔥 YOLO Kafka Consumer 시작됨")

try:
    for message in consumer:
        data = message.value
        frame_index += 1

        recv_time = time.time()
        sent_time = float(data.get("sent_timestamp", recv_time))
        latency_ms = (recv_time - sent_time) * 1000
        print(f"[{frame_index}] Frame latency: {latency_ms:.2f} ms")

        if frame_index == 1:
            start_time = time.time()

        if frame_index % 50 == 0:
            elapsed = time.time() - start_time
            fps = frame_index / elapsed
            print(f"🔥 Processed {frame_index} frames in {elapsed:.2f}s → {fps:.2f} FPS")

        camera_id = data["camera_id"]
        lat = data["location"]["latitude"]
        lon = data["location"]["longitude"]

        img_bytes = base64.b64decode(data["frame"])
        np_img = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        img = letterbox(frame, new_shape=640)
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img_tensor = torch.from_numpy(img).float() / 255.0
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)
        img_tensor = img_tensor.to(device)

        with torch.no_grad():
            pred = model(img_tensor)[0]
            pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

        filtered_detections = []
        for det in pred:
            if det is not None and len(det):
                scaled_coords = scale_coords(img_tensor.shape[2:], det[:, :4], frame.shape).round()
                det = det.clone()
                det[:, :4] = scaled_coords

                for det_item in det:
                    x1, y1, x2, y2 = map(int, det_item[:4])
                    conf = float(det_item[4])
                    cls = int(det_item[5])

                    if conf < 0.25:
                        continue

                    label = model.names[cls].lower()

                    x1, x2 = sorted([x1, x2])
                    y1, y2 = sorted([y1, y2])

                    h, w = frame.shape[:2]
                    x1, x2 = max(0, min(x1, w - 1)), max(0, min(x2, w - 1))
                    y1, y2 = max(0, min(y1, h - 1)), max(0, min(y2, h - 1))

                    if label == "fl":
                        color = (255, 0, 0)
                    elif label == "sm":
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        frame,
                        f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                    )

                    now = datetime.now()
                    last_time = last_sent_time.get(label)
                    if last_time and (now - last_time) < timedelta(minutes=10):
                        continue

                    filtered_detections.append(
                        {"label": label, "confidence": conf, "bbox": [x1, y1, x2, y2]}
                    )

        if len(filtered_detections) > 0:
            _, buf = cv2.imencode(".jpg", frame)
            annotated_b64 = base64.b64encode(buf).decode("utf-8")

            result = {
                "timestamp": datetime.now().isoformat(),
                "camera_id": camera_id,
                "location": {"latitude": lat, "longitude": lon},
                "detections": filtered_detections,
                "annotated_frame": annotated_b64,
            }

            producer.send(OUTPUT_TOPIC, value=result)
            print(f"🔥 감지 전송 완료 ({len(filtered_detections)}건)")

            for detection in filtered_detections:
                last_sent_time[detection["label"]] = datetime.now()
except Exception as e:
    print("❌ 예외 발생:", e)

