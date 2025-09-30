# Architecture — Real-Time Personal Finance Coach (AWS)

## Cloud Provider
**Amazon Web Services (AWS)**

## Why AWS for this MVP
- Easiest “no servers to manage” path with **ECS Fargate**.
- Managed streaming (**Kinesis**) + serverless Spark (**AWS Glue Streaming**) means less DevOps.
- **RDS for PostgreSQL** supports **TimescaleDB** extension for time-series.
- Simple static hosting for frontend via **S3 + CloudFront**.
- Built-in auth with **Cognito** and monitoring with **CloudWatch**.

## Services (MVP scope)
- **Frontend:** S3 (static site) + CloudFront (CDN)
- **API & Model Service:** ECS Fargate (Dockerized FastAPI)
- **Streaming Bus:** Kinesis Data Streams
- **Stream Processing (ETL):** AWS Glue Streaming job (Spark Structured Streaming)
- **Database:** Amazon RDS for PostgreSQL (+ TimescaleDB extension)
- **Object Storage:** S3 (artifacts, backups)
- **Auth:** Amazon Cognito (OAuth2/JWT)
- **Secrets:** AWS Secrets Manager
- **Monitoring & Logs:** CloudWatch (metrics, logs)
- **(Optional later)** Prometheus + Grafana (self-hosted on ECS) or Amazon Managed Grafana

## Data Flow (high level)
1. Frontend (React) calls backend APIs over HTTPS.
2. Backend ingests transactions → writes to **Kinesis**.
3. **AWS Glue Streaming (Spark)** reads from Kinesis, cleans/enriches data.
4. Cleaned data goes to **RDS (PostgreSQL + TimescaleDB)**.
5. Backend reads from RDS to power the dashboard and alerts.
6. Auth handled by **Cognito**; JWTs used for API requests.
7. Metrics/logs flow to **CloudWatch**.

## Mermaid Diagram
```mermaid
flowchart TD
  A[User Browser (React + TS)] -->|HTTPS| B[CloudFront CDN]
  B -->|Static files| C[S3 Frontend Bucket]

  A -->|API calls (JWT)| D[API Gateway (optional) --> FastAPI on ECS Fargate]
  D -->|Ingest| E[(Kinesis Data Streams)]
  E -->|Stream| F[AWS Glue Streaming (Spark)]
  F -->|Write| G[(RDS PostgreSQL + TimescaleDB)]
  D -->|Read/Write| G

  subgraph Security & Auth
    H[Cognito User Pool]
    I[AWS Secrets Manager]
  end
  A -->|Sign-in/OAuth2| H
  D -->|DB creds/API keys| I

  subgraph Observability
    J[CloudWatch Logs/Metrics]
  end
  D --> J
  F --> J
  G --> J
