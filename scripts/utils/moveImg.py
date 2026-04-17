import os
import shutil
from pathlib import Path

# 상위 폴더 (fire, smoke, None 등 포함)
source_root = Path("D:/fireDetection/images/val")

# 샘플 이미지 저장 위치
target_root = Path("D:/fireDetection/images/val_sampled")
target_root.mkdir(parents=True, exist_ok=True)

# 최대 추출 수
max_samples = 90
extensions = ['.jpg', '.JPG', '.jpeg']
total_moved = 0

for subfolder in source_root.rglob("*"):
    if subfolder.is_dir():
        # 현재 폴더 내 이미지들 수집
        image_files = [f for f in subfolder.iterdir() if f.suffix.lower() in extensions and f.is_file()]
        image_files.sort()  # 이름 순 정렬

        num_images = len(image_files)
        if num_images == 0:
            continue

        # 추출 간격 계산
        step = max(1, num_images // max_samples)
        selected_files = image_files[::step][:max_samples]  # 간격 추출 후 최대 180개 제한

        for img_path in selected_files:
            target_path = target_root / img_path.name
            shutil.move(str(img_path), str(target_path))
            total_moved += 1

print(f"총 {total_moved}개의 이미지가 간격 샘플링되어 {target_root}로 이동되었습니다.")
