import os
from pathlib import Path

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


def get_label_from_txt(label_path):
    try:
        with open(label_path, "r") as f:
            lines = f.readlines()
            labels = {int(line.split()[0]) for line in lines if line.strip()}
    except Exception:
        labels = set()

    if labels == {0}:
        return 0
    if 1 in labels:
        return 1
    if len(labels) == 0:
        return 2
    return None


class FireSmokeImageDataset(Dataset):
    def __init__(self, img_dir, label_dir, transform=None):
        self.img_dir = img_dir
        self.label_dir = label_dir
        self.transform = transform or T.Compose([T.Resize((224, 224)), T.ToTensor()])

        self.samples = []
        img_list = [f for f in os.listdir(img_dir) if f.endswith(".jpg")]
        for i, fname in enumerate(img_list):
            if i % 500 == 0:
                progress = f"[INFO] 처리 중: {i} / {len(img_list)}"
                print(progress.ljust(50), end="\r")

            img_path = os.path.join(img_dir, fname)
            label_path = os.path.join(label_dir, fname.replace(".jpg", ".txt"))
            label = get_label_from_txt(label_path)
            if label is not None:
                self.samples.append((img_path, label))

        print(f"\n총 {len(self.samples)}개의 이미지 로딩 완료")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        img = self.transform(Image.open(img_path).convert("RGB"))
        return img, label


class FireClassifier(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        base_model = models.resnet18(pretrained=True)
        base_model.fc = nn.Linear(base_model.fc.in_features, num_classes)
        self.model = base_model

    def forward(self, x):
        return self.model(x)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    train_img_dir = project_root / "data" / "images" / "train_sampled"
    train_label_dir = project_root / "data" / "labels" / "train_sampled"
    val_img_dir = project_root / "data" / "images" / "val_sampled"
    val_label_dir = project_root / "data" / "labels" / "val_sampled"
    checkpoint_path = project_root / "models" / "best_fire_img_classifier_acc96.10.pth"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_dataset = FireSmokeImageDataset(str(train_img_dir), str(train_label_dir))
    val_dataset = FireSmokeImageDataset(str(val_img_dir), str(val_label_dir))

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=5, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=5, pin_memory=True)

    model = FireClassifier(num_classes=3).to(device)
    if checkpoint_path.exists():
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))

    optimizer = Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    best_acc = 0.0

    for epoch in range(5, 10):
        model.train()
        total_train_loss = 0
        print(f"\nEpoch {epoch + 1}/10")
        for x, y in tqdm(train_loader, desc="Training", leave=False):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()

        model.eval()
        total_val_loss = 0
        correct = 0
        total = 0
        for x_val, y_val in tqdm(val_loader, desc="Validating", leave=False):
            x_val, y_val = x_val.to(device), y_val.to(device)
            with torch.no_grad():
                val_out = model(x_val)
                val_loss = criterion(val_out, y_val)
                total_val_loss += val_loss.item()
                preds = val_out.argmax(dim=1)
                correct += (preds == y_val).sum().item()
                total += y_val.size(0)

        acc = correct / total * 100
        print(
            f"[Epoch {epoch + 1}] Train Loss: {total_train_loss / len(train_loader):.4f} | "
            f"Val Loss: {total_val_loss / len(val_loader):.4f} | Val Acc: {acc:.2f}%"
        )

        if acc > best_acc:
            best_acc = acc
            output_path = project_root / f"best_fire_img_classifier_epoch{epoch + 1}_acc{acc:.2f}.pth"
            torch.save(model.state_dict(), output_path)
            print(f"✅ Best model saved at epoch {epoch + 1} with acc {acc:.2f}%")

