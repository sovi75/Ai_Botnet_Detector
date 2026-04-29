import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import joblib
from sklearn.model_selection import cross_val_score
from sklearn.utils import resample

print("🔄 Loading datasets...")

# Load your benign traffic
my_benign = pd.read_csv('my_benign_traffic.csv')
print(f"✅ Your benign traffic: {len(my_benign)} packets")

# Load attack data
udp_attack = pd.read_csv('2.gafgyt.udp.csv')
syn_attack = pd.read_csv('2.mirai.syn.csv')

# Extract features from attacks
def extract_attack_features(df, max_samples=2000):
    features = []
    for idx, row in df.iterrows():
        if idx >= max_samples:
            break
        size = row.get('packet_size', row.get('length', row.get('size', 64)))
        proto = row.get('protocol', row.get('proto', 6))
        flags = row.get('tcp_flags', row.get('flags', 2))
        payload = row.get('payload_len', row.get('data_len', 0))
        features.append([size, proto, flags, payload])
    return np.array(features)

# Balance the dataset - take equal samples from each class
BALANCED_SIZE = min(len(my_benign), 2000)

# Benign: your traffic
X_benign = my_benign[['packet_size', 'protocol', 'tcp_flags', 'payload_len']].values
if len(X_benign) > BALANCED_SIZE:
    X_benign = resample(X_benign, n_samples=BALANCED_SIZE, random_state=42)
y_benign = np.zeros(len(X_benign))

# Attack: balanced sample
X_udp = extract_attack_features(udp_attack, BALANCED_SIZE // 2)
X_syn = extract_attack_features(syn_attack, BALANCED_SIZE // 2)
X_attack = np.vstack([X_udp, X_syn])
y_attack = np.ones(len(X_attack))

# Combine balanced datasets
X = np.vstack([X_benign, X_attack])
y = np.hstack([y_benign, y_attack])

print(f"📊 Balanced dataset:")
print(f"   Benign samples: {len(X_benign)}")
print(f"   Attack samples: {len(X_attack)}")
print(f"   Total: {len(X)}")

# Train
print("🚀 Training balanced model...")
model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.15,
    random_state=42,
    scale_pos_weight=1  # Balanced classes
)
model.fit(X, y)

# Save
joblib.dump(model, 'botnet_model_balanced.pkl')
print("✅ Saved as 'botnet_model_balanced.pkl'")

# Test
scores = cross_val_score(model, X, y, cv=5)
print(f"📈 Cross-validation accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")

# Feature importance
print("\n📊 Feature importance:")
for i, feat in enumerate(['packet_size', 'protocol', 'tcp_flags', 'payload_len']):
    print(f"   {feat}: {model.feature_importances_[i]:.3f}")