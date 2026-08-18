# Practical Task 3 — Deployed Agent API with Automated Workflow

## Autonomous Research Agent API

This project implements a FastAPI autonomous research agent integrated with an automated n8n workflow.

## Technologies

- Python
- FastAPI
- Uvicorn
- Groq LLM
- REST API
- Background Tasks
- Rate Limiting
- n8n
- Email Automation

## API Endpoints

### Health Check

`GET /health`

Returns the API health status.

Example:

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Synchronous Research

`POST /research`

Runs the autonomous research agent and returns a structured result.

Example request:

```json
{
  "topic": "Explain the difference between training and testing data in machine learning.",
  "max_retries": 2
}
```

The endpoint was successfully tested with HTTP `200`.

### Streaming Research

`POST /research/stream`

Runs the research process and streams agent state updates/results.

The endpoint was tested successfully with HTTP `200`.

### Asynchronous Research

`POST /research/async`

Accepts a research job and returns immediately while the actual research runs in the background.

Example:

```json
{
  "topic": "Explain the difference between training, validation, and testing data in machine learning.",
  "max_retries": 2
}
```

Successful response:

```json
{
  "job_id": "example-job-id",
  "status": "accepted",
  "topic": "Explain the difference between training, validation, and testing data in machine learning.",
  "message": "Research job accepted and will run in the background."
}
```

The endpoint returns HTTP `202 Accepted`.

### Background Job Status

`GET /research/async/{job_id}`

Returns the current status of a background research job.

Possible states include:

- accepted
- running
- completed
- failed

## Request Validation

The API validates request bodies using FastAPI/Pydantic.

Sending `/research` without the required `topic` field produces:

`HTTP 422 Unprocessable Entity`

Example:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "topic"],
      "msg": "Field required"
    }
  ]
}
```

## Rate Limiting

The API implements client-based rate limiting.

Configuration:

- Maximum requests: 10
- Time window: 60 seconds

When the limit is exceeded:

`HTTP 429 Too Many Requests`

Example:

```json
{
  "detail": "Rate limit exceeded. Maximum 10 requests per minute."
}
```

## Automated n8n Workflow

The FastAPI API is connected to an n8n workflow.

Workflow:

```text
Schedule Trigger
       |
       v
 HTTP Request
       |
   +---+---+
   |       |
Success   Error
   |       |
   v       v
 Code     Code
   |       |
   v       v
 Email    Email
```

### Success Path

```text
Schedule Trigger
        ↓
HTTP Request
        ↓
Success
        ↓
Code in JavaScript
        ↓
Send an Email
```

The successful email contains the research report and metadata such as:

- Research topic
- Quality score
- Retry count
- Tokens used
- Duration

### Error Path

```text
Schedule Trigger
        ↓
HTTP Request
        ↓
Error
        ↓
Code in JavaScript
        ↓
Send an Email
```

The error email reports that the FastAPI research endpoint failed and includes the error information.

## Testing Results

| Test | Result |
|---|---|
| `GET /health` | HTTP 200 |
| `POST /research` | HTTP 200 |
| `POST /research/stream` | HTTP 200 |
| `POST /research/async` | HTTP 202 |
| `GET /research/async/{job_id}` | HTTP 200 |
| Invalid `/research` request | HTTP 422 |
| Rate limit exceeded | HTTP 429 |
| n8n success workflow | Successful |
| n8n error workflow | Successful |

## Example Successful Research

A successful research request returned:

```text
Quality Score: 0.74
Retry Count: 2
Tokens Used: 14581
Duration: 89.42 seconds
```

The generated report contained:

- Summary
- Findings
- Limitations
- Conclusion

## Error Handling

The system handles:

1. Request validation errors
2. API rate limiting
3. Background job failures
4. External LLM/API errors
5. n8n HTTP request errors
6. Automated error email notifications

An external LLM rate-limit error can cause an asynchronous job to enter the `failed` state while the FastAPI service itself remains operational.

## Project Demonstration

This project demonstrates:

- Deployed FastAPI agent API
- Autonomous research execution
- Structured API responses
- Streaming responses
- Background asynchronous processing
- Job status tracking
- Request validation
- HTTP 429 rate limiting
- Scheduled n8n automation
- Success/error branching
- Automated email notifications
- Execution monitoring

## Conclusion

The project combines an autonomous research agent API with asynchronous processing and an automated n8n workflow.

The API receives research topics, executes the research process, returns structured results, supports streaming, and runs jobs in the background.

The n8n workflow provides scheduled execution and automated email notifications for both successful and failed API requests.
