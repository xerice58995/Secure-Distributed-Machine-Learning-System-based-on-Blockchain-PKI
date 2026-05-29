"""
安全層模塊 - 密碼學操作和簽名驗證
實現RSA/ECDSA數位簽名和SHA-256雜湊驗證
"""

import hashlib
import json
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.backends import default_backend
import numpy as np


class CryptographicManager:
    """
    密碼學管理器
    負責生成密鑰、計算雜湊值、生成和驗證簽名
    """

    # RSA密鑰長度（位）
    RSA_KEY_SIZE = 2048

    # ECDSA曲線
    ECDSA_CURVE = ec.SECP256R1()

    @staticmethod
    def generate_rsa_key_pair() -> Tuple[str, str]:
        """
        生成RSA公鑰-私鑰對

        Returns:
            (私鑰PEM字符串, 公鑰PEM字符串)
        """
        # 生成私鑰
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=CryptographicManager.RSA_KEY_SIZE,
            backend=default_backend()
        )

        # 從私鑰推導出公鑰
        public_key = private_key.public_key()

        # 將私鑰序列化為PEM格式
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # 將公鑰序列化為PEM格式
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return private_pem, public_pem

    @staticmethod
    def generate_ecdsa_key_pair() -> Tuple[str, str]:
        """
        生成ECDSA公鑰-私鑰對

        Returns:
            (私鑰PEM字符串, 公鑰PEM字符串)
        """
        # 生成私鑰
        private_key = ec.generate_private_key(
            CryptographicManager.ECDSA_CURVE,
            default_backend()
        )

        # 從私鑰推導出公鑰
        public_key = private_key.public_key()

        # 將私鑰序列化為PEM格式
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # 將公鑰序列化為PEM格式
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return private_pem, public_pem

    @staticmethod
    def compute_model_hash(model_weights: dict) -> str:
        """
        計算模型權重的SHA-256雜湊值
        這用於驗證模型的完整性

        Args:
            model_weights: 模型權重字典（通常來自PyTorch模型）

        Returns:
            十六進制格式的SHA-256雜湊值
        """
        # 將模型權重轉換為JSON字符串（確保可序列化）
        weights_json = json.dumps(
            {k: v.tolist() if isinstance(v, np.ndarray) else v
             for k, v in model_weights.items()},
            sort_keys=True
        )

        # 計算SHA-256雜湊
        hash_value = hashlib.sha256(weights_json.encode()).hexdigest()
        return hash_value

    @staticmethod
    def sign_hash_rsa(data_hash: str, private_key_pem: str) -> str:
        """
        使用RSA私鑰簽署雜湊值

        Args:
            data_hash: 要簽署的雜湊值（十六進制字符串）
            private_key_pem: RSA私鑰的PEM格式字符串

        Returns:
            簽名的十六進制編碼字符串
        """
        # 從PEM字符串加載私鑰
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

        # 簽署雜湊值
        signature = private_key.sign(
            data_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # 返回十六進制編碼的簽名
        return signature.hex()

    @staticmethod
    def sign_hash_ecdsa(data_hash: str, private_key_pem: str) -> str:
        """
        使用ECDSA私鑰簽署雜湊值

        Args:
            data_hash: 要簽署的雜湊值
            private_key_pem: ECDSA私鑰的PEM格式字符串

        Returns:
            簽名的十六進制編碼字符串
        """
        # 從PEM字符串加載私鑰
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

        # 簽署雜湊值
        signature = private_key.sign(
            data_hash.encode(),
            ec.ECDSA(hashes.SHA256())
        )

        # 返回十六進制編碼的簽名
        return signature.hex()

    @staticmethod
    def verify_signature_rsa(data_hash: str, signature_hex: str,
                           public_key_pem: str) -> bool:
        """
        使用RSA公鑰驗證簽名

        Args:
            data_hash: 原始的雜湊值（十六進制字符串）
            signature_hex: 簽名的十六進制字符串
            public_key_pem: RSA公鑰的PEM格式字符串

        Returns:
            簽名是否有效
        """
        try:
            # 從PEM字符串加載公鑰
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )

            # 將十六進制簽名轉換為字節
            signature_bytes = bytes.fromhex(signature_hex)

            # 驗證簽名
            public_key.verify(
                signature_bytes,
                data_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # 簽名有效
            return True

        except Exception as e:
            # 簽名無效或驗證失敗
            print(f"RSA簽名驗證失敗: {str(e)}")
            return False

    @staticmethod
    def verify_signature_ecdsa(data_hash: str, signature_hex: str,
                              public_key_pem: str) -> bool:
        """
        使用ECDSA公鑰驗證簽名

        Args:
            data_hash: 原始的雜湊值（十六進制字符串）
            signature_hex: 簽名的十六進制字符串
            public_key_pem: ECDSA公鑰的PEM格式字符串

        Returns:
            簽名是否有效
        """
        try:
            # 從PEM字符串加載公鑰
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )

            # 將十六進制簽名轉換為字節
            signature_bytes = bytes.fromhex(signature_hex)

            # 驗證簽名
            public_key.verify(
                signature_bytes,
                data_hash.encode(),
                ec.ECDSA(hashes.SHA256())
            )

            # 簽名有效
            return True

        except Exception as e:
            # 簽名無效或驗證失敗
            print(f"ECDSA簽名驗證失敗: {str(e)}")
            return False

    @staticmethod
    def verify_model_integrity(model_weights: dict, model_hash: str) -> bool:
        """
        驗證模型的完整性
        計算當前模型的雜湊並與預期的雜湊進行比較

        Args:
            model_weights: 模型權重字典
            model_hash: 預期的模型雜湊值

        Returns:
            模型是否完整未被篡改
        """
        # 重新計算模型雜湊
        computed_hash = CryptographicManager.compute_model_hash(model_weights)

        # 比較雜湊值
        return computed_hash == model_hash


class SignatureManager:
    """
    簽名管理器
    負責模型簽名和驗證流程的整體管理
    """

    def __init__(self, key_type: str = "rsa"):
        """
        初始化簽名管理器

        Args:
            key_type: 使用的密鑰類型 ("rsa" 或 "ecdsa")
        """
        self.key_type = key_type.lower()
        if self.key_type not in ["rsa", "ecdsa"]:
            raise ValueError("key_type必須是'rsa'或'ecdsa'")

    def generate_keys(self) -> Tuple[str, str]:
        """
        生成公鑰-私鑰對

        Returns:
            (私鑰PEM字符串, 公鑰PEM字符串)
        """
        if self.key_type == "rsa":
            return CryptographicManager.generate_rsa_key_pair()
        else:
            return CryptographicManager.generate_ecdsa_key_pair()

    def sign_model(self, model_weights: dict, private_key_pem: str) -> Tuple[str, str]:
        """
        簽署模型權重

        Args:
            model_weights: 模型權重字典
            private_key_pem: 私鑰的PEM格式字符串

        Returns:
            (模型雜湊值, 簽名)
        """
        # 計算模型雜湊
        model_hash = CryptographicManager.compute_model_hash(model_weights)

        # 簽署雜湊
        if self.key_type == "rsa":
            signature = CryptographicManager.sign_hash_rsa(model_hash, private_key_pem)
        else:
            signature = CryptographicManager.sign_hash_ecdsa(model_hash, private_key_pem)

        return model_hash, signature

    def verify_model(self, model_weights: dict, model_hash: str,
                    signature: str, public_key_pem: str) -> Tuple[bool, str]:
        """
        驗證模型簽名和完整性

        Args:
            model_weights: 模型權重字典
            model_hash: 宣稱的模型雜湊值
            signature: 模型的簽名
            public_key_pem: 公鑰的PEM格式字符串

        Returns:
            (驗證是否成功, 詳細信息)
        """
        # 首先驗證模型完整性
        if not CryptographicManager.verify_model_integrity(model_weights, model_hash):
            return False, "模型完整性驗證失敗：權重被篡改"

        # 驗證簽名
        if self.key_type == "rsa":
            signature_valid = CryptographicManager.verify_signature_rsa(
                model_hash, signature, public_key_pem
            )
        else:
            signature_valid = CryptographicManager.verify_signature_ecdsa(
                model_hash, signature, public_key_pem
            )

        if not signature_valid:
            return False, "簽名驗證失敗：簽名無效或不匹配"

        return True, "驗證成功：模型已驗證"
