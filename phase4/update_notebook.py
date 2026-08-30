import json
from pathlib import Path

nb_path = Path("phase4/MP.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 4: Leakage-free train/val/test splitting
nb["cells"][4]["source"] = [
    "# Deterministic Seed & Leakage-Free Train/Val/Test Split\n",
    "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
    "\n",
    "SEED = 42\n",
    "random.seed(SEED)\n",
    "np.random.seed(SEED)\n",
    "torch.manual_seed(SEED)\n",
    "if torch.cuda.is_available():\n",
    "    torch.cuda.manual_seed_all(SEED)\n",
    "    torch.backends.cudnn.deterministic = True\n",
    "\n",
    "# 1. Split positive edges (70% train, 15% val, 15% test)\n",
    "pos_edges_shuffled = pos_edges.sample(frac=1, random_state=SEED).reset_index(drop=True)\n",
    "n_pos = len(pos_edges_shuffled)\n",
    "n_pos_train = int(0.70 * n_pos)\n",
    "n_pos_val   = int(0.15 * n_pos)\n",
    "\n",
    "pos_train = pos_edges_shuffled.iloc[:n_pos_train].reset_index(drop=True)\n",
    "pos_val   = pos_edges_shuffled.iloc[n_pos_train:n_pos_train + n_pos_val].reset_index(drop=True)\n",
    "pos_test  = pos_edges_shuffled.iloc[n_pos_train + n_pos_val:].reset_index(drop=True)\n",
    "\n",
    "# 2. Split negative edges (70% train, 15% val, 15% test)\n",
    "neg_edges_shuffled = neg_edges.sample(frac=1, random_state=SEED).reset_index(drop=True)\n",
    "n_neg = len(neg_edges_shuffled)\n",
    "n_neg_train = int(0.70 * n_neg)\n",
    "n_neg_val   = int(0.15 * n_neg)\n",
    "\n",
    "neg_train = neg_edges_shuffled.iloc[:n_neg_train].reset_index(drop=True)\n",
    "neg_val   = neg_edges_shuffled.iloc[n_neg_train:n_neg_train + n_neg_val].reset_index(drop=True)\n",
    "neg_test  = neg_edges_shuffled.iloc[n_neg_train + n_neg_val:].reset_index(drop=True)\n",
    "\n",
    "# 3. Build evaluation candidate pairs for each split\n",
    "train_df = pd.concat([pos_train, neg_train], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)\n",
    "val_df   = pd.concat([pos_val, neg_val], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)\n",
    "test_df  = pd.concat([pos_test, neg_test], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)\n",
    "\n",
    "X_train = train_df[[\"node1\", \"node2\"]].values\n",
    "y_train = train_df[\"label\"].values\n",
    "\n",
    "X_val   = val_df[[\"node1\", \"node2\"]].values\n",
    "y_val   = val_df[\"label\"].values\n",
    "\n",
    "X_test  = test_df[[\"node1\", \"node2\"]].values\n",
    "y_test  = test_df[\"label\"].values\n",
    "\n",
    "print(f\"Train candidate pairs : {len(X_train):,} (pos: {len(pos_train):,}, neg: {len(neg_train):,})\")\n",
    "print(f\"Val candidate pairs   : {len(X_val):,} (pos: {len(pos_val):,}, neg: {len(neg_val):,})\")\n",
    "print(f\"Test candidate pairs  : {len(X_test):,} (pos: {len(pos_test):,}, neg: {len(neg_test):,})\")\n",
    "print(f\"Positive rates -> Train: {y_train.mean():.2%}, Val: {y_val.mean():.2%}, Test: {y_test.mean():.2%}\")\n",
]

# Cell 5: Build PyTorch Geometric Data object with LEAKAGE-FREE message-passing edge index
nb["cells"][5]["source"] = [
    "# Construct LEAKAGE-FREE message-passing edge index from pos_train ONLY\n",
    "# Validation and test positive edges are strictly excluded from message passing.\n",
    "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
    "\n",
    "train_edge_index = torch.tensor(\n",
    "    [pos_train[\"node1\"].tolist() + pos_train[\"node2\"].tolist(),\n",
    "     pos_train[\"node2\"].tolist() + pos_train[\"node1\"].tolist()],\n",
    "    dtype=torch.long\n",
    ").to(device)\n",
    "\n",
    "# Compute degree feature strictly from positive training edges\n",
    "train_degree = torch.zeros(num_nodes)\n",
    "for _, row in pos_train.iterrows():\n",
    "    train_degree[int(row[\"node1\"])] += 1\n",
    "    train_degree[int(row[\"node2\"])] += 1\n",
    "if train_degree.max() > 0:\n",
    "    train_degree = (train_degree / train_degree.max()).unsqueeze(1)\n",
    "else:\n",
    "    train_degree = train_degree.unsqueeze(1)\n",
    "\n",
    "# Node feature matrix: SHA-256 features + train degree\n",
    "feat_cols = [c for c in features_df.columns if c not in [\"node_id\", \"name\"]]\n",
    "x_base = torch.tensor(features_df[feat_cols].values, dtype=torch.float)\n",
    "x = torch.cat([x_base, train_degree], dim=1).to(device)\n",
    "\n",
    "graph_data = Data(x=x, edge_index=train_edge_index).to(device)\n",
    "\n",
    "print(f\"Node feature matrix shape: {graph_data.x.shape}\")\n",
    "print(f\"Leakage-Free Training Graph: {graph_data}\")\n",
    "print(f\"Message-passing directed edges: {graph_data.edge_index.shape[1]:,} (derived strictly from {len(pos_train):,} pos_train edges)\")\n",
]

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Successfully updated phase4/MP.ipynb with leakage-free splits!")
