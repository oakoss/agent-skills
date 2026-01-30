---
title: Git Internals
description: Object model (blobs, trees, commits), SHA hashing, the index, references, packfiles, and garbage collection
tags: [git-internals, object-model, sha, reflog, fsck, packfiles]
---

# Git Internals

Understanding how Git stores data enables effective debugging and recovery.

## The Content-Addressable Store

Git is a persistent map of SHA hash keys to objects:

- **Blobs**: File contents (just the data, no filename)
- **Trees**: Directory structures (pointing to blobs and other trees)
- **Commits**: Snapshots of the tree with metadata (author, message, parent)

```bash
# Inspect any object
git cat-file -p <hash>

# Show object type
git cat-file -t <hash>

# Show the tree of a commit
git cat-file -p HEAD^{tree}
```

## Object Identification (SHA-256)

Git uses SHA hashing for collision resistance and content verification. Every object (blob, tree, commit, tag) gets a unique hash.

```bash
# Hash a file to see what Git would name it
git hash-object path/to/file

# Verify repository integrity
git fsck --full
```

## The Index (Staging Area)

The index is a binary file (`.git/index`) that prepares the next commit. It serves as the bridge between the working directory and the repository.

```bash
# See exactly what is in the index
git ls-files --stage

# Compare working directory to index
git diff

# Compare index to last commit
git diff --cached
```

## References and Symbolic Refs

- **Heads**: Local branches (`refs/heads/`)
- **Remotes**: Remote tracking branches (`refs/remotes/`)
- **Tags**: Version markers (`refs/tags/`)
- **HEAD**: Symbolic ref pointing to the current branch or commit

```bash
# Show where HEAD points
git symbolic-ref HEAD

# Show all refs
git show-ref

# Show the reflog (history of HEAD changes)
git reflog
```

## Data Recovery

```bash
# Find lost commits via reflog
git reflog --all

# Find dangling objects (unreachable commits, blobs)
git fsck --unreachable

# Recover a lost commit
git cherry-pick <hash-from-reflog>

# Recover a deleted branch
git checkout -b recovered-branch <hash-from-reflog>
```

## Packfiles and Garbage Collection

Git compresses objects into packfiles to save space:

```bash
# Run cleanup and optimization
git gc

# Remove unreachable objects
git prune

# Show pack statistics
git count-objects -v

# Verify pack integrity
git verify-pack -v .git/objects/pack/*.idx
```

## Repository Size Management

```bash
# Find large objects in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sort -k3 -n -r | head -20

# Remove a file from all history (use with caution)
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch path/to/large-file' HEAD
```
