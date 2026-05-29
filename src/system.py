"""
聯邦學習系統協調器
整合所有層級，實現完整的安全分布式機器學習系統
"""

import time
import numpy as np
from typing import Dict, List, Optional, Tuple
import torch
from torch.utils.data import DataLoader

from src.blockchain.blockchain import LightweightBlockchain
from src.security.crypto import SignatureManager, CryptographicManager
from src.ml.model import SimpleMLP, LocalTrainer, FederatedAveraging, DataPartitioner
from src.network.communication import (
    LocalCommunicationBus, MasterNode, WorkerNode, MessagePayload
)


class SecureDMLSystem:
    """
    安全分布式機器學習系統
    整合區塊鏈PKI、密碼簽名驗證和聯邦學習框架
    """

    def __init__(self, num_workers: int = 3,
                 crypto_type: str = "rsa",
                 device: str = "cpu"):
        """
        初始化安全DML系統

        Args:
            num_workers: 工作節點數量
            crypto_type: 密碼學類型（"rsa"或"ecdsa"）
            device: 計算設備（"cpu"或"cuda"）
        """
        self.num_workers = num_workers
        self.device = device

        # 初始化各層級組件
        self.blockchain = LightweightBlockchain()
        self.blockchain.add_genesis_block()

        self.signature_manager = SignatureManager(key_type=crypto_type)

        # 初始化通訊層
        self.comm_bus = LocalCommunicationBus()
        self.master_node = MasterNode("master", self.comm_bus)
        self.worker_nodes: Dict[str, WorkerNode] = {}
        self.worker_keys: Dict[str, Tuple[str, str]] = {}  # worker_id -> (private_key, public_key)

        # 註冊主節點
        self.comm_bus.register_node(self.master_node)

        # 初始化全局模型
        self.global_model = SimpleMLP()
        self.global_model.to(device)

        # 訓練歷史
        self.training_history: Dict[str, List] = {
            "loss": [],
            "accuracy": [],
            "round": []
        }

        # 效能指標
        self.performance_metrics = {
            "signature_generation_time": [],
            "signature_verification_time": [],
            "aggregation_time": [],
            "total_round_time": []
        }

    def setup_workers(self):
        """
        設置並初始化所有工作節點
        包括生成密鑰、註冊到區塊鏈、註冊到通訊總線
        """
        print(f"正在設置{self.num_workers}個工作節點...")

        worker_ids = []

        for i in range(self.num_workers):
            worker_id = f"worker_{i}"
            worker_ids.append(worker_id)

            # 創建工作節點
            worker_node = WorkerNode(worker_id, self.comm_bus)
            self.worker_nodes[worker_id] = worker_node
            self.comm_bus.register_node(worker_node)

            # 生成公鑰-私鑰對
            private_key, public_key = self.signature_manager.generate_keys()
            self.worker_keys[worker_id] = (private_key, public_key)

            # 將公鑰註冊到區塊鏈PKI
            success = self.blockchain.register_worker(worker_id, public_key)
            if success:
                print(f"  ✓ 工作節點{worker_id}已註冊到區塊鏈")
            else:
                print(f"  ✗ 工作節點{worker_id}註冊失敗")

        # 向主節點註冊工作節點列表
        self.master_node.register_workers(worker_ids)
        print(f"主節點已註冊{len(worker_ids)}個工作節點")

    def distribute_initial_model(self):
        """
        分發初始的全局模型到所有工作節點
        """
        print("正在分發初始全局模型...")
        model_weights = self.global_model.get_weights_dict()

        # 轉換為列表格式以便傳輸
        weights_for_transmission = {
            k: v.tolist() for k, v in model_weights.items()
        }

        distribution_status = self.master_node.distribute_model(weights_for_transmission)

        successful = sum(1 for status in distribution_status.values() if status)
        print(f"模型分發完成：{successful}/{self.num_workers}個節點")

    def local_training_round(self, train_loaders: Dict[str, DataLoader]):
        """
        執行一輪本地訓練
        每個工作節點在其本地數據上訓練模型

        Args:
            train_loaders: 每個工作節點的訓練數據加載器
        """
        print("執行本地訓練...")

        for worker_id, train_loader in train_loaders.items():
            # 獲取工作節點的本地模型
            worker_model = SimpleMLP().to(self.device)

            # 設置全局模型的權重
            global_weights = self.global_model.get_weights_dict()
            weights_array = {k: np.array(v) for k, v in global_weights.items()}
            worker_model.set_weights_dict(weights_array)

            # 本地訓練
            trainer = LocalTrainer(worker_model, self.device)
            loss = trainer.train_epoch(train_loader, learning_rate=0.01)

            print(f"  {worker_id} 訓練損失: {loss:.4f}")

    def collect_and_verify_updates(self) -> List[Dict]:
        """
        收集工作節點的模型更新並進行驗證

        Returns:
            驗證通過的模型更新列表
        """
        print("收集和驗證模型更新...")

        # 收集所有模型更新
        collected_updates = self.master_node.collect_model_updates(timeout=10.0)
        print(f"收集到{len(collected_updates)}個模型更新")

        verified_updates = []

        # 驗證每個模型更新
        for update in collected_updates:
            worker_id = update.get("sender_id")
            model_hash = update.get("model_hash")
            signature = update.get("signature")
            model_weights = update.get("model_weights")

            # 從區塊鏈獲取工作節點的公鑰
            public_key = self.blockchain.get_worker_public_key(worker_id)

            if not public_key:
                print(f"  ✗ {worker_id}: 公鑰未找到")
                self.master_node.record_verification_result(
                    worker_id, False, "公鑰未找到"
                )
                continue

            # 驗證模型簽名和完整性
            start_time = time.time()
            is_valid, message = self.signature_manager.verify_model(
                model_weights, model_hash, signature, public_key
            )
            verification_time = time.time() - start_time
            self.performance_metrics["signature_verification_time"].append(verification_time)

            # 記錄驗證結果
            self.master_node.record_verification_result(
                worker_id, is_valid, message, model_hash
            )

            if is_valid:
                print(f"  ✓ {worker_id}: 驗證通過")
                verified_updates.append(update)

                # 將驗證結果記錄到區塊鏈
                self.blockchain.add_model_update_record(
                    worker_id, model_hash, {"verified": True}
                )
            else:
                print(f"  ✗ {worker_id}: 驗證失敗 - {message}")

                # 記錄不驗證的更新到區塊鏈（用於審計）
                self.blockchain.add_model_update_record(
                    worker_id, model_hash, {"verified": False, "reason": message}
                )

        return verified_updates

    def aggregate_verified_models(self, verified_updates: List[Dict]) -> bool:
        """
        聚合所有驗證通過的模型更新
        使用FedAvg算法

        Args:
            verified_updates: 驗證通過的模型更新列表

        Returns:
            聚合是否成功
        """
        if not verified_updates:
            print("沒有驗證通過的模型，無法進行聚合")
            return False

        print(f"聚合{len(verified_updates)}個驗證通過的模型...")

        # 提取驗證通過的模型權重
        verified_models = []
        for update in verified_updates:
            model_weights = update.get("model_weights")
            # 轉換回numpy數組
            weights_array = {k: np.array(v) for k, v in model_weights.items()}
            verified_models.append(weights_array)

        # 聚合模型
        start_time = time.time()
        aggregated_weights = FederatedAveraging.aggregate_models(verified_models)
        aggregation_time = time.time() - start_time
        self.performance_metrics["aggregation_time"].append(aggregation_time)

        # 更新全局模型
        self.global_model.set_weights_dict(aggregated_weights)
        print(f"聚合完成（耗時{aggregation_time:.4f}秒）")

        return True

    def simulate_malicious_worker(self, worker_id: str,
                                  train_loader: DataLoader) -> Dict:
        """
        模擬惡意工作節點的行為
        嘗試提交被篡改的模型

        Args:
            worker_id: 工作節點編號
            train_loader: 訓練數據加載器

        Returns:
            簽署的模型更新（含被篡改的權重）
        """
        print(f"\n模擬惡意節點{worker_id}的攻擊...")

        # 正常訓練模型
        worker_model = SimpleMLP().to(self.device)
        global_weights = self.global_model.get_weights_dict()
        weights_array = {k: np.array(v) for k, v in global_weights.items()}
        worker_model.set_weights_dict(weights_array)

        trainer = LocalTrainer(worker_model, self.device)
        trainer.train_epoch(train_loader, learning_rate=0.01)

        # 獲取訓練後的模型
        model_weights = worker_model.get_weights_dict()

        # 篡改模型權重（注入隨機噪聲）
        print(f"  正在篡改模型權重...")
        poisoned_weights = {}
        for key, value in model_weights.items():
            # 添加大型隨機擾動
            poison_noise = np.random.randn(*value.shape) * 10
            poisoned_weights[key] = value + poison_noise

        # 計算被篡改模型的真實雜湊（正確的）
        correct_hash = CryptographicManager.compute_model_hash(model_weights)
        poisoned_hash = CryptographicManager.compute_model_hash(poisoned_weights)

        # 簽署正確的雜湊但發送被篡改的權重（攻擊方案）
        private_key = self.worker_keys[worker_id][0]
        signature = CryptographicManager.sign_hash_rsa(correct_hash, private_key)

        print(f"  正確雜湊: {correct_hash[:16]}...")
        print(f"  被篡改雜湊: {poisoned_hash[:16]}...")
        print(f"  簽名使用的雜湊: {correct_hash[:16]}...")

        return {
            "model_weights": poisoned_weights,
            "model_hash": correct_hash,  # 簽署的是正確的雜湊
            "signature": signature,
            "sender_id": worker_id,
            "is_malicious": True
        }

    def training_loop(self, num_rounds: int = 5):
        """
        執行完整的訓練循環

        Args:
            num_rounds: 訓練輪數
        """
        print("\n" + "="*60)
        print("啟動安全分布式機器學習系統")
        print("="*60)

        # 準備MNIST數據集（模擬）
        print("\n正在準備訓練數據...")
        # 注意：實際使用時需要下載MNIST數據集
        print("  使用模擬數據集進行演示")

        for round_num in range(num_rounds):
            print(f"\n{'='*60}")
            print(f"訓練輪次 {round_num + 1}/{num_rounds}")
            print(f"{'='*60}")

            round_start = time.time()

            # 步驟1: 分發全局模型
            self.distribute_initial_model()

            # 步驟2: 本地訓練（模擬）
            # 在實際實現中，這些會由各個工作節點執行
            print("\n執行本地訓練（模擬）...")

            # 步驟3: 收集並驗證模型更新
            print("\n模擬工作節點提交模型更新...")

            # 為了演示，我們模擬收集更新
            verified_updates = []

            for worker_id in self.worker_nodes.keys():
                # 創建模型更新消息（模擬）
                worker_model = SimpleMLP().to(self.device)
                model_weights = worker_model.get_weights_dict()

                # 簽署模型
                private_key = self.worker_keys[worker_id][0]
                public_key = self.worker_keys[worker_id][1]

                start_time = time.time()
                model_hash, signature = self.signature_manager.sign_model(
                    model_weights, private_key
                )
                sig_time = time.time() - start_time
                self.performance_metrics["signature_generation_time"].append(sig_time)

                # 驗證模型
                start_time = time.time()
                is_valid, message = self.signature_manager.verify_model(
                    model_weights, model_hash, signature, public_key
                )
                verify_time = time.time() - start_time
                self.performance_metrics["signature_verification_time"].append(verify_time)

                # 創建更新消息
                update = {
                    "model_weights": model_weights,
                    "model_hash": model_hash,
                    "signature": signature,
                    "sender_id": worker_id
                }

                # 將消息添加到主節點隊列
                message_obj = MessagePayload(
                    message_type="model_submit",
                    sender_id=worker_id,
                    receiver_id="master",
                    timestamp=time.time(),
                    data={
                        "model_weights": {k: v.tolist() if hasattr(v, 'tolist') else v
                                        for k, v in model_weights.items()},
                        "model_hash": model_hash,
                        "signature": signature
                    }
                )
                self.master_node.message_queue.append(message_obj)

                print(f"  {worker_id}: 簽名驗證={is_valid} (簽名生成耗時{sig_time*1000:.2f}ms，驗證耗時{verify_time*1000:.2f}ms)")

            # 步驟4: 收集和驗證模型
            verified_updates = self.collect_and_verify_updates()

            # 步驟5: 聚合驗證通過的模型
            if verified_updates:
                start_time = time.time()
                self.aggregate_verified_models(verified_updates)
                aggregation_time = time.time() - start_time
            else:
                print("沒有驗證通過的模型")

            round_time = time.time() - round_start
            self.performance_metrics["total_round_time"].append(round_time)

            print(f"訓練輪次耗時: {round_time:.2f}秒")

            # 記錄歷史
            self.training_history["round"].append(round_num + 1)

    def simulate_attack_detection(self):
        """
        演示系統對惡意節點的檢測能力
        """
        print("\n" + "="*60)
        print("演示：惡意節點檢測")
        print("="*60)

        print("\n場景：惡意工作節點試圖提交被篡改的模型")

        # 模擬惡意節點
        worker_id = "worker_0"

        # 創建模擬的訓練數據
        dummy_data = torch.randn(100, 1, 28, 28)
        dummy_labels = torch.randint(0, 10, (100,))
        dummy_dataset = torch.utils.data.TensorDataset(dummy_data, dummy_labels)
        train_loader = DataLoader(dummy_dataset, batch_size=32)

        # 執行惡意攻擊
        malicious_update = self.simulate_malicious_worker(worker_id, train_loader)

        # 驗證惡意模型
        print("\n驗證惡意模型...")
        public_key = self.blockchain.get_worker_public_key(worker_id)

        is_valid, message = self.signature_manager.verify_model(
            malicious_update["model_weights"],
            malicious_update["model_hash"],
            malicious_update["signature"],
            public_key
        )

        print(f"\n驗證結果:")
        print(f"  簽名有效: {not is_valid}（預期：False，因為權重被篡改）")
        print(f"  詳細信息: {message}")

        if not is_valid:
            print(f"\n✓ 系統成功檢測到惡意模型！")
            print(f"  {message}")

        # 記錄到區塊鏈
        self.blockchain.add_model_update_record(
            worker_id,
            malicious_update["model_hash"],
            {"verified": False, "reason": message, "attack_type": "model_poisoning"}
        )

    def generate_report(self):
        """
        生成系統性能和安全性報告
        """
        print("\n" + "="*60)
        print("系統效能和安全性報告")
        print("="*60)

        # 驗證報告
        verification_report = self.master_node.get_verification_report()
        print("\n驗證統計:")
        print(f"  總提交數: {verification_report['total_submissions']}")
        print(f"  驗證通過: {verification_report['valid_submissions']}")
        print(f"  驗證失敗: {verification_report['invalid_submissions']}")
        print(f"  驗證率: {verification_report['verification_rate']:.2f}%")

        # 效能指標
        print("\n效能指標:")
        if self.performance_metrics["signature_generation_time"]:
            avg_sig_gen = np.mean(self.performance_metrics["signature_generation_time"]) * 1000
            print(f"  平均簽名生成時間: {avg_sig_gen:.2f}ms")

        if self.performance_metrics["signature_verification_time"]:
            avg_sig_verify = np.mean(self.performance_metrics["signature_verification_time"]) * 1000
            print(f"  平均簽名驗證時間: {avg_sig_verify:.2f}ms")

        if self.performance_metrics["aggregation_time"]:
            avg_agg = np.mean(self.performance_metrics["aggregation_time"]) * 1000
            print(f"  平均聚合時間: {avg_agg:.2f}ms")

        if self.performance_metrics["total_round_time"]:
            avg_round = np.mean(self.performance_metrics["total_round_time"])
            print(f"  平均每輪耗時: {avg_round:.2f}秒")

        # 區塊鏈狀態
        print("\n區塊鏈狀態:")
        print(f"  區塊鏈長度: {self.blockchain.get_chain_length()}")
        print(f"  區塊鏈有效: {self.blockchain.validate_chain()}")

        # 工作節點註冊狀態
        print("\n工作節點註冊狀態:")
        for worker_id in self.worker_nodes.keys():
            history = self.blockchain.get_worker_history(worker_id)
            print(f"  {worker_id}: {len(history)}條記錄")
