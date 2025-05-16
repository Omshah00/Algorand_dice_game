# 🎲 Algorand Dice Game Smart Contract

This is a simple blockchain-based dice game built on the Algorand TestNet using PyTeal and the Algorand Python SDK.

## 📌 Overview

Players interact with a smart contract by sending a small amount of ALGO. The contract simulates a dice roll using the current block timestamp. If the result is 4 or higher, the player wins double the stake; otherwise, the stake is kept by the contract.

---

## 📁 Project Structure

algorand_dice_game/
├── dice_game.py
├── deploy.py 

---

## ⚙️ Prerequisites

- Python 3.8+
- Install required packages:

```bash
pip install pyteal algosdk
