"""
網絡層模塊 - 節點間通訊
實現主節點和工作節點之間的通訊協議
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import threading
from abc import ABC, abstractmethod


@dataclass
class MessagePayload:
    """
    通訊消息載體
    用於主節點和工作節點之間的數據交換
    """
    message_type: str              # 消息類型（"register", "distribute", "submit", "aggregate"等）
    sender_id: str                 # 發送者編號
    receiver_id: str               # 接收者編號
    timestamp: float               # 時間戳
    data: Dict[str, Any]          # 具體數據


class NetworkNode(ABC):
    """
    網絡節點基類
    定義節點的基本通訊介面
    """

    def __init__(self, node_id: str):
        """
        初始化網絡節點

        Args:
            node_id: 節點的唯一編號
        """
        self.node_id = node_id
        self.message_queue: List[MessagePayload] = []
        self.lock = threading.RLock()

    @abstractmethod
    def send_message(self, message: MessagePayload) -> bool:
        """
        發送消息

        Args:
            message: 要發送的消息

        Returns:
            是否發送成功
        """
        pass

    @abstractmethod
    def receive_message(self) -> Optional[MessagePayload]:
        """
        接收消息

        Returns:
            接收到的消息或None
        """
        pass


class LocalCommunicationBus:
    """
    本地通訊總線
    在單機模擬中用於節點間通訊
    """

    def __init__(self):
        """初始化通訊總線"""
        self.nodes: Dict[str, NetworkNode] = {}
        self.lock = threading.RLock()

    def register_node(self, node: NetworkNode):
        """
        註冊節點到通訊總線

        Args:
            node: 要註冊的節點
        """
        with self.lock:
            self.nodes[node.node_id] = node

    def deliver_message(self, message: MessagePayload) -> bool:
        """
        遞送消息給目標節點

        Args:
            message: 要遞送的消息

        Returns:
            是否遞送成功
        """
        with self.lock:
            receiver_id = message.receiver_id
            if receiver_id in self.nodes:
                # 將消息放入接收者的隊列
                receiver = self.nodes[receiver_id]
                with receiver.lock:
                    receiver.message_queue.append(message)
                return True
            return False


class WorkerNode(NetworkNode):
    """
    工作節點
    執行本地訓練，簽署模型，並向主節點提交更新
    """

    def __init__(self, node_id: str, comm_bus: LocalCommunicationBus):
        """
        初始化工作節點

        Args:
            node_id: 節點編號
            comm_bus: 通訊總線參考
        """
        super().__init__(node_id)
        self.comm_bus = comm_bus
        self.master_id = "master"

    def send_message(self, message: MessagePayload) -> bool:
        """
        發送消息到主節點或其他節點

        Args:
            message: 要發送的消息

        Returns:
            是否發送成功
        """
        return self.comm_bus.deliver_message(message)

    def receive_message(self) -> Optional[MessagePayload]:
        """
        接收消息

        Returns:
            接收到的消息或None
        """
        with self.lock:
            if self.message_queue:
                return self.message_queue.pop(0)
            return None

    def submit_model_update(self, model_weights: Dict,
                           model_hash: str,
                           signature: str,
                           private_key: str) -> bool:
        """
        提交簽署的模型更新到主節點

        Args:
            model_weights: 模型權重
            model_hash: 模型雜湊值
            signature: 數位簽名
            private_key: 工作節點的私鑰（用於追蹤）

        Returns:
            是否提交成功
        """
        # 創建模型提交消息
        message = MessagePayload(
            message_type="model_submit",
            sender_id=self.node_id,
            receiver_id=self.master_id,
            timestamp=time.time(),
            data={
                "model_weights": {k: v.tolist() if hasattr(v, 'tolist') else v
                                for k, v in model_weights.items()},
                "model_hash": model_hash,
                "signature": signature,
                "epoch": 0  # 可由調用者設置
            }
        )

        return self.send_message(message)

    def receive_global_model(self) -> Optional[Dict]:
        """
        接收主節點發送的全局模型

        Returns:
            模型權重字典或None
        """
        message = self.receive_message()
        if message and message.message_type == "model_distribute":
            return message.data.get("model_weights")
        return None


class MasterNode(NetworkNode):
    """
    主節點
    負責模型分發、簽名驗證、模型聚合
    """

    def __init__(self, node_id: str = "master",
                 comm_bus: Optional[LocalCommunicationBus] = None):
        """
        初始化主節點

        Args:
            node_id: 節點編號（通常為"master"）
            comm_bus: 通訊總線參考
        """
        super().__init__(node_id)
        self.comm_bus = comm_bus
        self.worker_ids: List[str] = []
        self.verification_results: Dict[str, Dict] = {}

    def send_message(self, message: MessagePayload) -> bool:
        """
        發送消息到工作節點

        Args:
            message: 要發送的消息

        Returns:
            是否發送成功
        """
        if self.comm_bus:
            return self.comm_bus.deliver_message(message)
        return False

    def receive_message(self) -> Optional[MessagePayload]:
        """
        接收消息

        Returns:
            接收到的消息或None
        """
        with self.lock:
            if self.message_queue:
                return self.message_queue.pop(0)
            return None

    def register_workers(self, worker_ids: List[str]):
        """
        註冊工作節點列表

        Args:
            worker_ids: 工作節點編號列表
        """
        self.worker_ids = worker_ids

    def distribute_model(self, model_weights: Dict) -> Dict[str, bool]:
        """
        向所有工作節點分發全局模型

        Args:
            model_weights: 要分發的全局模型權重

        Returns:
            每個工作節點的分發狀態
        """
        delivery_status = {}

        # 向每個工作節點發送模型
        for worker_id in self.worker_ids:
            message = MessagePayload(
                message_type="model_distribute",
                sender_id=self.node_id,
                receiver_id=worker_id,
                timestamp=time.time(),
                data={
                    "model_weights": {k: v.tolist() if hasattr(v, 'tolist') else v
                                    for k, v in model_weights.items()},
                    "round": 0  # 訓練輪數，可由調用者設置
                }
            )

            success = self.send_message(message)
            delivery_status[worker_id] = success

        return delivery_status

    def collect_model_updates(self, timeout: float = 30.0) -> List[Dict]:
        """
        收集所有工作節點提交的模型更新

        Args:
            timeout: 等待超時時間（秒）

        Returns:
            收集到的模型更新列表
        """
        start_time = time.time()
        collected_updates = []
        received_count = 0
        expected_count = len(self.worker_ids)

        # 循環接收消息直到超時或收集完整
        while time.time() - start_time < timeout and received_count < expected_count:
            message = self.receive_message()
            if message and message.message_type == "model_submit":
                # 將模型更新添加到列表
                update_data = message.data.copy()
                update_data["sender_id"] = message.sender_id
                collected_updates.append(update_data)
                received_count += 1
            else:
                # 短暫延遲以避免忙輪詢
                time.sleep(0.01)

        return collected_updates

    def record_verification_result(self, worker_id: str,
                                  is_valid: bool,
                                  details: str,
                                  model_hash: Optional[str] = None):
        """
        記錄模型驗證結果
        用於審計和監控

        Args:
            worker_id: 工作節點編號
            is_valid: 驗證是否通過
            details: 驗證詳細信息
            model_hash: 模型雜湊值
        """
        self.verification_results[worker_id] = {
            "is_valid": is_valid,
            "details": details,
            "model_hash": model_hash,
            "timestamp": time.time()
        }

    def get_verification_report(self) -> Dict[str, Any]:
        """
        獲取驗證報告
        用於分析系統安全性

        Returns:
            驗證報告字典
        """
        total_submissions = len(self.verification_results)
        valid_submissions = sum(1 for result in self.verification_results.values()
                              if result["is_valid"])

        return {
            "total_submissions": total_submissions,
            "valid_submissions": valid_submissions,
            "invalid_submissions": total_submissions - valid_submissions,
            "verification_rate": (valid_submissions / total_submissions * 100)
                               if total_submissions > 0 else 0,
            "details": self.verification_results
        }
