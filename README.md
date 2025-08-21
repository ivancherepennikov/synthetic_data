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
  - **Best achieved loss:** `0.0831`

## 🧠 Simulated Person Behavior

Each person in the simulation (`Person` class) is a self-contained agent with complex, life-like behavior. Here's what a person can do in the simulation:

---

### 🧬 Life Events
- ⏳ Ages over time
- 💀 Can **die** (probability depends on age, income, debt)
- 🧓 Can **retire** and receive a pension

---

### 👪 Social Behavior
- 💍 Can **get married**
- 💔 Can **divorce**
- 👶 Can **have children**
- 🧾 Can **receive inheritance** (or **inherit debt**) from parents

---

### 🎓 Education & Military
- 🏫 Can **receive education**: school → college → university
- 🎖️ Males may **join the army** after high school

---

### 💼 Work & Finance
- 💼 Can **change jobs** (income depends on job type and education)
- 🔥 Can **burn out** and **lose job**
- 💰 Earns **income**, which may increase or decrease over time
- 🏦 Can **take loans** if balance is negative
- 📉 Can **miss loan payments**, **incur penalties**, and hurt credit score
- 📈 Receives **interest** on savings
- 🧽 May **wipe credit history** under risky conditions

---

### ⚖️ Legal & Ethical Actions
- 💸 May **attempt bribery** (can increase income or result in prison)
- 🚔 May **go to prison** (random chance + risky behavior)
- 🧍‍♂️ Can **serve sentence** and get **released**
- 👮 While imprisoned, **income drops** and **work status changes**

---

### 💳 Credit Score Logic
Credit score is updated dynamically based on:
- 💵 Income level  
- 🏦 Balance and 💳 Debt  
- ⌛ Missed payments  
- 🎓 Education level  
- 👶 Age  
- 🧾 Loan history  
- 🎲 Random risk factors

---

### 🛢️ Economy & Resources
- 🛢️ Oil as a limited resource affecting the economy
- 📉 Low oil supply causes inflation, higher living costs, and reduced credit availability
- 💹 Oil prices influence income and financial decisions of all agents
- 🔄 Oil reserves are updated dynamically each simulation cycle
- 🔢 **Final credit score is scaled between 0 and 999**
