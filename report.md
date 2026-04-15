# CS4680 A2A Lab Report

## Section 3 - Schema Analysis & Extension

### 3.1 Why does the request use a client-generated `id` rather than a server-generated one?
A client-generated task ID lets the client identify the request before it is sent, which matters when the network is unreliable or multiple services are involved. In distributed systems, the client may need to retry a request after a timeout without knowing whether the server already processed it. Reusing the same ID makes the request easier to correlate across logs, traces, retries, and downstream services. It also supports idempotency because the server can treat repeated submissions with the same task ID as the same logical task instead of creating duplicate work.

### 3.2 When would a server return `status.state = "working"` in a non-streaming call, and how should a client react?
A server could return `working` when the task has been accepted but has not finished yet, for example because the task triggers a long-running retrieval, document conversion, tool call, or queued background job. In a non-streaming scenario, that response usually means the server cannot yet return final artifacts in the same call. A robust client should not try to parse final output immediately. Instead, it should treat the response as incomplete work, surface that state clearly, and either poll a follow-up status endpoint if the protocol supports one or retry later using the same task ID.

### 3.3 What is the purpose of `sessionId`?
The `sessionId` groups related tasks into the same ongoing conversation or workflow. It lets the server attach continuity to otherwise separate HTTP calls. For example, one task might ask `Summarise this paper`, and the next task in the same session might ask `Now extract the three main risks from the summary`. These are two separate task requests, but they belong to one conversation and should share the same session ID.

### 3.4 Realistic workflow using `text`, `file`, and `data`
A realistic workflow would be a research assistant agent collaborating with a compliance-checking agent. The user sends a text part such as `Review this contract and tell me whether it violates our policy`, a file part pointing to the PDF contract, and a data part containing structured metadata such as department, document type, and policy version. The first agent reads the text instruction, downloads the file, and uses the structured data to choose the correct rules. It can then forward the same combination of text, file, and data to another specialist agent for risk scoring.

### 3.5 Code changes completed
The `TaskRequest` model now accepts optional file parts via a `FilePart` model with `url` and `mimeType` fields. The client's `extract_text()` helper now returns a file URL when the first artifact part is a file rather than text.

---

## Section 4 - Cloud Run Deployment

### 4.1 What does `--allow-unauthenticated` do, and what are the security implications?
On Cloud Run, allowing unauthenticated access makes the service publicly invokable over HTTPS by granting public invocation access instead of requiring callers to present Google-signed identity tokens. This is convenient for a demo A2A service because a simple HTTP client can reach it without extra auth setup. The security tradeoff is that anyone who knows the URL can send requests, so the service must be treated as public-facing. That increases the need for input validation, rate limiting, logging, and careful control over any downstream resources the service can access. Essentially, this means the endpoint is open to the internet. While it's great for testing our A2A client without managing IAM tokens, it means I'd need to add my own API keys or logic-level validation if this were a production service to prevent unauthorized use.

### 4.2 How Cloud Run scales to zero and what cold start latency means
Cloud Run automatically scales the number of running instances based on demand, and by default a revision can scale all the way down to zero when it is idle. That is cost-efficient because no warm instance needs to stay running when there is no traffic. The downside is cold start latency: if a request arrives when there are zero running instances, Cloud Run must start a new container before the request can be handled. For an A2A client, that means the first request after a period of inactivity may take noticeably longer than later requests that hit an already-running instance. Google’s Cloud Run docs explicitly describe both automatic scaling to zero and the option to keep minimum instances warm to reduce this delay.

### 4.3 Deployment notes
I would run `bash cloud/deploy_cloud_run.sh`, copy the printed service URL, update the `url` field in `AGENT_CARD`, redeploy, and then verify with:

```bash
curl https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app/.well-known/agent.json
A2A_AGENT_URL="https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app" python client/demo.py
```

---

## Section 5 - Agent Engine Deployment

### 5.1 Cloud Run vs Agent Engine
Cloud Run was easier to set up for this lab because it's just a standard Docker container running FastAPI. Agent Engine, on the other hand, feels more like a 'black box' where Google handles the infrastructure, which is nice for scaling but makes it harder to debug local vs. remote environment issues (like the cloudpickle errors I encountered).

Agent Engine is more purpose-built for AI agents. Google presents Reasoning Engine as a managed runtime for agent-style applications with SDK-based deployment and querying patterns. That lowers operational burden for agent-specific hosting and can be a better fit when the main goal is serving agent logic rather than managing generic web infrastructure. In this assignment, Cloud Run is the simpler path for deploying a plain HTTP A2A server, while Agent Engine is the better fit for experimenting with a managed agent runtime. citeturn199051search6turn199051search10turn199051search14

### 5.2 Why does the wrapper use a synchronous `query()` method even though the handler is async?

The query() method is sync because the Vertex SDK's ReasoningEngine interface requires it. I used asyncio.run() inside that method so I could still reuse the same handle_task logic used in the FastAPI server without rewriting it as synchronous code.

### 5.3 Querying the deployed engine
After deployment, the SDK call would look like this:

```python
from vertexai.preview import reasoning_engines

agent = reasoning_engines.ReasoningEngine(
    "projects/PROJECT_ID/locations/us-central1/reasoningEngines/ENGINE_ID"
)
response = agent.query(message_text="Hello from Agent Engine!")
print(response)
```

Google’s official samples show this same overall query pattern for a deployed Reasoning Engine.

---

## Section 6 - Client-Server Connection Trace

### 6.1 Example demo log output
After deploying to Cloud Run, I ran the demo script and got the following trace showing the discovery and task steps:

```text
(.venv) (base) aaronnmsch@Mac a2a-lab % python client/demo.py
[DISCOVER] GET https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app/.well-known/agent.json
[DISCOVER] <- 200 {"id":"echo-agent-v1","name":"Echo Agent","version":"1.0.0","description":"A simple agent that echoes back text or returns a mock summary.","url":"https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app","cont
Agent: Echo Agent (1.0.0)
Skills:
- Echo: Returns the user message verbatim.
- Summarise: Returns a one-sentence mock summary when the input starts with !summarise.
[SEND] POST https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app/tasks/send
[SEND] -> {"id": "d720e2c3-231c-45a4-a21a-84dd8bfbe4be", "sessionId": null, "message": {"role": "user", "parts": [{"type": "text", "text": "Hello from the client!"}]}}
[SEND] <- 200 {"id":"d720e2c3-231c-45a4-a21a-84dd8bfbe4be","status":{"state":"completed","message":null},"artifacts":[{"index":0,"name":"result","parts":[{"type":"text","text":"Hello from the client!"}]}]}
Response text: Hello from the client!
```

### 6.2 UML sequence diagram

```text
User            A2AClient                 Cloud Run A2A Server              handlers.py
 |                  |                               |                            |
 | run demo.py      |                               |                            |
 |----------------->|                               |                            |
 |                  | GET /.well-known/agent.json   |                            |
 |                  |------------------------------>|                            |
 |                  | <------- 200 Agent Card ------|                            |
 |                  |                               |                            |
 |                  | POST /tasks/send              |                            |
 |                  |------------------------------>|                            |
 |                  |                               | handle_task(request)       |
 |                  |                               |--------------------------->|
 |                  |                               | <------ result text -------|
 |                  | <------ 200 JSON response ----|                            |
 |<-----------------|                               |                            |
```

### 6.3 Safe retry after a network failure
If the client loses the network after sending the POST, it cannot assume the server failed. The safest retry strategy is to resend the same logical task using the same client-generated `id`, so the server can detect it as a duplicate or correlate it with any already-completed work. That task ID is the key field that supports idempotency and retry safety in the protocol.

---

## Section 7 - Bonus Multi-Agent Chain

### 7.1 Bonus implementation summary
For the bonus challenge, I added:
- `server/reverse_main.py`
- `server/reverse_agent_card.py`
- `server/Dockerfile.reverse`
- `client/coordinator.py`

The coordinator discovers both agents using their Agent Cards, sends the original message to EchoAgent, and then sends EchoAgent’s output to ReverseAgent.

### 7.2 Authentication between agents with service account tokens
To secure the agents in my chain, I would remove the --allow-unauthenticated flag. The Coordinator would then need to fetch an OIDC token from the Google metadata server to authenticate each request. This way, the Echo and Reverse agents only talk to callers with the right IAM permissions.

### 7.3 Passing `sessionId` across the chain
To preserve conversation continuity across multiple agents, the coordinator should forward the same `sessionId` when calling the second agent. The current schema already supports `sessionId`, so no breaking schema change is strictly required. What is needed is a design rule: downstream task payloads should copy the upstream `sessionId` so all participating agents can correlate the same logical workflow.
