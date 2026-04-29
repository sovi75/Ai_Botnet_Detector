import pandas as pd
from xgboost import XGBClassifier
import joblib
import numpy as np

print("🔄 Processing datasets for SIMPLE per-packet model...")

# 1. Load the files
benign = pd.read_csv('2.benign.csv')
udp = pd.read_csv('2.gafgyt.udp.csv')
syn = pd.read_csv('2.mirai.syn.csv')

# 2. Extract per-packet features (available from every packet)
# These are basic TCP/IP header fields
simple_features = [
    'packet_size',      # Total packet length
    'protocol',         # TCP=6, UDP=17
    'tcp_flags',        # SYN=2, ACK=16, etc.
    'payload_len'       # Data payload size
]

# Helper function to extract features from raw CSV
# Your CSVs may have different column names - let me know if errors occur
def extract_simple_features(df, label):
    result = []
    for idx, row in df.iterrows():
        # Map existing columns to our simple features
        # Adjust these based on your actual CSV columns
        packet_size = row.get('packet_size', row.get('length', row.get('size', 64)))
        protocol = row.get('protocol', row.get('proto', 6))
        tcp_flags = row.get('tcp_flags', row.get('flags', 2))
        payload_len = row.get('payload_len', row.get('data_len', 0))
        
        result.append([packet_size, protocol, tcp_flags, payload_len])
    return np.array(result)

print("📊 Extracting features from benign traffic...")
X_benign = extract_simple_features(benign, 0)
y_benign = np.zeros(len(X_benign))

print("📊 Extracting features from UDP attack...")
X_udp = extract_simple_features(udp, 1)
y_udp = np.ones(len(X_udp))

print("📊 Extracting features from SYN attack...")
X_syn = extract_simple_features(syn, 1)
y_syn = np.ones(len(X_syn))

# Combine
X = np.vstack([X_benign, X_udp, X_syn])
y = np.hstack([y_benign, y_udp, y_syn])

print(f"✅ Dataset ready: {len(X)} samples, {X.shape[1]} features")

# 3. Train model
print("🚀 Training XGBoost model...")
model = XGBClassifier(
    n_estimators=50,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)
model.fit(X, y)

# 4. Save model and features
joblib.dump(model, 'botnet_model_simple.pkl')
joblib.dump(simple_features, 'feature_names_simple.pkl')

print("✅ DONE! Saved as 'botnet_model_simple.pkl'")

# 5. Test accuracy
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
print(f"📈 Cross-validation accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")