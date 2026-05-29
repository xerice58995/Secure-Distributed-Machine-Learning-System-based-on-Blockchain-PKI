# 安全分布式機器學習系統 - 文件索引

## 📚 文檔索引

### 主要文檔
- `README.md` - 完整的技術文檔，包含系統設計、架構、使用說明
- `QUICKSTART.md` - 快速開始指南，5分鐘上手
- `PROJECT_SUMMARY.md` - 項目完成總結，包含功能清單和統計
- `INDEX.md` - 本文件，快速導航

### 代碼文件
- `main.py` - 主程序入口，演示完整的系統流程
- `requirements.txt` - Python依賴列表

---

## 🗂️ 源代碼結構

### 區塊鏈PKI層 (`src/blockchain/`)

**blockchain.py** (246行)
```
功能: 輕量級區塊鏈實現
- Block 類: 單個區塊
- BlockData 類: 區塊存儲的元數據
- LightweightBlockchain 類: 區塊鏈管理器

關鍵方法:
- register_worker() - 註冊工作節點公鑰
- add_model_update_record() - 添加審計日誌
- validate_chain() - 驗證區塊鏈完整性
- get_worker_history() - 查詢工作節點歷史
```

### 安全層 (`src/security/`)

**crypto.py** (359行)
```
功能: 密碼學操作和簽名驗證
- CryptographicManager 類: 密碼學操作管理器
  * generate_rsa_key_pair() - RSA密鑰生成
  * generate_ecdsa_key_pair() - ECDSA密鑰生成
  * compute_model_hash() - SHA-256雜湊計算
  * sign_hash_rsa() - RSA簽署
  * verify_signature_rsa() - RSA驗證
  * verify_model_integrity() - 完整性驗證

- SignatureManager 類: 高層簽名管理
  * sign_model() - 簽署模型
  * verify_model() - 驗證模型
```

### 機器學習層 (`src/ml/`)

**model.py** (350行)
```
功能: 神經網絡模型和聯邦學習算法
- SimpleMLP 類: 多層感知機模型
  * forward() - 前向傳播
  * get_weights_dict() - 獲取權重
  * set_weights_dict() - 設置權重

- LocalTrainer 類: 本地訓練器
  * train_epoch() - 訓練一個epoch
  * evaluate() - 評估模型

- FederatedAveraging 類: 聯邦平均算法
  * aggregate_models() - 聚合多個模型
  * weighted_aggregate_models() - 加權聚合

- DataPartitioner 類: 數據分割
  * non_iid_partition() - Non-IID分割
  * iid_partition() - IID分割
```

### 網絡層 (`src/network/`)

**communication.py** (354行)
```
功能: 節點間通訊協議
- MessagePayload 類: 消息結構
- NetworkNode 抽象類: 節點基類
- LocalCommunicationBus 類: 本地通訊總線

- MasterNode 類: 主節點
  * distribute_model() - 分發模型
  * collect_model_updates() - 收集更新
  * record_verification_result() - 記錄驗證結果

- WorkerNode 類: 工作節點
  * submit_model_update() - 提交更新
  * receive_global_model() - 接收全局模型
```

### 系統協調器 (`src/system.py`)

**system.py** (499行)
```
功能: 整合所有層級的系統協調器
- SecureDMLSystem 類: 安全DML系統
  * setup_workers() - 設置工作節點
  * training_loop() - 完整訓練循環
  * collect_and_verify_updates() - 收集和驗證
  * aggregate_verified_models() - 聚合模型
  * simulate_malicious_worker() - 模擬攻擊
  * simulate_attack_detection() - 演示檢測
  * generate_report() - 生成報告
```

---

## 🧪 測試文件

### 區塊鏈測試 (`tests/test_blockchain.py`, 111行)
```
TestBlockchain 類測試用例:
- test_add_genesis_block - 創世區塊測試
- test_register_worker - 工作節點註冊測試
- test_get_worker_public_key - 公鑰查詢測試
- test_add_model_update_record - 記錄添加測試
- test_validate_chain - 鏈驗證測試
- test_worker_history - 歷史查詢測試
```

### 密碼學測試 (`tests/test_crypto.py`, 188行)
```
TestCryptography 類測試用例:
- test_rsa_key_generation - RSA密鑰生成
- test_ecdsa_key_generation - ECDSA密鑰生成
- test_model_hash_computation - 雜湊計算
- test_rsa_signature_verification - RSA簽名驗證
- test_ecdsa_signature_verification - ECDSA簽名驗證
- test_signature_manager_rsa - RSA管理器
- test_signature_manager_ecdsa - ECDSA管理器
- test_model_integrity_verification - 完整性驗證
- test_invalid_key_type - 錯誤處理
```

---

## 🎯 使用導航

### 如果你想...

#### 了解系統設計
→ 閱讀 `README.md` 的"系統架構"部分

#### 快速上手運行演示
→ 按照 `QUICKSTART.md` 的步驟

#### 理解區塊鏈實現
→ 查看 `src/blockchain/blockchain.py` + 運行 `test_blockchain.py`

#### 理解密碼學
→ 查看 `src/security/crypto.py` + 運行 `test_crypto.py`

#### 理解聯邦學習
→ 查看 `src/ml/model.py`

#### 理解通訊協議
→ 查看 `src/network/communication.py`

#### 看完整例子
→ 查看 `src/system.py` 和 `main.py`

#### 了解項目統計
→ 查看 `PROJECT_SUMMARY.md`

---

## 📊 代碼統計

```
層級             文件數   代碼行數   主要功能
─────────────────────────────────────────
區塊鏈層          1       246      PKI和審計
安全層            1       359      密碼學和簽名
機器學習層        1       350      模型和聯邦學習
網絡層            1       354      通訊協議
系統協調          1       499      整體協調
─────────────────────────────────────────
測試             2       299      單元測試
文檔             3       900+     技術文檔
主程序           1        58      入口點
─────────────────────────────────────────
合計            11      2,125+    完整系統
```

---

## 🔑 關鍵概念快速參考

### 區塊鏈相關
- **Block** - 區塊，包含區塊數據
- **BlockData** - 輕量級元數據（公鑰、雜湊、時間戳）
- **LightweightBlockchain** - 無PoW的區塊鏈
- **validate_chain()** - 驗證完整性

### 密碼學相關
- **RSA** - 非對稱加密算法，2048位
- **ECDSA** - 橢圓曲線簽名算法
- **SHA-256** - 密碼學雜湊函數
- **簽名** - 證明消息來源和未被篡改

### 機器學習相關
- **SimpleMLP** - 簡單的神經網絡
- **LocalTrainer** - 本地訓練器
- **FedAvg** - 聯邦平均聚合算法
- **DataPartitioner** - 數據分割器

### 系統相關
- **MasterNode** - 主節點，負責聚合和驗證
- **WorkerNode** - 工作節點，執行本地訓練
- **MessagePayload** - 消息結構
- **LocalCommunicationBus** - 本地通訊總線

---

## 🚀 執行流程

```
1. 初始化系統
   ↓
2. 設置工作節點（生成密鑰、註冊到區塊鏈）
   ↓
3. 分發初始模型
   ↓
4. 本地訓練
   ↓
5. 簽署模型（計算雜湊、生成簽名）
   ↓
6. 提交到主節點
   ↓
7. 驗證簽名和完整性
   ↓
8. 聚合驗證通過的模型
   ↓
9. 記錄到區塊鏈
   ↓
10. 重複3-9
```

---

## 📞 快速幫助

### 如何運行系統？
```bash
python main.py
```

### 如何運行測試？
```bash
python -m pytest tests/ -v
```

### 如何安裝依賴？
```bash
pip install -r requirements.txt
```

### 如何查看性能？
系統運行後自動輸出性能報告，包括：
- 簽名生成時間
- 簽名驗證時間
- 模型聚合時間
- 驗證通過率

---

## ✨ 系統特色

✅ **完全安全** - RSA/ECDSA + SHA-256 + 區塊鏈  
✅ **高效率** - 無PoW開銷，毫秒級驗證  
✅ **清晰設計** - 5層架構，關注點分離  
✅ **詳細註解** - 所有代碼都有中文註解  
✅ **充分測試** - 單元測試覆蓋核心功能  
✅ **易於擴展** - 模塊化設計，清晰接口  

---

祝您使用愉快！有任何問題請參考相應的文檔或代碼註解。
