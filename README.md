# llm-lab

A hands-on lab for learning LLM engineering on AWS Bedrock and Anthropic API.

Built during a 90-day journey from Senior AWS Cloud Engineer → Senior Cloud + AI Engineer.

---

## What's inside

### Week 1: Multi-provider LLM comparison API

A FastAPI app that calls both **AWS Bedrock (Amazon Nova Lite)** and the **Anthropic API (Claude Haiku 4.5)** side by side, returning normalized responses with latency metrics.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/query/aws` | Call Amazon Nova via Bedrock |
| `POST` | `/query/anthropic` | Call Claude via Anthropic API |
| `POST` | `/query/compare` | Call both providers, return responses + latency |

**Example response from `/query/compare`:**

```json
{
  "aws": {
    "text": "RAG (Retrieval-Augmented Generation) is...",
    "latency_ms": 571,
    "model": "apac.amazon.nova-lite-v1:0"
  },
  "anthropic": {
    "text": "Retrieval-Augmented Generation is...",
    "latency_ms": 1086,
    "model": "claude-haiku-4-5-20251001"
  }
}
```

**Stack:** FastAPI · Python 3.12 · boto3 · anthropic SDK · Pydantic · python-dotenv

---

## Setup

```bash
# Clone the repo
git clone git@github.com:jindalankuraws/llm-lab.git
cd llm-lab

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Then edit .env and fill in your real values

# Run the API
uvicorn src.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key from [console.anthropic.com](https://console.anthropic.com/) |
| `REGION_NAME` | AWS region for Bedrock (e.g., `ap-southeast-1`) |
| `AWS_MODEL_ID` | Bedrock model ID (e.g., `apac.amazon.nova-lite-v1:0`) |
| `ANTHROPIC_MODEL_ID` | Anthropic model ID (e.g., `claude-haiku-4-5-20251001`) |

AWS credentials are read from your local AWS profile (`~/.aws/credentials` or SSO session). No keys live in code.

---

## Architecture notes

- **Response normalization:** Both providers return different JSON shapes. The `call_aws()` and `call_anthropic()` helpers normalize them to `{ text, latency_ms, model }` so downstream consumers don't care which provider answered.
- **Enum-based provider routing:** FastAPI validates the `provider` path parameter against an `Enum`, giving you a dropdown in Swagger and free request validation.
- **Single-instance clients:** Both `boto3` and `anthropic` clients are created once at module load — not per request — to avoid auth handshake overhead on every call.

---

## Security

This repo is hardened with:

- Branch protection on `main` (PR required, signed commits required, force-push blocked)
- Secret scanning + push protection enabled
- Dependabot alerts + security updates
- Pinned dependency versions in `requirements.txt`
- `.env` strictly gitignored — never committed

If you spot a security issue, please open a private report rather than a public issue.

---

## Roadmap

The full 90-day plan that produced this repo:

- [x] **Week 1:** Multi-provider LLM comparison API ← *you are here*
- [ ] **Week 2:** Embeddings + vector search (FAISS + Bedrock Titan)
- [ ] **Week 3:** RAG architecture on AWS
- [ ] **Week 4:** Project 1 — RAG chatbot over AWS Well-Architected Framework
- [ ] **Month 2:** Agents, tool use, FinOps Text-to-SQL assistant
- [ ] **Month 3:** Production-grade AI gateway (Guardrails, Langfuse, evals, Terraform)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built by [Ankur Jindal](https://github.com/jindalankuraws) · Senior AWS Cloud Engineer based in Singapore, exploring AI engineering.*
