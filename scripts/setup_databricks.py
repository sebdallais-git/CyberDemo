"""Populate a Databricks workspace with pharma demo data.

Creates Unity Catalog objects, MLflow experiments with runs, and a
drug-discovery notebook so the workspace looks realistic when opened
during the AI Factory demo scenario.

Uses the Databricks REST API via httpx — no SDK dependency.

Usage (run from project root):
    python scripts/setup_databricks.py              # Full setup
    python scripts/setup_databricks.py --catalog     # Unity Catalog only
    python scripts/setup_databricks.py --experiments  # MLflow experiments only
    python scripts/setup_databricks.py --notebook     # Notebook only
"""

from __future__ import annotations

import argparse
import base64
import json
import random
import sys
import time
from pathlib import Path

# Add project root so we can import app.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.config import settings

# ── Databricks connection ─────────────────────────────────────────

BASE_URL = f"https://{settings.DATABRICKS_HOST}"
HEADERS = {}  # Set in main() after config loads


def api(method: str, path: str, body: dict = None, allow_conflict: bool = True) -> dict | None:
    """Call a Databricks REST API endpoint. Returns JSON or None on error."""
    url = f"{BASE_URL}{path}"
    try:
        resp = httpx.request(method, url, headers=HEADERS, json=body, timeout=30)
        if resp.status_code == 409 and allow_conflict:
            # Already exists — fine for idempotent setup
            print(f"  EXISTS: {method} {path}")
            return None
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except httpx.HTTPStatusError as e:
        print(f"  ERROR {e.response.status_code}: {method} {path} — {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"  ERROR: {method} {path} — {e}")
        return None


def sql_exec(statement: str, warehouse_id: str) -> dict | None:
    """Execute a SQL statement on the serverless warehouse."""
    body = {
        "warehouse_id": warehouse_id,
        "statement": statement,
        "wait_timeout": "30s",
    }
    result = api("POST", "/api/2.0/sql/statements", body, allow_conflict=False)
    if result:
        status = result.get("status", {}).get("state", "UNKNOWN")
        if status == "FAILED":
            err = result.get("status", {}).get("error", {}).get("message", "unknown")
            # Show first 80 chars of the statement for context
            print(f"  SQL FAILED: {statement.strip()[:80]}... — {err[:120]}")
        elif status == "SUCCEEDED":
            print(f"  SQL OK: {statement.strip()[:80]}")
    return result


# ── Unity Catalog ─────────────────────────────────────────────────

CATALOGS = {
    "rd_pharma": {
        "comment": "R&D Pharma data assets — molecular, genomics, compound libraries",
        "schemas": {
            "molecular": {
                "simulations": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.molecular.simulations (
                            sim_id STRING, compound_id STRING, method STRING,
                            energy_kcal DOUBLE, rmsd_angstrom DOUBLE,
                            duration_ns DOUBLE, status STRING, run_date TIMESTAMP
                        )
                    """,
                    "rows": [
                        "('SIM-40291', 'BPX-7721', 'Molecular Dynamics', -342.7, 1.82, 500.0, 'COMPLETE', '2025-12-15 08:30:00')",
                        "('SIM-40292', 'BPX-7721', 'Monte Carlo', -338.1, 2.01, 250.0, 'COMPLETE', '2025-12-16 14:22:00')",
                        "('SIM-40293', 'CPD-8834', 'Docking', -289.4, 1.54, 100.0, 'RUNNING', '2026-01-20 09:15:00')",
                    ],
                },
                "compounds": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.molecular.compounds (
                            compound_id STRING, name STRING, smiles STRING,
                            mol_weight DOUBLE, logp DOUBLE, phase STRING,
                            target_protein STRING
                        )
                    """,
                    "rows": [
                        "('BPX-7721', 'Brixapimab', 'CC(=O)Nc1ccc(O)cc1', 458.3, 2.7, 'Phase III', 'EGFR-T790M')",
                        "('CPD-8834', 'Compound-8834', 'c1ccc(CC(=O)O)cc1', 312.1, 1.9, 'Phase I', 'JAK2-V617F')",
                        "('CPD-9102', 'Compound-9102', 'CC(C)CC1=CC=CC=C1', 275.6, 3.1, 'Preclinical', 'PD-L1')",
                    ],
                },
            },
            "genomics": {
                "sequences": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.genomics.sequences (
                            seq_id STRING, patient_cohort STRING, gene STRING,
                            variant_count INT, coverage_x DOUBLE,
                            sequencer STRING, run_date TIMESTAMP
                        )
                    """,
                    "rows": [
                        "('SEQ-70412', 'BPX-7721-COHORT-A', 'EGFR', 47, 312.5, 'NovaSeq-6000', '2025-11-10 06:00:00')",
                        "('SEQ-70413', 'BPX-7721-COHORT-B', 'TP53', 23, 287.3, 'NovaSeq-6000', '2025-11-12 06:00:00')",
                        "('SEQ-70414', 'CPD-8834-PILOT', 'JAK2', 12, 445.1, 'NextSeq-2000', '2026-01-05 06:00:00')",
                    ],
                },
                "variants": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.genomics.variants (
                            variant_id STRING, gene STRING, position INT,
                            ref_allele STRING, alt_allele STRING,
                            clinical_significance STRING, frequency DOUBLE
                        )
                    """,
                    "rows": [
                        "('VAR-001', 'EGFR', 858, 'CTG', 'CGG', 'Pathogenic', 0.023)",
                        "('VAR-002', 'EGFR', 790, 'ACC', 'ATG', 'Pathogenic', 0.041)",
                        "('VAR-003', 'TP53', 248, 'CGG', 'TGG', 'Likely pathogenic', 0.008)",
                    ],
                },
            },
            "compounds": {
                "admet_predictions": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.compounds.admet_predictions (
                            compound_id STRING, model_version STRING,
                            absorption DOUBLE, distribution DOUBLE,
                            metabolism DOUBLE, excretion DOUBLE,
                            toxicity_score DOUBLE, herg_risk STRING
                        )
                    """,
                    "rows": [
                        "('BPX-7721', 'ADMET-v3.2', 0.89, 0.76, 0.82, 0.71, 0.12, 'LOW')",
                        "('CPD-8834', 'ADMET-v3.2', 0.74, 0.68, 0.55, 0.63, 0.34, 'MEDIUM')",
                        "('CPD-9102', 'ADMET-v3.2', 0.91, 0.83, 0.78, 0.69, 0.08, 'LOW')",
                    ],
                },
                "synthesis_routes": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS rd_pharma.compounds.synthesis_routes (
                            route_id STRING, compound_id STRING, steps INT,
                            yield_pct DOUBLE, cost_per_gram_usd DOUBLE,
                            scale STRING, validated BOOLEAN
                        )
                    """,
                    "rows": [
                        "('RTR-201', 'BPX-7721', 7, 34.2, 1250.00, 'Pilot', true)",
                        "('RTR-202', 'BPX-7721', 5, 28.7, 890.00, 'Lab', true)",
                        "('RTR-301', 'CPD-8834', 4, 45.1, 670.00, 'Lab', false)",
                    ],
                },
            },
        },
    },
    "clinical_trials": {
        "comment": "Clinical trial data — regulated, GxP-validated",
        "schemas": {
            "phase3": {
                "bpx7721_endpoints": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS clinical_trials.phase3.bpx7721_endpoints (
                            endpoint_id STRING, trial_id STRING, endpoint_type STRING,
                            metric STRING, target_value DOUBLE,
                            observed_value DOUBLE, p_value DOUBLE, status STRING
                        )
                    """,
                    "rows": [
                        "('EP-001', 'NCT-05847721', 'Primary', 'Progression-Free Survival', 12.0, 14.7, 0.0023, 'MET')",
                        "('EP-002', 'NCT-05847721', 'Secondary', 'Overall Response Rate', 0.35, 0.42, 0.018, 'MET')",
                        "('EP-003', 'NCT-05847721', 'Safety', 'Grade 3+ AE Rate', 0.15, 0.11, 0.041, 'MET')",
                    ],
                },
                "bpx7721_subjects": {
                    "ddl": """
                        CREATE TABLE IF NOT EXISTS clinical_trials.phase3.bpx7721_subjects (
                            subject_id STRING, site_id STRING, arm STRING,
                            age INT, sex STRING, enrolled_date DATE,
                            status STRING, last_visit DATE
                        )
                    """,
                    "rows": [
                        "('SUBJ-10001', 'SITE-CH-001', 'Treatment', 58, 'F', '2025-03-15', 'Active', '2026-01-20')",
                        "('SUBJ-10002', 'SITE-CH-001', 'Placebo', 63, 'M', '2025-03-18', 'Active', '2026-01-18')",
                        "('SUBJ-10003', 'SITE-US-004', 'Treatment', 51, 'F', '2025-04-02', 'Completed', '2025-12-30')",
                        "('SUBJ-10004', 'SITE-DE-002', 'Treatment', 67, 'M', '2025-05-10', 'Active', '2026-01-22')",
                    ],
                },
            },
        },
    },
}


def setup_catalog(warehouse_id: str):
    """Create Unity Catalog catalogs, schemas, and tables with sample data.

    Uses SQL statements (not REST API) to create catalogs and schemas,
    because trial workspaces with Default Storage require this approach.
    """
    print("\n=== Unity Catalog Setup ===")

    for catalog_name, catalog_def in CATALOGS.items():
        print(f"\n── Catalog: {catalog_name} ──")

        # Create catalog via SQL (works with Default Storage)
        sql_exec(
            f"CREATE CATALOG IF NOT EXISTS {catalog_name} COMMENT '{catalog_def['comment']}'",
            warehouse_id,
        )

        for schema_name, tables in catalog_def["schemas"].items():
            # Create schema via SQL
            sql_exec(
                f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}",
                warehouse_id,
            )

            for table_name, table_def in tables.items():
                fqn = f"{catalog_name}.{schema_name}.{table_name}"
                print(f"  Table: {fqn}")

                # Create table via SQL
                sql_exec(table_def["ddl"], warehouse_id)

                # Insert sample rows
                if table_def.get("rows"):
                    values = ", ".join(table_def["rows"])
                    sql_exec(f"INSERT INTO {fqn} VALUES {values}", warehouse_id)

    print("\nCatalog setup complete.")


# ── MLflow Experiments ────────────────────────────────────────────

EXPERIMENTS = [
    {
        "name": "/Shared/BaselPharma-RD/BPX-7721-MolecularDynamics",
        "runs": [
            {"metrics": {"loss": 0.0234, "rmsd": 1.82, "energy_kcal": -342.7, "epoch": 150}},
            {"metrics": {"loss": 0.0187, "rmsd": 1.71, "energy_kcal": -348.2, "epoch": 200}},
            {"metrics": {"loss": 0.0312, "rmsd": 2.04, "energy_kcal": -331.5, "epoch": 100}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/BPX-7721-ProteinFolding",
        "runs": [
            {"metrics": {"loss": 0.0156, "tm_score": 0.87, "gdt_ts": 82.3, "epoch": 250}},
            {"metrics": {"loss": 0.0198, "tm_score": 0.84, "gdt_ts": 79.1, "epoch": 200}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/BPX-7721-QSAR-v3",
        "runs": [
            {"metrics": {"r_squared": 0.934, "rmse": 0.187, "mae": 0.142, "epoch": 80}},
            {"metrics": {"r_squared": 0.921, "rmse": 0.204, "mae": 0.158, "epoch": 60}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/BPX-7721-ADMET-Prediction",
        "runs": [
            {"metrics": {"auc_roc": 0.962, "accuracy": 0.918, "f1_score": 0.907, "epoch": 120}},
            {"metrics": {"auc_roc": 0.948, "accuracy": 0.903, "f1_score": 0.891, "epoch": 100}},
            {"metrics": {"auc_roc": 0.971, "accuracy": 0.932, "f1_score": 0.924, "epoch": 150}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/GenomicsVariantCalling",
        "runs": [
            {"metrics": {"precision": 0.987, "recall": 0.974, "f1_score": 0.980, "variants_called": 47231}},
            {"metrics": {"precision": 0.991, "recall": 0.968, "f1_score": 0.979, "variants_called": 45892}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/DrugInteractionModel",
        "runs": [
            {"metrics": {"loss": 0.0089, "accuracy": 0.956, "interaction_pairs": 12840, "epoch": 300}},
            {"metrics": {"loss": 0.0112, "accuracy": 0.943, "interaction_pairs": 12840, "epoch": 250}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/ClinicalOutcomePrediction",
        "runs": [
            {"metrics": {"auc_roc": 0.891, "concordance_index": 0.834, "brier_score": 0.112, "epoch": 200}},
            {"metrics": {"auc_roc": 0.878, "concordance_index": 0.821, "brier_score": 0.128, "epoch": 180}},
        ],
    },
    {
        "name": "/Shared/BaselPharma-RD/ToxicologyScreening",
        "runs": [
            {"metrics": {"sensitivity": 0.943, "specificity": 0.967, "compounds_screened": 8450, "epoch": 90}},
            {"metrics": {"sensitivity": 0.938, "specificity": 0.958, "compounds_screened": 8450, "epoch": 75}},
            {"metrics": {"sensitivity": 0.951, "specificity": 0.972, "compounds_screened": 8450, "epoch": 120}},
        ],
    },
]


def setup_experiments():
    """Create MLflow experiments with realistic runs and metrics."""
    print("\n=== MLflow Experiments Setup ===")

    # Ensure parent workspace directory exists (MLflow needs it)
    api("POST", "/api/2.0/workspace/mkdirs", {"path": "/Shared/BaselPharma-RD"})

    for exp_def in EXPERIMENTS:
        name = exp_def["name"]
        print(f"\n── Experiment: {name} ──")

        # Create experiment
        result = api("POST", "/api/2.0/mlflow/experiments/create", {"name": name})
        if result is None:
            # Already exists — look it up by name
            lookup = api("GET", f"/api/2.0/mlflow/experiments/get-by-name?experiment_name={name}")
            if lookup and "experiment" in lookup:
                exp_id = lookup["experiment"]["experiment_id"]
            else:
                print(f"  SKIP: Could not create or find experiment {name}")
                continue
        else:
            exp_id = result.get("experiment_id", "")

        if not exp_id:
            print(f"  SKIP: No experiment ID for {name}")
            continue

        # Create runs with metrics
        for i, run_def in enumerate(exp_def["runs"]):
            run_result = api("POST", "/api/2.0/mlflow/runs/create", {
                "experiment_id": exp_id,
                "start_time": int((time.time() - random.randint(3600, 86400 * 30)) * 1000),
                "tags": [
                    {"key": "mlflow.user", "value": "baselpharma-rd"},
                    {"key": "mlflow.source.name", "value": f"training/{name.split('/')[-1].lower()}.py"},
                    {"key": "mlflow.runName", "value": f"run-{i+1}"},
                ],
            })

            if not run_result or "run" not in run_result:
                print(f"  Could not create run {i+1}")
                continue

            run_id = run_result["run"]["info"]["run_id"]

            # Log metrics
            for key, value in run_def["metrics"].items():
                api("POST", "/api/2.0/mlflow/runs/log-metric", {
                    "run_id": run_id,
                    "key": key,
                    "value": value,
                    "timestamp": int(time.time() * 1000),
                }, allow_conflict=False)

            # End the run (mark as FINISHED)
            api("POST", "/api/2.0/mlflow/runs/update", {
                "run_id": run_id,
                "status": "FINISHED",
                "end_time": int(time.time() * 1000),
            }, allow_conflict=False)

            print(f"  Run {i+1}: {len(run_def['metrics'])} metrics logged")

    print("\nExperiments setup complete.")


# ── Workspace Notebook ────────────────────────────────────────────

NOTEBOOK_CONTENT = """# Databricks notebook source
# MAGIC %md
# MAGIC # BPX-7721 Training Pipeline
# MAGIC **Drug Discovery AI — Molecular Dynamics + QSAR Model Training**
# MAGIC
# MAGIC This notebook trains the Phase III candidate BPX-7721 binding affinity model
# MAGIC using molecular simulation data from the R&D data lake.
# MAGIC
# MAGIC | Parameter | Value |
# MAGIC |-----------|-------|
# MAGIC | Compound | BPX-7721 (Brixapimab) |
# MAGIC | Target | EGFR-T790M |
# MAGIC | Pipeline Value | $2.1B |
# MAGIC | Phase | III |

# COMMAND ----------

import pandas as pd
import numpy as np
import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
from datetime import datetime

print(f"PyTorch {torch.__version__} | MLflow {mlflow.__version__}")
print(f"GPU available: {torch.cuda.is_available()}")
print(f"Pipeline started: {datetime.now().isoformat()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load Training Data from Unity Catalog
# MAGIC Pull molecular simulation results and compound properties from the R&D catalog.

# COMMAND ----------

# Load molecular dynamics simulation results
simulations_df = spark.sql(\"\"\"
    SELECT s.sim_id, s.compound_id, s.method, s.energy_kcal, s.rmsd_angstrom,
           c.smiles, c.mol_weight, c.logp, c.target_protein
    FROM rd_pharma.molecular.simulations s
    JOIN rd_pharma.molecular.compounds c ON s.compound_id = c.compound_id
    WHERE c.compound_id = 'BPX-7721'
\"\"\").toPandas()

# Load ADMET predictions for feature enrichment
admet_df = spark.sql(\"\"\"
    SELECT compound_id, absorption, distribution, metabolism, excretion, toxicity_score
    FROM rd_pharma.compounds.admet_predictions
    WHERE compound_id = 'BPX-7721'
\"\"\").toPandas()

print(f"Loaded {len(simulations_df)} simulations, {len(admet_df)} ADMET records")
display(simulations_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Feature Engineering — Molecular Descriptors

# COMMAND ----------

def compute_molecular_features(df):
    \"\"\"Compute binding affinity features from simulation data.\"\"\"
    features = pd.DataFrame()
    features['energy_norm'] = (df['energy_kcal'] - df['energy_kcal'].mean()) / df['energy_kcal'].std()
    features['rmsd_norm'] = df['rmsd_angstrom'] / df['rmsd_angstrom'].max()
    features['logp'] = df['logp']
    features['mol_weight_scaled'] = df['mol_weight'] / 500.0  # Scale to ~1.0
    # Interaction score — combines energy and structural fit
    features['interaction_score'] = -features['energy_norm'] * (1 - features['rmsd_norm'])
    return features

X_train = compute_molecular_features(simulations_df)
y_train = torch.tensor(simulations_df['energy_kcal'].values, dtype=torch.float32)

print(f"Feature matrix: {X_train.shape}")
print(f"Features: {list(X_train.columns)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Model Architecture — Binding Affinity Predictor

# COMMAND ----------

class BindingAffinityNet(nn.Module):
    \"\"\"Neural network for predicting protein-ligand binding affinity.\"\"\"
    def __init__(self, input_dim=5, hidden_dims=[128, 64, 32]):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(prev_dim, h), nn.ReLU(), nn.Dropout(0.2)])
            prev_dim = h
        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

model = BindingAffinityNet(input_dim=X_train.shape[1])
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
print(model)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Training Loop with MLflow Tracking

# COMMAND ----------

EXPERIMENT_NAME = "/Shared/BaselPharma-RD/BPX-7721-MolecularDynamics"
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run(run_name="binding-affinity-v3") as run:
    # Hyperparameters
    lr = 0.001
    epochs = 200
    batch_size = 32

    mlflow.log_params({"lr": lr, "epochs": epochs, "batch_size": batch_size,
                        "compound": "BPX-7721", "target": "EGFR-T790M"})

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    X_tensor = torch.tensor(X_train.values, dtype=torch.float32)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        predictions = model(X_tensor).squeeze()
        loss = criterion(predictions, y_train)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0:
            rmsd = torch.sqrt(loss).item()
            mlflow.log_metrics({"loss": loss.item(), "rmsd": rmsd}, step=epoch)
            print(f"Epoch {epoch+1}/{epochs} — Loss: {loss.item():.4f}, RMSD: {rmsd:.4f}")

    # Log final model
    mlflow.pytorch.log_model(model, "binding_affinity_model")
    print(f"\\nRun ID: {run.info.run_id}")
    print(f"Model logged to: {EXPERIMENT_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Register Model for Production Scoring

# COMMAND ----------

model_uri = f"runs:/{run.info.run_id}/binding_affinity_model"
registered = mlflow.register_model(model_uri, "BPX7721-BindingAffinity")
print(f"Registered model version: {registered.version}")
print(f"Model: BPX7721-BindingAffinity v{registered.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Inference — Score New Compounds

# COMMAND ----------

# Score candidate compounds from the pipeline
candidates = spark.sql(\"\"\"
    SELECT compound_id, name, smiles, mol_weight, logp, target_protein
    FROM rd_pharma.molecular.compounds
\"\"\").toPandas()

model.eval()
with torch.no_grad():
    # Simple scoring using available features
    for _, row in candidates.iterrows():
        features = torch.tensor([[0.0, 0.5, row['logp'], row['mol_weight']/500.0, 0.5]],
                                  dtype=torch.float32)
        score = model(features).item()
        print(f"  {row['compound_id']} ({row['name']}): predicted binding energy = {score:.1f} kcal/mol")

print("\\nScoring complete — results ready for lead optimization team.")
"""


def setup_notebook():
    """Import the BPX-7721 training pipeline notebook into the workspace."""
    print("\n=== Workspace Notebook Setup ===")

    notebook_path = "/Shared/BaselPharma-RD/BPX-7721_Training_Pipeline"
    print(f"  Importing: {notebook_path}")

    # Create the parent directory first
    api("POST", "/api/2.0/workspace/mkdirs", {
        "path": "/Shared/BaselPharma-RD",
    })

    # Import notebook (base64-encoded content)
    encoded = base64.b64encode(NOTEBOOK_CONTENT.encode("utf-8")).decode("utf-8")
    result = api("POST", "/api/2.0/workspace/import", {
        "path": notebook_path,
        "format": "SOURCE",
        "language": "PYTHON",
        "content": encoded,
        "overwrite": True,
    })

    if result is not None:
        print(f"  OK: Notebook imported at {notebook_path}")
    else:
        print(f"  Notebook import may have failed — check workspace")

    print("\nNotebook setup complete.")


# ── Warehouse discovery ───────────────────────────────────────────

def find_warehouse() -> str | None:
    """Find the first available SQL warehouse ID."""
    result = api("GET", "/api/2.0/sql/warehouses")
    if not result or "warehouses" not in result:
        return None
    for wh in result["warehouses"]:
        print(f"  Found warehouse: {wh['name']} ({wh['id']}) — {wh.get('state', 'unknown')}")
        return wh["id"]
    return None


# ── Main ──────────────────────────────────────────────────────────

def main():
    global HEADERS

    parser = argparse.ArgumentParser(description="Populate Databricks workspace with pharma demo data")
    parser.add_argument("--catalog", action="store_true", help="Only create Unity Catalog objects")
    parser.add_argument("--experiments", action="store_true", help="Only create MLflow experiments")
    parser.add_argument("--notebook", action="store_true", help="Only import the notebook")
    args = parser.parse_args()

    # Default: run everything if no flag specified
    run_all = not (args.catalog or args.experiments or args.notebook)

    if not settings.DATABRICKS_HOST or not settings.DATABRICKS_TOKEN:
        print("ERROR: Set DATABRICKS_HOST and DATABRICKS_TOKEN in .env")
        sys.exit(1)

    HEADERS = {
        "Authorization": f"Bearer {settings.DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }

    print(f"Databricks host: {settings.DATABRICKS_HOST}")
    print(f"Base URL: {BASE_URL}")

    # Unity Catalog needs a SQL warehouse to execute DDL
    if run_all or args.catalog:
        warehouse_id = find_warehouse()
        if not warehouse_id:
            print("ERROR: No SQL warehouse found. Create one in the Databricks UI first.")
            if not (args.experiments or args.notebook):
                sys.exit(1)
        else:
            setup_catalog(warehouse_id)

    if run_all or args.experiments:
        setup_experiments()

    if run_all or args.notebook:
        setup_notebook()

    print("\n=== All done! ===")
    print(f"Open: https://{settings.DATABRICKS_HOST}/explore/data/rd_pharma")


if __name__ == "__main__":
    main()
