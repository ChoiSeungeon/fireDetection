import os
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import classification_report, recall_score
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
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
        self.transform = transform or transforms.Compose(
            [transforms.Resize((224, 224)), transforms.ToTensor()]
        )

        self.samples = []
        for fname in os.listdir(img_dir):
            if fname.endswith(".jpg"):
                img_path = os.path.join(img_dir, fname)
                label_path = os.path.join(label_dir, fname.replace(".jpg", ".txt"))
                label = get_label_from_txt(label_path)
                if label is not None:
                    self.samples.append((img_path, label))

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
    val_img_dir = project_root / "data" / "images" / "val_sampled"
    val_label_dir = project_root / "data" / "labels" / "val_sampled"
    model_path = project_root / "models" / "best_fire_img_classifier_acc96.10.pth"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    val_dataset = FireSmokeImageDataset(str(val_img_dir), str(val_label_dir))
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    model = FireClassifier(num_classes=3).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for x_val, y_val in tqdm(val_loader, desc="Evaluating"):
            x_val, y_val = x_val.to(device), y_val.to(device)
            outputs = model(x_val)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(y_val.cpu().numpy())

    recall = recall_score(all_labels, all_preds, average="macro")
    print(f"\n📢 [Recall] Macro-Averaged Recall: {recall:.4f}")

    print("\n[Classification Report]")
    print(classification_report(all_labels, all_preds, target_names=["연기", "화염", "정상"]))

