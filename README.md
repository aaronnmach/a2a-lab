# A2A Lab (CS4680)

This repository contains a complete starter solution for the Agent-to-Agent hands-on lab.

Project ID: a2a-lab-493222

## Project structure

```text
a2a-lab/
  server/
    main.py
    agent_card.py
    handlers.py
    agent_engine_wrapper.py
    Dockerfile
    requirements.txt
  client/
    client.py
    demo.py
  cloud/
    deploy_cloud_run.sh
    deploy_agent_engine.py
  report.md
  README.md
```

## 1. Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
pip install google-auth requests
```

## 2. Run locally

```bash
uvicorn server.main:app --reload --port 8000
```

Check endpoints:

```bash
curl http://localhost:8000/.well-known/agent.json
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"id":"t1","message":{"role":"user","parts":[{"type":"text","text":"Hello A2A"}]}}'
```

Test the mock summariser:

```bash
curl -X POST http://localhost:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"id":"t2","message":{"role":"user","parts":[{"type":"text","text":"!summarise This is a long article."}]}}'
```

## 3. Run the client demo

```bash
python client/demo.py
```

## 4. Deploy to Cloud Run

```bash
bash cloud/deploy_cloud_run.sh
```

### Cleanup

```bash
gcloud run services delete echo-a2a-agent --region=us-central1
```

## 5. Deploy to Vertex AI Agent Engine

```bash
gsutil mb -l us-central1 gs://a2a-lab-493222-a2a-staging
```

```bash
python cloud/deploy_agent_engine.py
```

## 6. Flake8

```bash
pip install flake8
flake8 server client cloud
```

## 7. Cloud Run Service URL

```text
https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app
```

## 8. Bonus multi-agent chain

Run the reverse agent locally on port 8001:

```bash
uvicorn server.reverse_main:app --reload --port 8001
```

```bash
ECHO_AGENT_URL="http://localhost:8000" REVERSE_AGENT_URL="http://localhost:8001" python client/coordinator.py
```
