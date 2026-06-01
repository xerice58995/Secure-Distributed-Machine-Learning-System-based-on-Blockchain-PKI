# 安全分布式機器學習系統（基於區塊鏈PKI）

## 系統概述

本項目實現了一套輕量級且安全的**分布式機器學習(DML)框架**，集成了**區塊鏈式公鑰基礎設施(PKI)機制**。

### 核心創新

不同於傳統使用計算成本高昂的工作量證明(PoW)共識算法的區塊鏈應用，本項目創新地將區塊鏈重新定位為：

- **分散式公鑰基礎設施(PKI)** - 管理工作節點的公鑰
- **不可篡改的審計日誌** - 記錄所有模型更新
- **信任驗證基礎設施** - 確保分布式系統的安全性

區塊鏈僅存儲輕量級元數據（工作節點ID、公鑰、模型雜湊、時間戳），而非完整的模型權重，大幅降低系統開銷。

# 快速開始

### 1. 環境設置

```bash
# 安裝依賴
pip install torch torchvision numpy cryptography

# 或使用requirements.txt
pip install -r requirements.txt
```

### 2. 運行演示

```bash
# 進入項目目錄
cd Distributed_Maching_Learning

# 運行完整演示
python main.py
```

### 3. 運行測試

```bash
# 測試區塊鏈功能
python -m pytest tests/test_blockchain.py -v

# 測試密碼學功能
python -m pytest tests/test_crypto.py -v
```

## 📋 核心概念

### 系統安全機制

1. **數位簽名** - RSA/ECDSA簽署模型
   - 工作節點使用私鑰簽署
   - 主節點使用公鑰驗證
   - 防止身份欺騙

2. **完整性檢查** - SHA-256雜湊驗證
   - 檢測模型是否被篡改
   - 任何權重修改都會導致驗證失敗

3. **不可篡改審計** - 區塊鏈記錄
   - 記錄所有模型更新
   - 支持事後審計和追蹤

### 執行流程

```
工作節點生成密鑰對
      ↓
向區塊鏈註冊公鑰
      ↓
接收主節點的全局模型
      ↓
本地訓練模型
      ↓
計算模型雜湊
      ↓
使用私鑰簽署雜湊
      ↓
提交給主節點
      ↓
主節點驗證簽名和完整性
      ↓
只聚合驗證通過的模型
      ↓
記錄到區塊鏈
```

## 💻 代碼示例

### 示例1：基本設置

```python
from src.system import SecureDMLSystem

# 創建系統（3個工作節點）
system = SecureDMLSystem(num_workers=3, crypto_type="rsa")

# 設置工作節點
system.setup_workers()

# 執行訓練
system.training_loop(num_rounds=5)

# 生成報告
system.generate_report()
```

### 示例2：密鑰管理

```python
from src.security.crypto import SignatureManager

# 創建簽名管理器
manager = SignatureManager(key_type="rsa")

# 生成密鑰對
private_key, public_key = manager.generate_keys()

# 簽署和驗證
model_hash, signature = manager.sign_model(model_weights, private_key)
is_valid, msg = manager.verify_model(model_weights, model_hash, signature, public_key)
```

### 示例3：區塊鏈操作

```python
from src.blockchain.blockchain import LightweightBlockchain

# 創建區塊鏈
bc = LightweightBlockchain()
bc.add_genesis_block()

# 註冊工作節點
bc.register_worker("worker_1", public_key)

# 添加模型記錄
bc.add_model_update_record("worker_1", model_hash, {"verified": True})

# 驗證完整性
is_valid = bc.validate_chain()
```

## 📊 性能指標

系統自動測量和報告：

- **簽名生成時間** - RSA/ECDSA簽名耗時 :
- **簽名驗證時間** - 驗證簽名耗時 :
- **模型聚合時間** - FedAvg聚合耗時 :
- **每輪訓練時間** - 完整訓練輪次耗時 :
- **驗證通過率** - 模型驗證成功比率 :

## 🔒 安全特性

✓ **身份驗證** - RSA/ECDSA簽名  
✓ **完整性保護** - SHA-256雜湊  
✓ **不可否認性** - 區塊鏈記錄  
✓ **審計追蹤** - 完整的操作日誌  
✓ **惡意檢測** - 自動識別模型篡改  

## 場景

### 醫療數據聯邦學習
多個醫院協作訓練診斷模型，保護患者隱私

### 金融風控聯合建模
銀行之間共享風控模型，防止模型被毒化

### 邊緣計算協作
IoT設備協作訓練模型，確保設備真實性

## 📁 文件結構

```
src/
├── blockchain/blockchain.py      # 區塊鏈PKI實現
├── security/crypto.py            # 密碼學與簽名
├── ml/model.py                   # 神經網絡與聯邦學習
├── network/communication.py      # 節點通訊
└── system.py                     # 系統協調器

tests/
├── test_blockchain.py            # 區塊鏈測試
└── test_crypto.py                # 密碼學測試

main.py                           # 主程序入口
```


## 參考文獻

- Wang, Z., Wang, Q., Yu, G., & Chen, S. (2024). TDML - A Trustworthy Distributed Machine Learning Framework.

- Subasi, Omer et al. "The Landscape of Modern Machine Learning: A Review of Machine, Distributed and Federated Learning." ArXiv abs/2312.03120 (2023).

- McMahan, B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data.

- Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system.
