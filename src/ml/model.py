"""
機器學習層模塊
實現輕量級的神經網絡模型和聯邦學習相關功能
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Subset
import numpy as np
from typing import Dict, List, Tuple, Optional
import copy


class SimpleMLP(nn.Module):
    """
    簡單的多層感知機(MLP)
    用於MNIST手寫數字識別任務
    """

    def __init__(self, input_size: int = 784, hidden_size: int = 128,
                 num_classes: int = 10):
        """
        初始化MLP網絡

        Args:
            input_size: 輸入層大小（MNIST為784=28*28）
            hidden_size: 隱藏層大小
            num_classes: 輸出類別數（MNIST為10個數字）
        """
        super(SimpleMLP, self).__init__()

        # 第一層：輸入層 -> 隱藏層
        self.fc1 = nn.Linear(input_size, hidden_size)
        # ReLU激活函數
        self.relu = nn.ReLU()
        # 第二層：隱藏層 -> 輸出層
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向傳播

        Args:
            x: 輸入張量

        Returns:
            輸出張量（未進行softmax，用於交叉熵損失）
        """
        # 展平輸入
        x = x.view(x.size(0), -1)
        # 第一層
        x = self.fc1(x)
        x = self.relu(x)
        # 第二層
        x = self.fc2(x)
        return x

    def get_weights_dict(self) -> Dict[str, np.ndarray]:
        """
        獲取模型的權重字典（轉換為numpy格式）
        用於簽名和序列化

        Returns:
            模型權重字典
        """
        weights = {}
        for name, param in self.named_parameters():
            weights[name] = param.data.cpu().numpy()
        return weights

    def set_weights_dict(self, weights: Dict[str, np.ndarray]):
        """
        從權重字典設置模型參數
        用於模型聚合後更新

        Args:
            weights: 模型權重字典
        """
        for name, param in self.named_parameters():
            if name in weights:
                param.data = torch.from_numpy(weights[name]).to(param.device)


class LocalTrainer:
    """
    本地訓練器
    每個工作節點使用此類進行本地模型訓練
    """

    def __init__(self, model: nn.Module, device: str = "cpu"):
        """
        初始化訓練器

        Args:
            model: PyTorch模型
            device: 計算設備（"cpu"或"cuda"）
        """
        self.model = model.to(device)
        self.device = device
        # 交叉熵損失函數（用於多分類任務）
        self.criterion = nn.CrossEntropyLoss()

    def train_epoch(self, train_loader: DataLoader,
                   learning_rate: float = 0.01) -> float:
        """
        訓練一個epoch（一輪完整的訓練數據）

        Args:
            train_loader: 訓練數據加載器
            learning_rate: 學習率

        Returns:
            平均損失值
        """
        # 將模型設置為訓練模式
        self.model.train()

        # 優化器（使用隨機梯度下降）
        optimizer = optim.SGD(self.model.parameters(), lr=learning_rate)

        total_loss = 0.0
        num_batches = 0

        # 遍歷訓練數據
        for images, labels in train_loader:
            # 將數據移動到指定設備
            images = images.to(self.device)
            labels = labels.to(self.device)

            # 前向傳播
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            # 反向傳播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        # 返回平均損失
        average_loss = total_loss / num_batches if num_batches > 0 else 0.0
        return average_loss

    def evaluate(self, test_loader: DataLoader) -> Tuple[float, float]:
        """
        評估模型性能

        Args:
            test_loader: 測試數據加載器

        Returns:
            (準確度百分比, 平均損失)
        """
        # 將模型設置為評估模式
        self.model.eval()

        total_loss = 0.0
        correct = 0
        total = 0

        # 不計算梯度以加快推理速度
        with torch.no_grad():
            for images, labels in test_loader:
                # 將數據移動到指定設備
                images = images.to(self.device)
                labels = labels.to(self.device)

                # 前向傳播
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

                total_loss += loss.item()

                # 獲取預測結果
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        # 計算準確度百分比
        accuracy = 100.0 * correct / total if total > 0 else 0.0
        average_loss = total_loss / len(test_loader) if len(test_loader) > 0 else 0.0

        return accuracy, average_loss


class FederatedAveraging:
    """
    聯邦平均(FedAvg)演算法
    用於在主節點上聚合所有工作節點的模型更新
    """

    @staticmethod
    def aggregate_models(model_list: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """
        聚合多個模型的權重
        計算所有驗證通過的模型的平均值

        Args:
            model_list: 工作節點模型權重字典列表

        Returns:
            聚合後的平均權重
        """
        if not model_list:
            return {}

        # 初始化聚合權重
        aggregated = None

        # 遍歷所有模型
        for model_weights in model_list:
            if aggregated is None:
                # 第一個模型作為初始值
                aggregated = {k: v.copy() for k, v in model_weights.items()}
            else:
                # 將所有模型的權重累加
                for key in aggregated:
                    if key in model_weights:
                        aggregated[key] += model_weights[key]

        # 計算平均值（除以模型數量）
        num_models = len(model_list)
        for key in aggregated:
            aggregated[key] = aggregated[key] / num_models

        return aggregated

    @staticmethod
    def weighted_aggregate_models(model_list: List[Dict[str, np.ndarray]],
                                  weights: Optional[List[float]] = None
                                  ) -> Dict[str, np.ndarray]:
        """
        帶權重的模型聚合
        根據權重對不同工作節點的模型進行加權平均

        Args:
            model_list: 工作節點模型權重字典列表
            weights: 權重列表（None表示均勻權重）

        Returns:
            聚合後的加權平均權重
        """
        if not model_list:
            return {}

        # 如果未提供權重，使用均勻權重
        if weights is None:
            weights = [1.0 / len(model_list)] * len(model_list)
        else:
            # 歸一化權重
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]

        # 初始化聚合權重
        aggregated = None

        # 使用加權求和
        for model_weights, weight in zip(model_list, weights):
            if aggregated is None:
                aggregated = {k: v.copy() * weight for k, v in model_weights.items()}
            else:
                for key in aggregated:
                    if key in model_weights:
                        aggregated[key] += model_weights[key] * weight

        return aggregated


class DataPartitioner:
    """
    數據分割器
    將MNIST數據集分割給多個工作節點（Non-IID分布）
    """

    @staticmethod
    def non_iid_partition(dataset, num_partitions: int,
                         concentration: float = 0.5) -> List[Subset]:
        """
        將數據集進行Non-IID分割
        每個工作節點只包含特定類別的數據，模擬實際分布不均勻的場景

        Args:
            dataset: 原始數據集
            num_partitions: 分割數量（工作節點數）
            concentration: 集中度參數（0-1之間，越高越集中）

        Returns:
            分割後的數據集列表
        """
        # 獲取所有樣本的標籤
        targets = np.array(dataset.targets)
        num_classes = len(np.unique(targets))

        # 為每個分割分配類別
        partitions = [[] for _ in range(num_partitions)]
        class_indices = {i: np.where(targets == i)[0] for i in range(num_classes)}

        # 分配數據
        for class_idx in range(num_classes):
            # 隨機排列該類別的所有樣本
            indices = class_indices[class_idx]
            np.random.shuffle(indices)

            # 根據集中度分配給工作節點
            samples_per_node = len(indices) // num_partitions
            for node_idx in range(num_partitions):
                # 每個節點主要獲得特定類別的數據
                start = node_idx * samples_per_node
                end = start + samples_per_node
                if node_idx == num_partitions - 1:
                    end = len(indices)

                partitions[node_idx].extend(indices[start:end])

        # 將索引列表轉換為Subset對象
        result = []
        for partition_indices in partitions:
            partition_indices = np.array(partition_indices)
            result.append(Subset(dataset, partition_indices))

        return result

    @staticmethod
    def iid_partition(dataset, num_partitions: int) -> List[Subset]:
        """
        將數據集進行IID分割
        隨機均勻分配數據給所有工作節點

        Args:
            dataset: 原始數據集
            num_partitions: 分割數量

        Returns:
            分割後的數據集列表
        """
        num_samples = len(dataset)
        indices = np.random.permutation(num_samples)
        samples_per_partition = num_samples // num_partitions

        partitions = []
        for i in range(num_partitions):
            start = i * samples_per_partition
            end = start + samples_per_partition if i < num_partitions - 1 else num_samples
            partition_indices = indices[start:end]
            partitions.append(Subset(dataset, partition_indices))

        return partitions
