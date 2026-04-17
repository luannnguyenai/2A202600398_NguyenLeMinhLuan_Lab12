# Lab 12 — Part 6 Final Project

## Điểm chính

- Public dashboard chat tại `GET /`
- Browser route không cần API key tại `POST /web/ask`
- Protected API route tại `POST /ask`, bắt buộc header `X-API-Key`
- OpenAI provider qua `OPENAI_API_KEY`
- Default model: `gpt-5-mini`
- Lưu lịch sử hội thoại trong Redis
- Rate limit theo user: mặc định `10 request/phút`
- Budget guard theo user: mặc định `$10/user/tháng`
- Context optimization: chỉ gửi vài message gần nhất vào model
- Health check: `GET /health`
- Readiness check: `GET /ready`
- Prometheus metrics: `GET /metrics`
- OpenTelemetry tracing và response header `X-Trace-Id`
- Docker multi-stage, non-root runtime
- Render-first deploy config trong `render.yaml`

## Cấu trúc

```text
06-lab-complete/
├── app/
│   ├── auth.py
│   ├── chat_service.py
│   ├── config.py
│   ├── cost_guard.py
│   ├── main.py
│   ├── openai_client.py
│   ├── rate_limiter.py
│   └── web_ui.py
├── tests/test_app.py
├── .dockerignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── prometheus.yml
├── render.yaml
└── check_production_ready.py
```

## Chạy local

### 1. Tạo env

```bash
cd 06-lab-complete
cp .env.example .env.local
```

Mở `.env.local` và set tối thiểu:

```env
OPENAI_API_KEY=sk-your-openai-key
AGENT_API_KEY=dev-key-change-me
```

Không commit `.env.local`.

### 2. Chạy full stack

```bash
docker compose up --build --scale agent=3
```

Các URL local:

- App qua nginx: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Redis: internal Docker network

### 3. Dừng stack

```bash
docker compose down
```

Xóa luôn Redis volume local:

```bash
docker compose down -v
```

## Test nhanh local

### Dashboard

```bash
curl -i http://localhost:8080/
```

Kỳ vọng: HTTP `200`, HTML có `Render AI Operations Console`.

### Health

```bash
curl -i http://localhost:8080/health
curl -i http://localhost:8080/ready
```

Kỳ vọng: `/health` và `/ready` trả `200`. Nếu `/ready` trả `503`, Redis chưa sẵn sàng hoặc app chưa connect được Redis.

### Public chat route

```bash
curl -i -X POST http://localhost:8080/web/ask \
  -H "Content-Type: application/json" \
  -d '{"client_id":"browser-local-test","question":"What should I verify before deploying to Render?"}'
```

Kỳ vọng:

- HTTP `200`
- không cần `X-API-Key`
- JSON có `user_id`, `answer`, `history_length`, `served_by`, `usage`

### Protected API route

Request thiếu API key:

```bash
curl -i -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student-1","question":"hello"}'
```

Kỳ vọng: HTTP `401`.

Request có API key:

```bash
curl -i -X POST http://localhost:8080/ask \
  -H "X-API-Key: dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student-1","question":"What is a readiness check?"}'
```

Kỳ vọng:

- HTTP `200`
- có header `X-Trace-Id`
- JSON có `served_by`
- JSON có `history_length`

### Metrics

```bash
curl -i http://localhost:8080/metrics
```

Kỳ vọng: text metrics có `agent_http_requests_total`.

## Test code

Máy local có thể thiếu dependency Python, nên cách ổn định nhất là chạy trong container Python 3.11:

```bash
docker run --rm \
  -v "$(pwd)/..:/workspace" \
  -w /workspace/06-lab-complete \
  python:3.11-slim \
  sh -lc "pip install --no-cache-dir -r requirements.txt >/tmp/pip.log && PYTHONPATH=/workspace/06-lab-complete pytest tests/test_app.py -q"
```

Chạy production readiness checker:

```bash
python3 check_production_ready.py
```

Checker rà các điểm chính:

- Dockerfile, `.dockerignore`, `.env.example`, `render.yaml`
- `/health`, `/ready`, `/metrics`
- API key auth, rate limit, budget guard
- Redis-backed conversation history
- OpenAI provider config
- tracing/logging/metrics

## Deploy lên Render

Render không cần cài server trên máy của bạn. Cách dùng chính là Render Dashboard trên web. Render CLI là tùy chọn, hữu ích khi muốn validate `render.yaml`, xem service, trigger deploy hoặc script hóa thao tác.

### Cách 1: Deploy bằng Render Dashboard

1. Push repo lên GitHub.
2. Vào `https://dashboard.render.com`.
3. Đăng ký hoặc đăng nhập Render.
4. Kết nối GitHub account với Render.
5. Chọn `New` -> `Web Service`.
6. Chọn repo chứa project này.
7. Chọn runtime/language là `Docker`.
8. Set `Root Directory` = `06-lab-complete`.
9. Set health check path = `/ready`.
10. Tạo một Render Key Value/Redis-compatible instance trong cùng workspace.
11. Copy internal Redis URL của Key Value instance.
12. Vào tab `Environment` của Web Service và set:

```env
ENVIRONMENT=production
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-5-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=30
AGENT_API_KEY=your-secret-agent-key
REDIS_URL=redis://your-internal-render-redis-url
RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
```

13. Deploy service.
14. Mở URL `.onrender.com` do Render cấp.

### Cách 2: Deploy bằng Blueprint

Repo đã có `06-lab-complete/render.yaml`.

1. Push repo lên GitHub.
2. Trong Render Dashboard chọn `New` -> `Blueprint`.
3. Chọn repo.
4. Khi Render hỏi Blueprint file path, dùng:

```text
06-lab-complete/render.yaml
```

5. Nhập các secret có `sync: false`, đặc biệt:

```env
OPENAI_API_KEY=sk-your-openai-key
REDIS_URL=redis://your-internal-render-redis-url
```

6. Confirm Blueprint sync.

`render.yaml` đang set:

- `runtime: docker`
- `rootDir: 06-lab-complete`
- `healthCheckPath: /ready`
- `autoDeployTrigger: commit`
- `OPENAI_MODEL=gpt-5-mini`

## Cài Render CLI

CLI không bắt buộc để deploy project này, nhưng nên cài nếu muốn validate Blueprint hoặc quản lý deploy từ terminal.

### macOS với Homebrew

```bash
brew update
brew install render
render login
```

### Linux/macOS bằng install script

```bash
curl -fsSL https://raw.githubusercontent.com/render-oss/cli/refs/heads/main/bin/install.sh | sh
render login
```

### Kiểm tra CLI

```bash
render --version
render services
```

### Validate Blueprint

Từ repo root:

```bash
render blueprints validate 06-lab-complete/render.yaml
```

Nếu muốn dùng CLI trong CI/CD, tạo Render API key rồi set:

```bash
export RENDER_API_KEY=rnd_your_api_key
```

## Test sau khi deploy Render

Giả sử Render URL là:

```text
https://your-service.onrender.com
```

Health:

```bash
curl -i https://your-service.onrender.com/health
curl -i https://your-service.onrender.com/ready
```

Dashboard:

```bash
curl -i https://your-service.onrender.com/
```

Public chat:

```bash
curl -i -X POST https://your-service.onrender.com/web/ask \
  -H "Content-Type: application/json" \
  -d '{"client_id":"browser-render-test","question":"What is this deployment running on?"}'
```

Protected API:

```bash
curl -i -X POST https://your-service.onrender.com/ask \
  -H "X-API-Key: your-secret-agent-key" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"render-api-test","question":"Explain Render health checks."}'
```

Auth fail:

```bash
curl -i -X POST https://your-service.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"render-api-test","question":"hello"}'
```

Kỳ vọng: HTTP `401`.

Metrics:

```bash
curl -i https://your-service.onrender.com/metrics
```

## Lỗi thường gặp trên Render

### `/ready` trả `503`

Kiểm tra:

- `REDIS_URL` đã đúng internal URL chưa
- Key Value/Redis instance có cùng workspace/region không
- Web Service đã redeploy sau khi thêm env chưa

### `/web/ask` trả `503`

Kiểm tra:

- `OPENAI_API_KEY` đúng chưa
- billing/quota OpenAI còn hoạt động không
- `OPENAI_MODEL` có quyền truy cập không
- Render logs có lỗi từ `OpenAI request failed` không

### Build fail

Kiểm tra:

- Web Service đang dùng Docker
- Root Directory là `06-lab-complete`
- Dockerfile nằm trong `06-lab-complete/Dockerfile`
- `requirements.txt` có thể install được

## OpenAI notes

App dùng OpenAI Responses API (`POST /v1/responses`) với `store: false` vì Redis đã giữ conversation state. Model mặc định là `gpt-5-mini` để cân bằng chi phí và chất lượng cho lab deployment.
