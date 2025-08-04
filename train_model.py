import torch
from torch.utils.data import DataLoader
from torch import nn, optim
import numpy as np
from sklearn.metrics import r2_score
from parce_data import (
    load_all_people_data, CreditSimulationDataset
)
from model import CreditScoreModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Используемое устройство: {device}")

all_data = load_all_people_data("people_statistic")
dataset = CreditSimulationDataset(all_data)
print(f"Загружено записей: {len(dataset)}")

train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

input_size = 20
model = CreditScoreModel(input_size=input_size).to(device)
print(f"Модель инициализирована с {input_size} входными параметрами")

loss_fn = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=2, factor=0.5)

epochs = 100
best_loss = float('inf')

for epoch in range(epochs):
    model.train()
    train_loss = 0
    all_preds = []
    all_targets = []
    
    for x_batch, y_batch in train_loader:
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)
        
        optimizer.zero_grad()
        predictions = model(x_batch)
        loss = loss_fn(predictions, y_batch)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item() * len(x_batch)
        all_preds.extend(predictions.detach().cpu().numpy())
        all_targets.extend(y_batch.detach().cpu().numpy())
    
    train_loss /= len(train_dataset)
    train_rmse = np.sqrt(train_loss) * 1000
    r2 = r2_score(all_targets, all_preds)
    
    model.eval()
    test_loss = 0
    test_preds = []
    test_targets = []
    
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            predictions = model(x_batch)
            loss = loss_fn(predictions, y_batch)
            test_loss += loss.item() * len(x_batch)
            test_preds.extend(predictions.cpu().numpy())
            test_targets.extend(y_batch.cpu().numpy())
    
    test_loss /= len(test_dataset)
    test_rmse = np.sqrt(test_loss) * 1000
    test_r2 = r2_score(test_targets, test_preds)
    
    scheduler.step(test_loss)
    
    print(f"\nEpoch {epoch+1}/{epochs}")
    print(f"Train Loss: {train_loss:.4f}")
    print(f"Test Loss:  {test_loss:.4f}")
    
    if test_loss < best_loss:
        best_loss = test_loss
        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'epoch': epoch,
            'input_size': input_size,
            'test_loss': test_loss,
        }, "best_credit_model.pth")
        print("Сохранена лучшая модель")

torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epoch': epochs,
    'input_size': input_size,
}, "final_credit_model.pth")
print("\nОбучение завершено. Модель сохранена в final_credit_model.pth")