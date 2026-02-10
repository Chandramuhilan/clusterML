"""Simple MNIST training script for ClusterML single-node example."""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    train_data = datasets.MNIST("./data", train=True, download=True, transform=transform)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)

    model = SimpleCNN().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0
        correct = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            correct += (output.argmax(1) == target).sum().item()

        accuracy = correct / len(train_data) * 100
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch}/{args.epochs} | Loss: {avg_loss:.4f} | Accuracy: {accuracy:.2f}%")

    print("Training complete!")
    torch.save(model.state_dict(), "model.pt")
    print("Model saved to model.pt")


if __name__ == "__main__":
    main()
