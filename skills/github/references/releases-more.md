---
title: Releases & More
description: GitHub CLI releases, gists, SSH/GPG key management, search, and API requests
tags: [gh-cli, releases, gists, ssh-keys, gpg-keys, search, api]
---

# Releases & More

## Releases

```bash
gh release list
gh release create v1.0.0 --title "Version 1.0" --notes "Release notes"
gh release create v1.0.0 --generate-notes
gh release upload v1.0.0 ./dist/app.zip
gh release download v1.0.0
gh release delete v1.0.0
```

## Gists

```bash
gh gist create file.txt --public
echo "Hello" | gh gist create -
gh gist list
gh gist view GIST_ID
gh gist edit GIST_ID
```

## SSH Keys

```bash
gh ssh-key list
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My laptop"
```

## GPG Keys

```bash
gh gpg-key list
gh gpg-key add key.gpg
```

## Search

```bash
gh search repos "react hooks" --limit 10
gh search issues "bug authentication" --repo owner/repo
gh search prs "fix memory leak" --state open
gh search code "function handleAuth" --repo owner/repo
```

## API

```bash
gh api repos/owner/repo
gh api repos/owner/repo/issues -f title="New issue" -f body="Description"
gh api graphql -f query='{ viewer { login } }'
gh api repos/owner/repo/issues --paginate
```
