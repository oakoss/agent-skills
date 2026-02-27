---
title: Release Pipeline
description: Supply chain security with cargo-deny, binary distribution with cargo-dist, and changelog automation with release-plz
tags:
  [
    cargo-deny,
    cargo-dist,
    release-plz,
    security,
    license,
    audit,
    distribution,
    changelog,
    semver,
  ]
---

# Release Pipeline

## cargo-deny: Supply Chain Security

cargo-deny audits dependencies for license compliance, known vulnerabilities, yanked crates, and source restrictions.

```bash
cargo install cargo-deny
cargo deny init
cargo deny check
```

### Configuration

```toml
# deny.toml
[advisories]
vulnerability = "deny"
unmaintained = "warn"
yanked = "deny"
notice = "warn"
ignore = []

[licenses]
unlicensed = "deny"
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-3.0",
]
copyleft = "deny"

[[licenses.clarify]]
name = "ring"
expression = "MIT AND ISC AND OpenSSL"
license-files = [{ path = "LICENSE", hash = 0xbd0eed23 }]

[bans]
multiple-versions = "warn"
wildcards = "deny"
highlight = "all"
skip = []

# Deny specific crates
deny = [
    { name = "openssl" },
]

[sources]
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
```

### CI Integration

```yaml
# .github/workflows/ci.yml
- name: Check dependencies
  uses: EmbarkStudios/cargo-deny-action@v2
  with:
    command: check
    arguments: --all-features
```

```bash
# Check specific categories
cargo deny check advisories
cargo deny check licenses
cargo deny check bans
cargo deny check sources

# Check all
cargo deny check
```

## cargo-dist: Binary Distribution

cargo-dist automates building and distributing pre-built binaries across platforms, with support for installers and package manager taps.

```bash
cargo install cargo-dist
cargo dist init
```

### Configuration

```toml
# Cargo.toml
[workspace.metadata.dist]
cargo-dist-version = "0.27.0"
ci = "github"
installers = ["shell", "powershell", "homebrew"]
targets = [
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
    "aarch64-unknown-linux-gnu",
    "x86_64-pc-windows-msvc",
]
tap = "myorg/homebrew-tap"
publish-jobs = ["homebrew"]

[workspace.metadata.dist.github-custom-runners]
aarch64-unknown-linux-gnu = "ubuntu-22.04-arm"
```

### Generated CI Workflow

Running `cargo dist init` generates a GitHub Actions workflow at `.github/workflows/release.yml` that builds binaries, creates GitHub releases, and publishes to configured installers when a tag is pushed.

```bash
# Preview what a release would produce
cargo dist plan

# Build for the current platform
cargo dist build

# Generate CI configuration
cargo dist generate
```

### Installer Output

After release, users can install via:

```bash
# Shell installer (macOS/Linux)
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/org/repo/releases/latest/download/myapp-installer.sh | sh

# PowerShell installer (Windows)
powershell -ExecutionPolicy ByPass -c "irm https://github.com/org/repo/releases/latest/download/myapp-installer.ps1 | iex"

# Homebrew
brew install myorg/tap/myapp
```

## release-plz: Automated Releases

release-plz automates changelog generation, version bumping based on conventional commits, and crate publishing.

```bash
cargo install release-plz
```

### Configuration

```toml
# release-plz.toml
[workspace]
changelog_config = "cliff.toml"
publish = true
git_release_enable = true
git_tag_enable = true

[[package]]
name = "my-crate"
semver_check = true

[[package]]
name = "my-internal-crate"
publish = false
```

### Changelog Configuration

```toml
# cliff.toml (git-cliff format)
[changelog]
header = "# Changelog\n\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})\
{% endfor %}
{% endfor %}
"""

[git]
conventional_commits = true
commit_parsers = [
    { message = "^feat", group = "Features" },
    { message = "^fix", group = "Bug Fixes" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Refactoring" },
    { message = "^doc", group = "Documentation" },
]
```

### CI Integration

```yaml
# .github/workflows/release-plz.yml
name: Release-plz

on:
  push:
    branches: [main]

jobs:
  release-plz:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: dtolnay/rust-toolchain@stable
      - uses: MarcoIeni/release-plz-action@v0.5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
```

### Commands

```bash
# Preview what changes would be made
release-plz update --dry-run

# Update changelogs and bump versions
release-plz update

# Create a release PR
release-plz release-pr

# Publish to crates.io
release-plz release
```

## Complete CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  CARGO_TERM_COLOR: always
  RUSTFLAGS: '-Dwarnings'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt
      - uses: Swatinem/rust-cache@v2

      - name: Format
        run: cargo fmt --all -- --check

      - name: Clippy
        run: cargo clippy --all-targets --all-features

      - name: Test
        run: cargo test --all-features

      - name: Deny
        uses: EmbarkStudios/cargo-deny-action@v2

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - name: Install cargo-llvm-cov
        uses: taiki-e/install-action@cargo-llvm-cov
      - name: Coverage
        run: cargo llvm-cov --all-features --lcov --output-path lcov.info
```

## Docker Multi-Stage Build

```dockerfile
FROM rust:1.83-slim AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

COPY src/ src/
RUN touch src/main.rs
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/myapp /usr/local/bin/
ENTRYPOINT ["myapp"]
```
