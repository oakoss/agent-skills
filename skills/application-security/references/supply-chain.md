---
title: Supply Chain Security
description: SBOM generation, dependency scanning, CI/CD pipeline hardening, artifact signing, and lockfile integrity
tags: [supply-chain, sbom, dependencies, ci-cd, artifact-signing, lockfile]
---

# Supply Chain Security

Software Supply Chain Failures is ranked #3 in the OWASP Top 10 (2025), expanding beyond vulnerable components to cover the entire ecosystem of dependencies, build systems, and distribution.

## Dependency Management

### Lockfile Integrity

Always commit lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`). Use `--frozen-lockfile` in CI to prevent unexpected dependency changes.

```bash
# CI installation — fails if lockfile is out of sync
pnpm install --frozen-lockfile

# Audit for known vulnerabilities
pnpm audit --audit-level=high
```

### Automated Scanning

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10
    groups:
      production:
        dependency-type: production
      development:
        dependency-type: development
```

Supplement Dependabot with runtime scanning tools (Snyk, Socket, OWASP Dependency-Check) that detect malicious packages, not just known CVEs.

### Reducing Attack Surface

```bash
# Find unused dependencies
npx depcheck

# Remove unnecessary packages
pnpm remove unused-package
```

Minimize dependency count. Prefer well-maintained packages with active security response teams. Check download counts, last publish date, and maintainer count before adopting new dependencies.

## SBOM (Software Bill of Materials)

Generate machine-readable SBOMs in CycloneDX or SPDX format as part of every release. SBOMs enable rapid incident response when a vulnerability is discovered in a transitive dependency.

```bash
# Generate CycloneDX SBOM from package-lock.json
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Generate SPDX SBOM
npx spdx-sbom-generator -o sbom-spdx.json
```

Automate SBOM generation in CI/CD so every build produces an updated inventory. Store SBOMs alongside release artifacts for auditing and compliance.

## CI/CD Pipeline Hardening

### Access Control

```yaml
# GitHub Actions — principle of least privilege
permissions:
  contents: read
  packages: write
```

- Enforce MFA for all accounts with write access to repositories and registries
- Use short-lived tokens (OIDC) instead of long-lived secrets where possible
- Require code review and branch protection on main/release branches
- Use ephemeral CI runners (containers/VMs destroyed after each job)

### Build Reproducibility

```bash
# Pin action versions by SHA, not mutable tags
# BAD: uses: actions/checkout@v4 (mutable tag)
# GOOD: uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

Pin all CI action versions to full commit SHAs to prevent supply chain attacks via tag hijacking. Use `npm ci` or `pnpm install --frozen-lockfile` to ensure deterministic installs.

### Secret Scanning

```yaml
# GitHub Actions — scan for leaked secrets
- name: Secret scan
  uses: trufflesecurity/trufflehog@main
  with:
    extra_args: --only-verified
```

Scan repositories for accidentally committed secrets (API keys, tokens, passwords). Block pushes containing secrets using pre-commit hooks or server-side push rules.

## Artifact Signing and Provenance

Sign release artifacts and container images to verify they have not been tampered with. Use Sigstore/cosign for container image signing or npm provenance for package publishing.

```bash
# Publish npm package with provenance (links package to source repo and build)
npm publish --provenance

# Sign container images with cosign
cosign sign --key cosign.key your-registry.com/your-image:tag
```

Provenance attestations let consumers verify that an artifact was built from the expected source code by a trusted build system.

## Monitoring and Response

### Vulnerability Alerting

- Enable GitHub security advisories and Dependabot alerts
- Configure Snyk or Socket for real-time dependency risk monitoring
- Subscribe to security mailing lists for critical dependencies
- Monitor the OSV (Open Source Vulnerabilities) database

### Incident Response Drill

Periodically simulate a supply chain incident:

1. Identify which services use the affected package (via SBOM)
2. Determine exposure window (when vulnerable version was deployed)
3. Roll back or patch affected deployments
4. Rotate any potentially compromised credentials
5. Communicate status to stakeholders

### Key Metrics

| Metric                                   | Target       |
| ---------------------------------------- | ------------ |
| Services with generated SBOMs            | 100%         |
| Mean time to remediate critical dep CVEs | Under 72h    |
| Repos with branch protection             | 100%         |
| CI pipelines with dependency scanning    | 100%         |
| Artifacts with signed provenance         | All releases |
