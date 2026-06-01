# Secure Distributed Machine Learning System based on Blockchain PKI

## System Overview

This project delivers a lightweight, highly secure **distributed machine learning (DML) framework** seamlessly integrated with a **blockchain-based Public Key Infrastructure (PKI)**.

### Key Innovations

While conventional blockchain applications rely on computationally heavy Proof-of-Work (PoW) consensus algorithms, this framework reimagines the role of blockchain as a:

* **Decentralized Public Key Infrastructure (PKI)** – Managing worker node public keys without centralized authorities.
* **Immutable Audit Trail** – Permanently logging all historical model updates.
* **Trust Verification Architecture** – Safeguarding the integrity and security of the distributed network.

By storing only lightweight metadata (such as worker IDs, public keys, cryptographic model hashes, and timestamps) rather than massive, raw model weights, the blockchain drastically minimizes system overhead.

---

# Quick Start

### 1. Environment Setup

```bash
# Install required dependencies
pip install torch torchvision numpy cryptography

# Alternatively, use the requirements file
pip install -r requirements.txt

```

### 2. Running the Demo

```bash
# Navigate to the project directory
cd Distributed_Maching_Learning

# Execute the complete pipeline demo
python main.py

```

### 3. Executing Tests

```bash
# Run unit tests for blockchain functionality
python -m pytest tests/test_blockchain.py -v

# Run unit tests for cryptographic modules
python -m pytest tests/test_crypto.py -v

```

---

##  Core Concepts

### System Security Mechanisms

1. **Digital Signatures** – RSA/ECDSA-signed models
* Worker nodes use their private keys to sign updates.
* The master node verifies authenticity via the corresponding public key.
* Mitigates identity spoofing and impersonation attacks.


2. **Integrity Verification** – SHA-256 hash checks
* Detects whether model parameters have been altered during transmission.
* Any unauthorized weight modification triggers an immediate verification failure.


3. **Tamper-Resistant Auditing** – Blockchain ledger
* Records every model update permanently.
* Facilitates post-hoc auditing, forensics, and end-to-end traceability.



### Execution Workflow

```
Worker node generates a key pair
          ↓
Registers public key to the blockchain
          ↓
Receives the global model from the master node
          ↓
Trains the model locally
          ↓
Computes the cryptographic model hash
          ↓
Signs the hash using its private key
          ↓
Submits the payload to the master node
          ↓
Master node validates signature and integrity
          ↓
Aggregates only verified models
          ↓
Logs the transaction to the blockchain

```

---

##  Code Examples

### Example 1: Basic Setup

```python
from src.system import SecureDMLSystem

# Initialize system with 3 worker nodes using RSA
system = SecureDMLSystem(num_workers=3, crypto_type="rsa")

# Set up worker nodes
system.setup_workers()

# Execute training loop for 5 rounds
system.training_loop(num_rounds=5)

# Generate evaluation report
system.generate_report()

```

### Example 2: Cryptographic Key Management

```python
from src.security.crypto import SignatureManager

# Initialize signature manager
manager = SignatureManager(key_type="rsa")

# Generate a fresh key pair
private_key, public_key = manager.generate_keys()

# Sign and verify the model
model_hash, signature = manager.sign_model(model_weights, private_key)
is_valid, msg = manager.verify_model(model_weights, model_hash, signature, public_key)

```

### Example 3: Blockchain Operations

```python
from src.blockchain.blockchain import LightweightBlockchain

# Initialize the blockchain and add the genesis block
bc = LightweightBlockchain()
bc.add_genesis_block()

# Register a worker node with its public key
bc.register_worker("worker_1", public_key)

# Append a model update entry to the ledger
bc.add_model_update_record("worker_1", model_hash, {"verified": True})

# Verify the integrity of the entire chain
is_valid = bc.validate_chain()

```

---

##  Performance Metrics

The system automatically tracks and benchmarks the following:

* **Signature Generation Time** – Overhead for signing via RSA/ECDSA :
* **Signature Verification Time** – Latency for checking signatures :
* **Model Aggregation Time** – Duration of the FedAvg process :
* **Per-Round Training Time** – Total wall-clock time per epoch/round :
* **Verification Success Rate** – Ratio of successfully validated models :

---

##  Security Profiles

* **Authentication** – Powered by RSA/ECDSA signatures

* **Integrity Protection** – Enforced via SHA-256 hashing

* **Non-Repudiation** – Guaranteed by blockchain immutable logs

* **Audit Trail** – Comprehensive and traceable operational logs

* **Anomaly Detection** – Automated identification of model tampering

---

## Application Scenarios

### Federated Learning for Healthcare

Enables multiple medical institutions to collaboratively train diagnostic models while keeping sensitive patient data completely localized and private.

### Joint Risk Control in Finance

Facilitates collaborative risk assessment modeling across banking networks while preventing malicious model poisoning attacks.

### Edge Computing Collaboration

Empowers distributed IoT devices to collaboratively train global models while ensuring hardware and node authenticity.

---

##  Project Structure

```
src/
├── blockchain/blockchain.py      # Blockchain PKI implementation
├── security/crypto.py            # Cryptographic utilities & signatures
├── ml/model.py                   # Neural networks & federated learning algorithms
├── network/communication.py      # Node communication protocols
└── system.py                     # Central system orchestrator

tests/
├── test_blockchain.py            # Unit tests for blockchain functionality
└── test_crypto.py                # Unit tests for cryptographic modules

main.py                           # Main entry point

```

---

## References

* Wang, Z., Wang, Q., Yu, G., & Chen, S. (2024). TDML - A Trustworthy Distributed Machine Learning Framework.
* Subasi, Omer et al. "The Landscape of Modern Machine Learning: A Review of Machine, Distributed and Federated Learning." ArXiv abs/2312.03120 (2023).
* McMahan, B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data.
* Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system.
