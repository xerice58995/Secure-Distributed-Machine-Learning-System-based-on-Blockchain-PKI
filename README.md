# 安全分布式機器學習系統（基於區塊鏈PKI）

> **課程:** 高等作業系統 (CSIE7010)  
> **作者:** CHING-YU HU (R14945033)

## 系統概述

本項目實現了一套輕量級且安全的**分布式機器學習(DML)框架**，集成了**區塊鏈式公鑰基礎設施(PKI)機制**。

### 核心創新

不同於傳統使用計算成本高昂的工作量證明(PoW)共識算法的區塊鏈應用，本項目創新地將區塊鏈重新定位為：

- **分散式公鑰基礎設施(PKI)** - 管理工作節點的公鑰
- **不可篡改的審計日誌** - 記錄所有模型更新
- **信任驗證基礎設施** - 確保分布式系統的安全性

區塊鏈僅存儲輕量級元數據（工作節點ID、公鑰、模型雜湊、時間戳），而非完整的模型權重，大幅降低系統開銷。

## 系統架構

### 層級設計

```
┌─────────────────────────────────────────┐
│       應用層（聯邦學習協調器）           │
│    - 模型分發、聚合、訓練協調           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         機器學習層（ML Models）          │
│    - SimpleMLP 神經網絡                 │
│    - 本地訓練器(LocalTrainer)          │
│    - 聯邦平均(FedAvg)聚合演算法         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       安全層（密碼學與簽名驗證）         │
│    - RSA/ECDSA 數位簽名                │
│    - SHA-256 雜湊驗證                  │
│    - 模型完整性驗證                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│     區塊鏈層（輕量級PKI基礎設施）       │
│    - 公鑰註冊與管理                    │
│    - 審計日誌記錄                      │
│    - 不可篡改驗證                      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       通訊層（節點間通訊協議）           │
│    - 主節點(MasterNode)                │
│    - 工作節點(WorkerNode)              │
│    - 消息隊列與路由                    │
└─────────────────────────────────────────┘
```

## 系統工作流程

### 步驟1：工作節點註冊
```
工作節點 → 生成RSA/ECDSA密鑰對
       → 向區塊鏈註冊公鑰
       → 加入聯邦學習系統
```

### 步驟2：全局模型分發
```
主節點 → 初始化全局模型
      → 向所有工作節點廣播分發
      → 所有工作節點接收相同的初始模型
```

### 步驟3：本地訓練
```
工作節點 → 在本地數據集上進行本地訓練
        → 計算模型更新
```

### 步驟4：模型簽名
```
工作節點 → 計算模型權重的SHA-256雜湊
        → 使用私鑰簽署雜湊
        → 發送：模型權重 + 雜湊 + 簽名 給主節點
```

### 步驟5：驗證與聚合
```
主節點 → 接收所有模型更新
      → 從區塊鏈查詢工作節點公鑰
      → 驗證簽名和模型完整性
      → 僅聚合驗證通過的模型
      → 使用FedAvg進行加權平均
      → 將驗證結果記錄到區塊鏈
```

## 文件結構

```
Distributed_Maching_Learning/
├── src/
│   ├── blockchain/
│   │   └── blockchain.py          # 輕量級區塊鏈PKI實現
│   ├── security/
│   │   └── crypto.py               # 密碼學與簽名驗證
│   ├── ml/
│   │   └── model.py                # 神經網絡模型與聯邦學習
│   ├── network/
│   │   └── communication.py        # 節點間通訊協議
│   └── system.py                   # 系統協調器
├── tests/
│   ├── test_blockchain.py          # 區塊鏈單元測試
│   └── test_crypto.py              # 密碼學單元測試
├── main.py                         # 主程序入口
├── requirements.txt                # 依賴列表
└── README.md                       # 本文件
```

## 關鍵模塊說明

### 1. 區塊鏈PKI層 (`blockchain.py`)

**LightweightBlockchain 類**
- 管理工作節點的公鑰註冊
- 記錄模型更新的審計日誌
- 驗證區塊鏈的完整性

**主要方法：**
```python
# 註冊工作節點
register_worker(worker_id, public_key) -> bool

# 查詢公鑰
get_worker_public_key(worker_id) -> str

# 添加模型更新記錄
add_model_update_record(worker_id, model_hash, metadata) -> bool

# 驗證區塊鏈
validate_chain() -> bool
```

### 2. 密碼學層 (`crypto.py`)

**CryptographicManager 類**
- RSA/ECDSA密鑰生成
- SHA-256雜湊計算
- 數位簽名生成與驗證

**SignatureManager 類**
- 高層簽名管理接口
- 模型簽名與驗證流程

**主要方法：**
```python
# 生成密鑰對
generate_rsa_key_pair() -> (private_key, public_key)
generate_ecdsa_key_pair() -> (private_key, public_key)

# 計算模型雜湊
compute_model_hash(model_weights) -> hash_value

# 驗證簽名
verify_signature_rsa(hash, signature, public_key) -> bool
verify_signature_ecdsa(hash, signature, public_key) -> bool

# 驗證模型完整性
verify_model_integrity(weights, hash) -> bool
```

### 3. 機器學習層 (`model.py`)

**SimpleMLP 類**
- 簡單的多層感知機模型
- 用於MNIST手寫數字識別

**LocalTrainer 類**
- 本地訓練器
- 支持本地epoch訓練和評估

**FederatedAveraging 類**
- FedAvg聯邦平均算法實現
- 支持加權聚合

**DataPartitioner 類**
- 將數據集分割給工作節點
- 支持IID和Non-IID分布

### 4. 通訊層 (`communication.py`)

**MasterNode 類**
- 主節點，負責模型聚合和驗證
- 分發全局模型給工作節點
- 收集和驗證工作節點的模型更新

**WorkerNode 類**
- 工作節點，執行本地訓練
- 提交簽署的模型更新

**LocalCommunicationBus 類**
- 本地通訊總線
- 在單機模擬中實現節點間通訊

### 5. 系統協調器 (`system.py`)

**SecureDMLSystem 類**
- 整合所有層級
- 協調完整的聯邦學習流程
- 演示安全性和性能

## 使用說明

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 運行完整演示

```bash
python main.py
```

該命令將執行以下操作：

1. **工作節點註冊** - 為3個工作節點生成密鑰並註冊到區塊鏈
2. **訓練循環** - 執行2輪完整的聯邦學習
3. **安全演示** - 模擬惡意節點的攻擊並展示檢測能力
4. **生成報告** - 輸出性能和安全性報告

### 運行單元測試

```bash
# 測試區塊鏈功能
python -m pytest tests/test_blockchain.py -v

# 測試密碼學功能
python -m pytest tests/test_crypto.py -v

# 運行所有測試
python -m pytest tests/ -v
```

## 核心功能演示

### 1. 模型簽名和驗證

```python
from src.security.crypto import SignatureManager

# 創建簽名管理器（使用RSA）
manager = SignatureManager(key_type="rsa")

# 生成密鑰對
private_key, public_key = manager.generate_keys()

# 簽署模型
model_hash, signature = manager.sign_model(model_weights, private_key)

# 驗證模型
is_valid, message = manager.verify_model(
    model_weights, model_hash, signature, public_key
)
```

### 2. 區塊鏈PKI管理

```python
from src.blockchain.blockchain import LightweightBlockchain

# 創建區塊鏈
blockchain = LightweightBlockchain()
blockchain.add_genesis_block()

# 註冊工作節點
blockchain.register_worker("worker_1", public_key)

# 添加模型更新記錄
blockchain.add_model_update_record(
    "worker_1", 
    model_hash, 
    {"verified": True}
)

# 驗證區塊鏈
is_valid = blockchain.validate_chain()
```

### 3. 聯邦學習聚合

```python
from src.ml.model import FederatedAveraging

# 聚合多個模型
verified_models = [model1, model2, model3]
aggregated = FederatedAveraging.aggregate_models(verified_models)

# 加權聚合
weights = [0.3, 0.4, 0.3]
weighted_aggregated = FederatedAveraging.weighted_aggregate_models(
    verified_models, weights
)
```

## 安全性特性

### 1. 模型簽名驗證
- 每個工作節點必須用私鑰簽署模型
- 主節點使用公鑰驗證簽名的真實性
- 防止身份欺騙

### 2. 完整性檢查
- SHA-256雜湊用於檢測模型篡改
- 雜湊值包含在簽名中
- 任何權重修改都會導致驗證失敗

### 3. 不可否認性
- 工作節點無法否認其提交的模型
- 所有操作記錄在不可篡改的區塊鏈上

### 4. 審計追蹤
- 區塊鏈記錄每個工作節點的所有操作
- 支持事後審計和分析

## 性能指標

系統計測以下性能指標：

- **簽名生成時間** - RSA/ECDSA簽名耗時
- **簽名驗證時間** - 驗證簽名耗時
- **模型聚合時間** - FedAvg聚合耗時
- **每輪訓練時間** - 完整訓練輪次耗時
- **驗證通過率** - 模型驗證成功比率

## 惡意節點檢測演示

系統能夠檢測多種攻擊：

### 模型篡改檢測
```
惡意節點試圖修改模型權重
  ↓
計算新的雜湊值（與簽名的雜湊不匹配）
  ↓
驗證失敗，拒絕該模型
  ↓
記錄攻擊到審計日誌
```

### 簽名偽造檢測
```
攻擊者試圖偽造簽名
  ↓
主節點使用工作節點的公鑰驗證
  ↓
簽名無效，驗證失敗
  ↓
保護全局模型
```

## 區塊鏈設計優勢

### 相比PoW共識的改進

| 特性 | 傳統PoW | 本系統 |
|------|---------|--------|
| 共識機制 | CPU密集型挖礦 | 無需挖礦 |
| 存儲開銷 | 存儲完整模型 | 僅存儲元數據 |
| 能量消耗 | 極高 | 低 |
| 安全性 | 基於計算成本 | 基於密碼學 |
| 惡意檢測 | 無法檢測模型毒化 | 可檢測 |
| 可擴展性 | 受限 | 高度可擴展 |

## 研究成果

### 系統優勢

1. **安全性** - RSA/ECDSA簽名確保真實性和完整性
2. **效率** - 無需PoW，顯著降低開銷
3. **可審計性** - 不可篡改的審計日誌
4. **可擴展性** - 輕量級區塊鏈支持大規模系統

### 應用場景

- 醫療數據聯邦學習
- 金融風控模型協作
- 邊緣計算節點協作
- 企業隱私保護聯合建模

## 參考文獻

- Wang, Z., Wang, Q., Yu, G., & Chen, S. (2024). TDML - A Trustworthy Distributed Machine Learning Framework.

- Subasi, Omer et al. "The Landscape of Modern Machine Learning: A Review of Machine, Distributed and Federated Learning." ArXiv abs/2312.03120 (2023).

- McMahan, B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data.

- Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system.

## 許可證

本項目用於教育和研究目的。

## 聯絡方式

如有任何問題或建議，歡迎反饋。
