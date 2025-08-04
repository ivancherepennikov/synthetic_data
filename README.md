# 🏦 Credit Score Simulation & Prediction Model

This project presents a credit scoring model trained entirely on synthetic data generated through simulation of "phantom" individuals. The approach allows for generating realistic, privacy-preserving training data to build and evaluate machine learning models for creditworthiness prediction.

---

## 📁 Project Structure

### 🔄 Simulation Files (Synthetic Data Generation)

- `main.py` — main script to run the simulation.
- `global_function.py` — utility functions used throughout the simulation process.
- `person.py` — class definition for `Person`, representing an individual with behavioral and financial attributes.
- `state.py` — constants and state definitions for the simulation.
- `names.py` — generation of first names, last names, and patronymics.

### 🤖 Model Files (Training & Prediction)

- `parce_data.py` — parses and prepares the synthetic dataset for training.
- `model.py` — defines the neural network architecture for credit score prediction.
- `train_model.py` — training script using the prepared dataset.

### 📦 Trained Model

- `final_credit_model.pth` — the final trained model.
  - Trained over **100 epochs**
  - **Best achieved loss:** `0.0162`
