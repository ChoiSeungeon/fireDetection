import os
import json
from glob import glob

# 📁 원본 경로
root_dir = r"D:\fireDetection\Training"

# 📁 YOLO 라벨 저장 위치
output_lbl_dir = r"D:\fireDetection\yolo_dataset\labels\train"
os.makedirs(output_lbl_dir, exist_ok=True)

# 클래스 매핑 (JSON category_id → YOLO class_id)
category_id_to_index = {2: 0, 1: 1}  # sm → 0, fl → 1

# 📂 모든 JSON 파일 순회
json_files = glob(os.path.join(root_dir, "02.라벨링데이터", "**", "JSON", "*.json"), recursive=True)

for json_path in json_files:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    width = data["image"]["width"]
    height = data["image"]["height"]
    filename = data["image"]["filename"]
    bbox_list = data["annotations"]

    yolo_lines = []
    for anno in bbox_list:
        cat_id = anno["categories_id"]
        if cat_id not in category_id_to_index:
            continue
        class_id = category_id_to_index[cat_id]

        # YOLO 형식으로 bbox 변환
        x, y, w, h = anno["bbox"]
        xc = (x + w / 2) / width
        yc = (y + h / 2) / height
        wn = w / width
        hn = h / height
        yolo_lines.append(f"{class_id} {xc:.6f} {yc:.6f} {wn:.6f} {hn:.6f}")

    # 파일 저장
    label_name = os.path.splitext(filename)[0] + ".txt"
    label_path = os.path.join(output_lbl_dir, label_name)
    with open(label_path, "w") as f:
        f.write("\n".join(yolo_lines))

print(f"✅ Training YOLO 라벨 {len(json_files)}개 변환 완료!")
