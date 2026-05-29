"""
單元測試 - 密碼學功能
"""

import unittest
import numpy as np
from src.security.crypto import CryptographicManager, SignatureManager


class TestCryptography(unittest.TestCase):
    """測試密碼學功能"""

    def test_rsa_key_generation(self):
        """測試RSA密鑰生成"""
        private_key, public_key = CryptographicManager.generate_rsa_key_pair()

        # 檢查密鑰格式
        self.assertIn("BEGIN RSA PRIVATE KEY", private_key)
        self.assertIn("BEGIN PUBLIC KEY", public_key)
        self.assertNotEqual(private_key, public_key)

    def test_ecdsa_key_generation(self):
        """測試ECDSA密鑰生成"""
        private_key, public_key = CryptographicManager.generate_ecdsa_key_pair()

        # 檢查密鑰格式
        self.assertIn("BEGIN EC PRIVATE KEY", private_key)
        self.assertIn("BEGIN PUBLIC KEY", public_key)
        self.assertNotEqual(private_key, public_key)

    def test_model_hash_computation(self):
        """測試模型雜湊計算"""
        # 創建測試模型權重
        model_weights = {
            "fc1.weight": np.random.randn(128, 784),
            "fc1.bias": np.random.randn(128),
            "fc2.weight": np.random.randn(10, 128),
            "fc2.bias": np.random.randn(10)
        }

        # 計算雜湊
        hash1 = CryptographicManager.compute_model_hash(model_weights)

        # 雜湊應該是十六進制字符串
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA-256的十六進制長度

        # 相同的模型應該產生相同的雜湊
        hash2 = CryptographicManager.compute_model_hash(model_weights)
        self.assertEqual(hash1, hash2)

        # 修改模型應該產生不同的雜湊
        model_weights["fc1.bias"] = np.random.randn(128)
        hash3 = CryptographicManager.compute_model_hash(model_weights)
        self.assertNotEqual(hash1, hash3)

    def test_rsa_signature_verification(self):
        """測試RSA簽名驗證"""
        # 生成密鑰對
        private_key, public_key = CryptographicManager.generate_rsa_key_pair()

        # 要簽署的數據
        data_hash = "abc123def456"

        # 簽署數據
        signature = CryptographicManager.sign_hash_rsa(data_hash, private_key)

        # 驗證簽名
        is_valid = CryptographicManager.verify_signature_rsa(
            data_hash, signature, public_key
        )
        self.assertTrue(is_valid)

        # 修改後的簽名應該驗證失敗
        modified_signature = signature[:-10] + "0" * 10
        is_valid = CryptographicManager.verify_signature_rsa(
            data_hash, modified_signature, public_key
        )
        self.assertFalse(is_valid)

        # 不同的數據應該驗證失敗
        different_hash = "different_hash"
        is_valid = CryptographicManager.verify_signature_rsa(
            different_hash, signature, public_key
        )
        self.assertFalse(is_valid)

    def test_ecdsa_signature_verification(self):
        """測試ECDSA簽名驗證"""
        # 生成密鑰對
        private_key, public_key = CryptographicManager.generate_ecdsa_key_pair()

        # 要簽署的數據
        data_hash = "test_data_hash"

        # 簽署數據
        signature = CryptographicManager.sign_hash_ecdsa(data_hash, private_key)

        # 驗證簽名
        is_valid = CryptographicManager.verify_signature_ecdsa(
            data_hash, signature, public_key
        )
        self.assertTrue(is_valid)

        # 修改後的簽名應該驗證失敗
        modified_signature = signature[:-10] + "0" * 10
        is_valid = CryptographicManager.verify_signature_ecdsa(
            data_hash, modified_signature, public_key
        )
        self.assertFalse(is_valid)

    def test_signature_manager_rsa(self):
        """測試RSA簽名管理器"""
        manager = SignatureManager(key_type="rsa")

        # 生成密鑰
        private_key, public_key = manager.generate_keys()

        # 創建模型
        model_weights = {
            "layer1": np.random.randn(10, 10),
            "layer2": np.random.randn(5, 10)
        }

        # 簽署模型
        model_hash, signature = manager.sign_model(model_weights, private_key)

        # 驗證模型
        is_valid, message = manager.verify_model(
            model_weights, model_hash, signature, public_key
        )
        self.assertTrue(is_valid)

    def test_signature_manager_ecdsa(self):
        """測試ECDSA簽名管理器"""
        manager = SignatureManager(key_type="ecdsa")

        # 生成密鑰
        private_key, public_key = manager.generate_keys()

        # 創建模型
        model_weights = {
            "layer1": np.random.randn(10, 10),
            "layer2": np.random.randn(5, 10)
        }

        # 簽署模型
        model_hash, signature = manager.sign_model(model_weights, private_key)

        # 驗證模型
        is_valid, message = manager.verify_model(
            model_weights, model_hash, signature, public_key
        )
        self.assertTrue(is_valid)

    def test_model_integrity_verification(self):
        """測試模型完整性驗證"""
        # 創建模型
        model_weights = {
            "weight": np.array([[1.0, 2.0], [3.0, 4.0]]),
            "bias": np.array([0.1, 0.2])
        }

        # 計算正確的雜湊
        correct_hash = CryptographicManager.compute_model_hash(model_weights)

        # 驗證應該通過
        is_intact = CryptographicManager.verify_model_integrity(
            model_weights, correct_hash
        )
        self.assertTrue(is_intact)

        # 修改模型後，驗證應該失敗
        model_weights["weight"] = np.array([[1.0, 2.0], [3.0, 5.0]])
        is_intact = CryptographicManager.verify_model_integrity(
            model_weights, correct_hash
        )
        self.assertFalse(is_intact)

    def test_invalid_key_type(self):
        """測試無效的密鑰類型"""
        # 應該拋出ValueError
        with self.assertRaises(ValueError):
            SignatureManager(key_type="invalid")


if __name__ == "__main__":
    unittest.main()
