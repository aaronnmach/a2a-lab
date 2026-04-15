"""Deploy the Echo A2A wrapper to Vertex AI Reasoning Engine."""

from __future__ import annotations

import os
import sys
import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "a2a-lab-493222"
REGION = "us-central1"
STAGING_BUCKET = f"gs://{PROJECT_ID}-a2a-staging"

CLOUD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CLOUD_DIR, ".."))
SERVER_DIR = os.path.join(PROJECT_ROOT, "server")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import EchoAgent

vertexai.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=STAGING_BUCKET,
)

remote_agent = reasoning_engines.ReasoningEngine.create(
    EchoAgent(),
    requirements=[
        "google-cloud-aiplatform[agent_engines]",
        "fastapi==0.111.0",
        "uvicorn==0.29.0",
        "pydantic==2.7.0",
        "httpx==0.27.0",
        "cloudpickle",
    ],
    extra_packages=["./agent"],
    display_name="Echo A2A Agent",
    description="A2A Lab - Echo Agent on Agent Engine",
    gcs_dir_name="echo-agent-v5-flat",
)

print(f"Deployed! Resource name: {remote_agent.resource_name}")
print(f"Engine ID: {remote_agent.resource_name.split('/')[-1]}")