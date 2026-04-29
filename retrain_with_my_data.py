import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import joblib
from sklearn.model_selection import cross_val_score

print("🔄 Loading datasets...")

# Load your captured benign traffic
try:
    my_benign = pd.read_csv('my_benign_traffic.csv')
    print(f"✅ Your benign traffic: {len(my_benign)} packets")
except:
    print("❌ Run capture_benign.py first!")
    exit()

# Load original benign (for comparison)
original_benign = pd.read_csv('2.benign.csv')

# Load attack data
udp_attack = pd.read_csv('2.gafgyt.udp.csv')
syn_attack = pd.read_csv('2.mirai.syn.csv')

# Extract features for original benign
def extract_features(df):
    # Map to our 4 features
    features = []
    for idx, row in df.iterrows():
        size = row.get('packet_size', row.get('length', row.get('size', 64)))
        proto = row.get('protocol', row.get('proto', 6))
        flags = row.get('tcp_flags', row.get('flags', 2))
        payload = row.get('payload_len', row.get('data_len', 0))
        features.append([size, proto, flags, payload])
    return np.array(features)

# Build training data
print("📊 Building training set...")

# Your benign traffic (label 0)
X_my_benign = my_benign[['packet_size', 'protocol', 'tcp_flags', 'payload_len']].values
y_my_benign = np.zeros(len(X_my_benign))

# Original benign (label 0) - take sample to balance
X_orig_benign = extract_features(original_benign)[:5000]
y_orig_benign = np.zeros(len(X_orig_benign))

# Attacks (label 1)
X_udp = extract_features(udp_attack)[:5000]
y_udp = np.ones(len(X_udp))
X_syn = extract_features(syn_attack)[:5000]
y_syn = np.ones(len(X_syn))

# Combine
X = np.vstack([X_my_benign, X_orig_benign, X_udp, X_syn])
y = np.hstack([y_my_benign, y_orig_benign, y_udp, y_syn])

print(f"✅ Total samples: {len(X)}")
print(f"   Benign (your traffic): {len(X_my_benign)}")
print(f"   Benign (original): {len(X_orig_benign)}")
print(f"   Attack (UDP+SYN): {len(X_udp) + len(X_syn)}")

# Train
print("🚀 Training improved model...")
model = XGBClassifier(
    n_estimators=50,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)
model.fit(X, y)

# Save
joblib.dump(model, 'botnet_model_improved.pkl')
print("✅ Saved as 'botnet_model_improved.pkl'")

# Test accuracy
scores = cross_val_score(model, X, y, cv=5)
print(f"📈 Cross-validation accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")