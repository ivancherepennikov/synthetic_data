import torch
from torch.utils.data import DataLoader
from torch import nn, optim
from model import CreditScoreModel
from parce_data import load_all_people_data, CreditSimulationDataset

all_data = load_all_people_data("people_statistic_2")
dataset = CreditSimulationDataset(all_data)
print(f"Загружено: {len(dataset)} записей")

loader = DataLoader(dataset, batch_size=64, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CreditScoreModel(input_size=11).to(device)

loss_fn = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

epochs = 10
for epoch in range(epochs):
    model.train()
    total_loss = 0

    for x_batch, y_batch in loader:
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)

        optimizer.zero_grad()
        predictions = model(x_batch)
        loss = loss_fn(predictions, y_batch)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(x_batch)

    avg_loss = total_loss / len(dataset)
    print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
    rmse = (avg_loss ** 0.5) * 1000
    error_percent = rmse / 1000 * 100
    print(f"📊 RMSE: {rmse:.2f} очков | Ошибка: {error_percent:.2f}%")

if epoch + 1 == epochs:
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'epoch': epoch,
    }, "credit_model_checkpoint.pth")
    print("✅ Модель сохранена в credit_model_checkpoint.pth")
