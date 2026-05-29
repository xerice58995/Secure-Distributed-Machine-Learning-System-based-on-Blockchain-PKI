"""
主程序
展示完整的安全分布式機器學習系統的使用
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.system import SecureDMLSystem


def main():
    """
    主函數
    演示系統的完整功能
    """

    # 創建系統實例（3個工作節點，使用RSA加密）
    system = SecureDMLSystem(
        num_workers=3,
        crypto_type="rsa",
        device="cpu"
    )

    # 第一步：設置工作節點
    print("\n" + "="*70)
    print("步驟1: 工作節點註冊")
    print("="*70)
    system.setup_workers()

    # 第二步：執行訓練循環
    print("\n" + "="*70)
    print("步驟2: 執行訓練循環")
    print("="*70)
    system.training_loop(num_rounds=2)

    # 第三步：演示惡意節點檢測
    print("\n" + "="*70)
    print("步驟3: 演示安全性 - 惡意節點檢測")
    print("="*70)
    system.simulate_attack_detection()

    # 第四步：生成報告
    print("\n" + "="*70)
    print("步驟4: 生成系統報告")
    print("="*70)
    system.generate_report()

    print("\n" + "="*70)
    print("演示完成")
    print("="*70)


if __name__ == "__main__":
    main()
