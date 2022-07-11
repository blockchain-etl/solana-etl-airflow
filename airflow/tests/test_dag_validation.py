# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sys
from pathlib import Path

import pytest
from airflow.models import DagBag, Variable

DAGS_FOLDER = f"{Path(__file__).resolve().parent.parent}/dags"

# Add to PATH to fix relative imports, like Airflow running dynamically
# https://airflow.apache.org/docs/apache-airflow/stable/modules_management.html#built-in-pythonpath-entries-in-airflow
sys.path.append(DAGS_FOLDER)

MOCK_ENV_VARS = {
    "AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT": "google-cloud-platform://",
    "DAGS_FOLDER": DAGS_FOLDER,
}

# Airflow Variables cannot be created using env vars before version 1.10.10
MOCK_AIRFLOW_VARS = {
    "discord_alerts_dag_owners": '{"dummy_dag": "test_discord_alerts_dag_owner"}',
    "discord_alerts_default_owner": "test_discord_alerts_default_owner",
    "discord_alerts_webhook_url": "test_discord_alerts_webhook_url",
    "environment": "test_environment",
    "notification_emails": "test_notification_emails@foo.bar",
    "solana_checkpoint_bucket": "test_solana_checkpoint_bucket",
    "solana_destination_dataset_project_id": "test_solana_destination_dataset_project_id",
    "solana_export_max_active_runs": "1",
    "solana_export_max_workers": "30",
    "solana_export_start_block": "138802069",
    "solana_load_all_partitions": "False",
    "solana_max_lag_in_minutes": "30",
    "solana_output_bucket": "test_solana_output_bucket",
    "solana_provider_uris": "test_solana_provider_uri_0, test_solana_provider_uri_1",
}


@pytest.fixture(autouse=True)
def env_vars_setup(monkeypatch):
    for k, v in MOCK_ENV_VARS.items():
        monkeypatch.setenv(k, v)


@pytest.fixture
def dag_bag(monkeypatch):
    monkeypatch.setattr(Variable, "get", MOCK_AIRFLOW_VARS.get)
    yield DagBag(dag_folder=DAGS_FOLDER, include_examples=False)


def test_no_import_errors(dag_bag):
    assert len(dag_bag.import_errors) == 0, "No Import Failures"


def test_dag_ids(dag_bag):
    expected_dag_ids = [
        "solana_export_dag",
        "solana_load_dag",
    ]
    assert sorted(dag_bag.dag_ids) == expected_dag_ids
