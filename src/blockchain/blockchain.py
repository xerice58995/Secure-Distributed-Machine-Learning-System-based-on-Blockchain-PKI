"""
區塊鏈PKI基礎設施模塊
此模塊實現了輕量級的區塊鏈結構，用於管理工作節點的公鑰和審計日誌
"""

import hashlib
import json
import threading
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


@dataclass
class BlockData:
    """區塊鏈中存儲的輕量級元數據"""

    worker_id: str  # 工作節點編號
    public_key: str  # 工作節點的公鑰（PEM格式）
    model_hash: str  # 模型權重的SHA-256雜湊值
    timestamp: float  # 時間戳
    signature_metadata: Dict  # 簽名元數據
    previous_hash: str  # 前一區塊的雜湊值


class Block:
    """
    區塊鏈中的單個區塊
    每個區塊包含驗證用數據而不是完整的模型權重，避免拖累效能
    """

    def __init__(self, data: BlockData, previous_hash: str = "0"):
        """
        初始化區塊

        Args:
            data: 區塊包含的元數據
            previous_hash: 前一個區塊的雜湊值
        """
        self.data = data
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        計算區塊的SHA-256雜湊值

        Returns:
            區塊的雜湊值（十六進制字符串）
        """
        block_content = {
            "worker_id": self.data.worker_id,
            "public_key": self.data.public_key,
            "model_hash": self.data.model_hash,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_content, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """將區塊轉換為字典格式以便於序列化"""
        return {
            "data": asdict(self.data),
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "hash": self.hash,
        }


class LightweightBlockchain:
    """
    輕量級區塊鏈 - 用於PKI和審計日誌
    不使用PoW共識，而是作為分散式信任驗證基礎設施
    """

    def __init__(self):
        """初始化區塊鏈"""
        self.chain: List[Block] = []
        self.pending_data: List[BlockData] = []
        self.worker_public_keys: Dict[str, str] = {}  # 工作節點ID -> 公鑰映射
        self.lock = threading.RLock()  # 線程安全鎖

    def add_genesis_block(self):
        """創建初始區塊"""
        with self.lock:
            if len(self.chain) == 0:
                genesis_data = BlockData(
                    worker_id="GENESIS",
                    public_key="",
                    model_hash="",
                    timestamp=time.time(),
                    signature_metadata={},
                    previous_hash="0",
                )
                genesis_block = Block(genesis_data, "0")
                self.chain.append(genesis_block)

    def register_worker(self, worker_id: str, public_key: str) -> bool:
        """
        將工作節點的公鑰註冊到區塊鏈

        Args:
            worker_id: 工作節點的唯一識別碼
            public_key: 工作節點的公鑰（PEM格式）

        Returns:
            註冊是否成功
        """
        with self.lock:
            # 檢查工作節點是否已註冊
            if worker_id in self.worker_public_keys:
                return False

            # 記錄工作節點的公鑰
            self.worker_public_keys[worker_id] = public_key

            # 創建註冊記錄區塊
            registration_data = BlockData(
                worker_id=worker_id,
                public_key=public_key,
                model_hash="REGISTRATION",
                timestamp=time.time(),
                signature_metadata={"type": "registration"},
                previous_hash=self.chain[-1].hash if self.chain else "0",
            )

            block = Block(registration_data, self.chain[-1].hash if self.chain else "0")
            self.chain.append(block)
            return True

    def get_worker_public_key(self, worker_id: str) -> Optional[str]:
        """
        從區塊鏈查詢工作節點的公鑰
        這用於主節點驗證簽名時獲取公鑰

        Args:
            worker_id: 工作節點編號

        Returns:
            公鑰字符串或None（若節點未註冊）
        """
        with self.lock:
            return self.worker_public_keys.get(worker_id)

    def add_model_update_record(
        self, worker_id: str, model_hash: str, signature_metadata: Dict
    ) -> bool:
        """
        添加模型更新記錄到區塊鏈
        這創建審計日誌，記錄每個工作節點的模型提交情況

        Args:
            worker_id: 工作節點編號
            model_hash: 模型權重的雜湊值
            signature_metadata: 簽名相關的元數據

        Returns:
            添加是否成功
        """
        with self.lock:
            # 驗證工作節點是否已註冊
            if worker_id not in self.worker_public_keys:
                return False

            public_key = self.worker_public_keys[worker_id]

            # 創建模型更新記錄
            update_data = BlockData(
                worker_id=worker_id,
                public_key=public_key,
                model_hash=model_hash,
                timestamp=time.time(),
                signature_metadata=signature_metadata,
                previous_hash=self.chain[-1].hash,
            )

            block = Block(update_data, self.chain[-1].hash)
            self.chain.append(block)
            return True

    def get_worker_history(self, worker_id: str) -> List[Dict]:
        """
        獲取特定工作節點的所有更新記錄
        用於審計和追蹤節點行為

        Args:
            worker_id: 工作節點編號

        Returns:
            該工作節點的所有區塊記錄
        """
        with self.lock:
            history = []
            for block in self.chain:
                if block.data.worker_id == worker_id:
                    history.append(block.to_dict())
            return history

    def validate_chain(self) -> bool:
        """
        驗證整個區塊鏈的完整性
        確保沒有區塊被篡改

        Returns:
            區塊鏈是否有效
        """
        with self.lock:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]

                # 驗證當前區塊的雜湊值
                if current_block.hash != current_block.calculate_hash():
                    return False

                # 驗證鏈的連續性
                if current_block.previous_hash != previous_block.hash:
                    return False

            return True

    def get_chain_length(self) -> int:
        """獲取區塊鏈的長度"""
        with self.lock:
            return len(self.chain)

    def get_chain_snapshot(self) -> List[Dict]:
        """
        獲取完整的區塊鏈快照
        用於節點同步或審計

        Returns:
            所有區塊的字典表示
        """
        with self.lock:
            return [block.to_dict() for block in self.chain]

    def get_latest_block(self) -> Optional[Block]:
        """獲取區塊鏈上最新的區塊"""
        with self.lock:
            if self.chain:
                return self.chain[-1]
            return None
