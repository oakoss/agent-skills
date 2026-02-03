---
title: Monitoring
description: Observability tiers, monitoring tool selection, and deployment checklists for pre-launch through post-launch
tags:
  [monitoring, observability, sentry, datadog, deployment, checklist, alerting]
---

# Monitoring and Deployment Checklists

## Observability Tiers

Choose a monitoring stack based on the application's scale and budget.

### Basic Tier ($0-30/month)

Suitable for MVPs and small production apps.

| Category          | Tools                                             |
| ----------------- | ------------------------------------------------- |
| Error tracking    | Sentry (free tier: 5K errors/month)               |
| Uptime monitoring | UptimeRobot or BetterUptime (free tier)           |
| Logging           | Platform-provided logs (Vercel, Railway, Render)  |
| Performance       | Vercel Analytics, Cloudflare Web Analytics (free) |
| Alerting          | Sentry alerts, UptimeRobot notifications          |

Key metrics to track: error rate, uptime percentage, response time (p50/p95), deployment success rate.

### Enhanced Tier ($30-200/month)

Suitable for growing products with paying users.

| Category       | Tools                                         |
| -------------- | --------------------------------------------- |
| APM            | New Relic or Datadog APM (application traces) |
| Logging        | LogTail (Betterstack), Axiom, or Datadog Logs |
| Error tracking | Sentry with performance monitoring            |
| Uptime         | BetterUptime with status pages                |
| Alerting       | PagerDuty or Opsgenie for on-call rotation    |

Additional metrics: database query latency, cache hit rate, API endpoint latency by route, queue depth, memory/CPU utilization.

### Enterprise Tier ($300-2000+/month)

Suitable for high-scale applications with SLA requirements.

| Category                 | Tools                                          |
| ------------------------ | ---------------------------------------------- |
| Full-stack observability | Datadog, New Relic, or Grafana Cloud           |
| Distributed tracing      | OpenTelemetry with Jaeger or Datadog APM       |
| Log aggregation          | Datadog Logs, Elastic/OpenSearch, Grafana Loki |
| Metrics                  | Prometheus + Grafana or Datadog Metrics        |
| Alerting                 | PagerDuty with escalation policies             |
| Status pages             | Statuspage.io or BetterUptime                  |

Additional capabilities: distributed tracing across services, custom dashboards, SLO/SLI tracking, cost attribution per service, anomaly detection.

## Alerting Strategy

### Alert Severity Levels

| Level         | Response Time       | Examples                                 |
| ------------- | ------------------- | ---------------------------------------- |
| Critical (P0) | Immediate (< 5 min) | Site down, data loss, security breach    |
| High (P1)     | < 30 min            | Error rate spike, payment failures       |
| Medium (P2)   | < 4 hours           | Elevated latency, degraded performance   |
| Low (P3)      | Next business day   | Non-critical warnings, capacity planning |

### Alert Best Practices

- Alert on symptoms (error rate, latency), not causes (CPU usage)
- Set meaningful thresholds based on baseline data, not arbitrary numbers
- Include runbook links in alert notifications
- Avoid alert fatigue: fewer, actionable alerts are better than many noisy ones
- Use separate notification channels for different severity levels

## Deployment Checklists

### Pre-Launch Checklist

**Infrastructure**:

- Environment variables configured for all environments
- Database migrations tested against production-like data
- SSL/HTTPS enabled and certificates valid
- Custom domain connected with proper DNS records
- CDN configured for static assets

**Application**:

- Error monitoring configured and verified (trigger a test error)
- Logging captures request context (request ID, user ID)
- Health check endpoint returns service status
- Rate limiting configured on public endpoints
- CORS settings restrict to known origins

**Security**:

- Secrets stored in platform secret management (not in code)
- Database credentials rotated from development defaults
- Security headers configured (CSP, HSTS, X-Frame-Options)
- Dependency audit shows no critical vulnerabilities
- Authentication and authorization flows tested

**Operations**:

- Backup strategy defined and tested (database, file storage)
- Rollback procedure documented and tested
- On-call rotation established (for production apps with SLAs)
- Runbooks created for common failure scenarios

### Launch Day Checklist

- [ ] Deploy to production using standard pipeline
- [ ] Verify all pages/routes load correctly
- [ ] Test critical user flows end-to-end (signup, login, core actions)
- [ ] Check error monitoring dashboard for new errors
- [ ] Verify response times are within acceptable range
- [ ] Confirm analytics/tracking events fire correctly
- [ ] Test from multiple geographic regions if applicable
- [ ] Rollback plan ready and tested

### Post-Launch Checklist (First 48 Hours)

- [ ] Monitor error rates and investigate any new error patterns
- [ ] Review response time trends (p50, p95, p99)
- [ ] Check database query performance for slow queries
- [ ] Verify analytics data is collecting accurately
- [ ] Review infrastructure costs against projections
- [ ] Document any issues encountered and resolutions
- [ ] Plan capacity scaling strategy based on observed load
- [ ] Schedule regular review cadence (weekly for first month)

## Structured Logging

Use structured logging (JSON format) for machine-parseable logs that integrate with log aggregation tools.

Key fields to include in every log entry:

| Field       | Purpose                                   |
| ----------- | ----------------------------------------- |
| `timestamp` | When the event occurred (ISO 8601)        |
| `level`     | Severity: debug, info, warn, error        |
| `message`   | Human-readable description                |
| `requestId` | Correlation ID for request tracing        |
| `service`   | Service name in microservices             |
| `duration`  | Operation duration in milliseconds        |
| `error`     | Error message and stack trace (on errors) |

## SLO/SLI Framework

Define Service Level Objectives (SLOs) based on Service Level Indicators (SLIs) to measure reliability.

| SLI                | Measurement                          | Typical SLO                     |
| ------------------ | ------------------------------------ | ------------------------------- |
| Availability       | Successful requests / total requests | 99.9% (8.7 hours downtime/year) |
| Latency (p50)      | Median response time                 | < 200ms                         |
| Latency (p95)      | 95th percentile response time        | < 1s                            |
| Error rate         | 5xx responses / total responses      | < 0.1%                          |
| Deployment success | Successful deploys / total deploys   | > 95%                           |

Track error budget (100% - SLO) to balance reliability investment against feature velocity.
