---
title: Releases & Search
description: GitHub CLI releases, attestation verification, search across repos, gists, and SSH/GPG key management
tags: [gh-cli, releases, attestation, search, gists, ssh-keys, gpg-keys, verify]
---

# Releases & Search

## Releases

### Create

```bash
gh release create v1.0.0
gh release create v1.0.0 --title "Version 1.0" --notes "Release notes"
gh release create v1.0.0 --generate-notes
gh release create v1.0.0 --generate-notes --notes-start-tag v0.9.0
gh release create v1.0.0 --draft
gh release create v1.0.0 --prerelease
gh release create v1.0.0 --target release-branch
gh release create v1.0.0 ./dist/app.zip ./dist/app.tar.gz
gh release create v1.0.0 --notes-file release-notes.md
```

### List and View

```bash
gh release list
gh release list --limit 10
gh release list --json tagName,publishedAt,isPrerelease
gh release view v1.0.0
gh release view v1.0.0 --web
gh release view v1.0.0 --json assets
```

### Edit

```bash
gh release edit v1.0.0 --title "Updated Title"
gh release edit v1.0.0 --notes "Updated notes"
gh release edit v1.0.0 --draft=false
gh release edit v1.0.0 --prerelease=false
gh release edit v1.0.0 --latest
```

### Upload and Download Assets

```bash
gh release upload v1.0.0 ./dist/app.zip
gh release upload v1.0.0 ./dist/app.zip --clobber
gh release download v1.0.0
gh release download v1.0.0 --pattern "*.tar.gz"
gh release download v1.0.0 --dir ./downloads
gh release delete-asset v1.0.0 app.zip
```

### Delete

```bash
gh release delete v1.0.0 --yes
gh release delete v1.0.0 --cleanup-tag --yes
```

### Verify Release Artifacts

```bash
gh release verify v1.0.0
gh release verify-asset v1.0.0 app.zip
```

## Attestation

Verify supply chain attestations for artifacts:

```bash
gh attestation verify artifact.tar.gz --owner owner
gh attestation verify artifact.tar.gz --repo owner/repo
gh attestation download artifact.tar.gz --owner owner
gh attestation trusted-root
```

## Search

### Search Repositories

```bash
gh search repos "react hooks" --limit 10
gh search repos "react hooks" --language typescript
gh search repos "cli tool" --stars ">100"
gh search repos "api" --owner my-org
gh search repos "react" --json fullName,description,stargazersCount
```

### Search Issues and PRs

```bash
gh search issues "bug authentication" --repo owner/repo
gh search issues "memory leak" --state open --label bug
gh search issues "feature request" --assignee @me
gh search prs "fix memory leak" --state open
gh search prs "refactor" --repo owner/repo --merged
```

### Search Code

```bash
gh search code "function handleAuth" --repo owner/repo
gh search code "TODO" --owner my-org --language typescript
gh search code "import express" --filename "server.ts"
```

### Search Commits

```bash
gh search commits "fix auth" --repo owner/repo
gh search commits "bump version" --author user1
```

## Gists

```bash
gh gist create file.txt --public
gh gist create file.txt --desc "Description"
gh gist create file1.txt file2.txt
echo "Hello" | gh gist create --filename hello.txt
gh gist list
gh gist list --public --limit 20
gh gist view GIST_ID
gh gist view GIST_ID --raw
gh gist edit GIST_ID
gh gist clone GIST_ID
gh gist rename GIST_ID old-name.txt new-name.txt
gh gist delete GIST_ID --yes
```

## SSH Keys

```bash
gh ssh-key list
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My laptop"
gh ssh-key add ~/.ssh/id_ed25519.pub --type signing
gh ssh-key delete KEY_ID --yes
```

## GPG Keys

```bash
gh gpg-key list
gh gpg-key add key.gpg
gh gpg-key delete KEY_ID --yes
```
