"""
單元測試 - 區塊鏈PKI功能
"""

import unittest
from src.blockchain.blockchain import LightweightBlockchain, BlockData


class TestBlockchain(unittest.TestCase):
    """測試區塊鏈功能"""

    def setUp(self):
        """測試前設置"""
        self.blockchain = LightweightBlockchain()
        self.blockchain.add_genesis_block()

    def test_add_genesis_block(self):
        """測試創世區塊"""
        # 區塊鏈應該有一個區塊
        self.assertEqual(self.blockchain.get_chain_length(), 1)

    def test_register_worker(self):
        """測試工作節點註冊"""
        # 註冊一個工作節點
        success = self.blockchain.register_worker(
            "worker_1",
            "-----BEGIN PUBLIC KEY-----\ntest_key\n-----END PUBLIC KEY-----"
        )
        self.assertTrue(success)

        # 重複註冊應該失敗
        success = self.blockchain.register_worker(
            "worker_1",
            "-----BEGIN PUBLIC KEY-----\ntest_key2\n-----END PUBLIC KEY-----"
        )
        self.assertFalse(success)

    def test_get_worker_public_key(self):
        """測試獲取工作節點公鑰"""
        test_key = "-----BEGIN PUBLIC KEY-----\ntest_key\n-----END PUBLIC KEY-----"
        self.blockchain.register_worker("worker_1", test_key)

        # 應該能夠檢索正確的公鑰
        retrieved_key = self.blockchain.get_worker_public_key("worker_1")
        self.assertEqual(retrieved_key, test_key)

        # 未註冊的工作節點應該返回None
        retrieved_key = self.blockchain.get_worker_public_key("worker_nonexistent")
        self.assertIsNone(retrieved_key)

    def test_add_model_update_record(self):
        """測試添加模型更新記錄"""
        # 先註冊一個工作節點
        self.blockchain.register_worker(
            "worker_1",
            "-----BEGIN PUBLIC KEY-----\ntest_key\n-----END PUBLIC KEY-----"
        )

        # 添加模型更新記錄
        success = self.blockchain.add_model_update_record(
            "worker_1",
            "model_hash_123",
            {"signature_valid": True}
        )
        self.assertTrue(success)

        # 嘗試為未註冊的工作節點添加記錄應該失敗
        success = self.blockchain.add_model_update_record(
            "worker_nonexistent",
            "model_hash_456",
            {"signature_valid": True}
        )
        self.assertFalse(success)

    def test_validate_chain(self):
        """測試區塊鏈驗證"""
        # 添加幾個工作節點
        for i in range(3):
            self.blockchain.register_worker(
                f"worker_{i}",
                f"-----BEGIN PUBLIC KEY-----\nkey_{i}\n-----END PUBLIC KEY-----"
            )

        # 區塊鏈應該是有效的
        self.assertTrue(self.blockchain.validate_chain())

    def test_worker_history(self):
        """測試工作節點歷史記錄"""
        # 註冊並添加多個記錄
        self.blockchain.register_worker(
            "worker_1",
            "-----BEGIN PUBLIC KEY-----\ntest_key\n-----END PUBLIC KEY-----"
        )

        # 添加模型更新
        for i in range(3):
            self.blockchain.add_model_update_record(
                "worker_1",
                f"model_hash_{i}",
                {"update_number": i}
            )

        # 獲取歷史
        history = self.blockchain.get_worker_history("worker_1")

        # 應該有4條記錄（1個註冊 + 3個更新）
        self.assertEqual(len(history), 4)


if __name__ == "__main__":
    unittest.main()
