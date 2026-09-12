import hashlib
import random
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch

ROOT = Path(__file__).parent.parent
DATA_PIPELINE_OUT = ROOT / "data_pipeline" / "outputs" if (ROOT / "data_pipeline" / "outputs").exists() else ROOT / "phase1" / "outputs"
ML_DATA_DIR = ROOT / "ml_engine" / "data" if (ROOT / "ml_engine" / "data").exists() else ROOT / "phase4" / "colab_data"


class TestP0WindowsSafePhase1:
    """Verify Phase 1 logging and utilities do not crash on Windows console encoding."""

    def test_utils_print_section_ascii_safe(self, capsys):
        try:
            from data_pipeline.cleaning.utils import print_section
        except ImportError:
            from phase1.utils import print_section
        print_section("TEST SECTION HEADER")
        captured = capsys.readouterr()
        assert "TEST SECTION HEADER" in captured.out
        assert all(ord(c) < 128 for c in captured.out)

    def test_utils_write_report_ascii_safe(self, tmp_path, capsys):
        try:
            from data_pipeline.cleaning.utils import write_report
        except ImportError:
            from phase1.utils import write_report
        report_file = tmp_path / "test_report.txt"
        write_report(["Line 1", "Line 2"], report_file)
        captured = capsys.readouterr()
        assert "Report saved ->" in captured.out
        assert all(ord(c) < 128 for c in captured.out)
        assert report_file.exists()


class TestP0SeverityRegeneration:
    """Verify the regenerated drugbank_ddi_cleaned.csv properties."""

    @pytest.fixture(scope="class")
    def ddi_df(self):
        csv_path = DATA_PIPELINE_OUT / "drugbank_ddi_cleaned.csv"
        assert csv_path.exists(), f"Missing {csv_path}"
        return pd.read_csv(csv_path)

    def test_severity_distribution_calibrated(self, ddi_df):
        """Verify the distribution is no longer 87.9% MAJOR."""
        counts = ddi_df["severity"].value_counts(normalize=True) * 100
        assert counts["MODERATE"] > 65.0, f"Expected MODERATE > 65%, got {counts['MODERATE']:.2f}%"
        assert counts["MAJOR"] < 30.0, f"Expected MAJOR < 30%, got {counts['MAJOR']:.2f}%"
        assert "MINOR" in counts and counts["MINOR"] > 1.0

    def test_no_missing_severities(self, ddi_df):
        assert ddi_df["severity"].isna().sum() == 0
        valid_sevs = {"MAJOR", "MODERATE", "MINOR"}
        assert set(ddi_df["severity"].unique()).issubset(valid_sevs)

    def test_no_pairwise_duplicates(self, ddi_df):
        assert ddi_df.duplicated(subset=["pair_key"]).sum() == 0

    def test_no_self_interactions(self, ddi_df):
        assert (ddi_df["drug1_norm"] == ddi_df["drug2_norm"]).sum() == 0


class TestP0ColabDataProvenance:
    """Verify colab_data/ exports match regenerated Phase 1 CSVs."""

    @pytest.fixture(scope="class")
    def colab_data(self):
        nodes = pd.read_csv(ML_DATA_DIR / "nodes.csv")
        edges = pd.read_csv(ML_DATA_DIR / "edges.csv")
        feats = pd.read_csv(ML_DATA_DIR / "node_features.csv")
        return nodes, edges, feats

    def test_node_feature_order_and_alignment(self, colab_data):
        nodes, edges, feats = colab_data
        assert len(nodes) == len(feats)
        assert (nodes["node_id"].values == feats["node_id"].values).all()
        assert (nodes["name"].values == feats["name"].values).all()

    def test_deterministic_sha256_features(self, colab_data):
        nodes, _, feats = colab_data
        for _, row in feats.head(50).iterrows():
            name = str(row["name"]).lower().strip()
            digest = hashlib.sha256(name.encode("utf-8")).digest()
            hash_val = int.from_bytes(digest[:2], byteorder="big")
            expected_bits = [(hash_val >> i) & 1 for i in range(8)]
            actual_bits = [row[f"hash_feat_{i}"] for i in range(8)]
            assert actual_bits == expected_bits

    def test_negative_sampling_zero_positive_overlap(self, colab_data):
        _, edges, _ = colab_data
        pos = edges[edges["label"] == 1]
        neg = edges[edges["label"] == 0]

        pos_pairs = set(zip(pos["node1"], pos["node2"])) | set(zip(pos["node2"], pos["node1"]))
        neg_pairs = set(zip(neg["node1"], neg["node2"])) | set(zip(neg["node2"], neg["node1"]))

        overlap = pos_pairs.intersection(neg_pairs)
        assert len(overlap) == 0, f"Found {len(overlap)} overlapping pos/neg pairs!"

    def test_no_self_edges(self, colab_data):
        _, edges, _ = colab_data
        self_edges = edges[edges["node1"] == edges["node2"]]
        assert len(self_edges) == 0, f"Found {len(self_edges)} self-edges in dataset!"


class TestP0GNNLeakageFreeSplit:
    """Verify train/val/test splits guarantee zero edge leakage into message-passing graph."""

    def test_leakage_free_edge_index_construction(self):
        edges = pd.read_csv(ML_DATA_DIR / "edges.csv")
        pos_edges = edges[edges["label"] == 1].reset_index(drop=True)
        neg_edges = edges[edges["label"] == 0].reset_index(drop=True)

        SEED = 42
        pos_shuffled = pos_edges.sample(frac=1, random_state=SEED).reset_index(drop=True)
        n_pos = len(pos_shuffled)
        n_train = int(0.70 * n_pos)
        n_val = int(0.15 * n_pos)

        pos_train = pos_shuffled.iloc[:n_train].reset_index(drop=True)
        pos_val = pos_shuffled.iloc[n_train:n_train + n_val].reset_index(drop=True)
        pos_test = pos_shuffled.iloc[n_train + n_val:].reset_index(drop=True)

        train_edge_set = set(zip(pos_train["node1"], pos_train["node2"])) | set(zip(pos_train["node2"], pos_train["node1"]))
        val_edge_set = set(zip(pos_val["node1"], pos_val["node2"])) | set(zip(pos_val["node2"], pos_val["node1"]))
        test_edge_set = set(zip(pos_test["node1"], pos_test["node2"])) | set(zip(pos_test["node2"], pos_test["node1"]))

        assert len(train_edge_set.intersection(val_edge_set)) == 0, "Leakage: Validation edges found in training graph!"
        assert len(train_edge_set.intersection(test_edge_set)) == 0, "Leakage: Test edges found in training graph!"
        assert len(val_edge_set.intersection(test_edge_set)) == 0, "Validation and Test positive edges overlap!"
