# 快速開始指南

## 🚀 5分鐘快速開始

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

### 系統的三大安全機制

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

- **簽名生成時間** - 平均毫秒級
- **簽名驗證時間** - 平均毫秒級
- **模型聚合時間** - 毫秒級
- **每輪訓練時間** - 秒級
- **驗證通過率** - 百分比

## 🔒 安全特性

✓ **身份驗證** - RSA/ECDSA簽名  
✓ **完整性保護** - SHA-256雜湊  
✓ **不可否認性** - 區塊鏈記錄  
✓ **審計追蹤** - 完整的操作日誌  
✓ **惡意檢測** - 自動識別模型篡改  

## 🎯 典型場景

### 醫療數據聯邦學習
多個醫院協作訓練診斷模型，保護患者隱私

### 金融風控聯合建模
銀行之間共享風控模型，防止模型被毒化

### 邊緣計算協作
IoT設備協作訓練模型，確保設備真實性

## 📁 文件結構速查

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

## 🐛 故障排除

### 問題1：導入錯誤
**解決方案：** 確保在項目根目錄運行，且已安裝所有依賴
```bash
cd Distributed_Maching_Learning
pip install -r requirements.txt
```

### 問題2：密鑰生成緩慢
**解決方案：** 這是正常現象，RSA密鑰生成需要時間。首次運行時可能需要幾秒鐘。

### 問題3：模型驗證失敗
**解決方案：** 檢查模型權重是否在簽名後被修改。使用完整性檢查確認權重未被篡改。

## 📚 進階主題

### 自定義模型
在 `src/ml/model.py` 中修改 `SimpleMLP` 類以支持不同的網絡結構

### 實時監控
在 `src/system.py` 中的 `training_loop` 方法中添加實時監控代碼

### 分散式部署
使用 FastAPI 或 gRPC 替換 `LocalCommunicationBus` 實現真實的分散式通訊

## 📞 支持

遇到問題？參考以下資源：

1. **代碼文檔** - 每個模塊都有詳細的中文註解
2. **測試用例** - `tests/` 目錄包含多個使用示例
3. **README** - 完整的技術文檔

## 🎓 學習資源

### 推薦閱讀順序
1. 先讀 `README.md` 了解整體架構
2. 檢查 `main.py` 了解使用流程
3. 查看各模塊代碼及註解
4. 運行測試用例驗證理解

### 關鍵概念
- **聯邦學習(FL)** - 分散式模型訓練
- **區塊鏈** - 不可篡改的分布式賬本
- **密碼學簽名** - 確保消息真實性和完整性
- **FedAvg算法** - 聯邦平均聚合策略

## 📈 擴展功能

系統可以輕鬆擴展：

- 添加更多工作節點
- 支持不同的密碼學算法
- 實現不同的聚合策略
- 添加異常檢測機制
- 集成真實數據集

祝您使用愉快！🎉
