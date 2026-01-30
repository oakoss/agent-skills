---
title: Query Language
description: CASS query language including basic queries, boolean operators, wildcards, match types, auto-fuzzy fallback, and flexible time input formats
tags:
  [
    query,
    boolean,
    AND,
    OR,
    NOT,
    wildcard,
    prefix,
    suffix,
    fuzzy,
    match-type,
    time,
    date,
    ISO-8601,
  ]
---

# Query Language

## Basic Queries

| Query                     | Matches                                        |
| ------------------------- | ---------------------------------------------- |
| `error`                   | Messages containing "error" (case-insensitive) |
| `python error`            | Both "python" AND "error"                      |
| `"authentication failed"` | Exact phrase                                   |

## Boolean Operators

| Operator | Example            | Meaning                       |
| -------- | ------------------ | ----------------------------- |
| `AND`    | `python AND error` | Both terms required (default) |
| `OR`     | `error OR warning` | Either term matches           |
| `NOT`    | `error NOT test`   | First term, excluding second  |
| `-`      | `error -test`      | Shorthand for NOT             |

```bash
# Complex boolean query
cass search "authentication AND (error OR failure) NOT test" --robot

# Exclude test files
cass search "bug fix -test -spec" --robot

# Either error type
cass search "TypeError OR ValueError" --robot
```

## Wildcard Patterns

| Pattern    | Type      | Performance         |
| ---------- | --------- | ------------------- |
| `auth*`    | Prefix    | Fast (edge n-grams) |
| `*tion`    | Suffix    | Slower (regex)      |
| `*config*` | Substring | Slowest (regex)     |

## Match Types

Results include `match_type`:

| Type        | Meaning                        | Score Boost |
| ----------- | ------------------------------ | ----------- |
| `exact`     | Verbatim match                 | Highest     |
| `prefix`    | Via prefix expansion           | High        |
| `suffix`    | Via suffix pattern             | Medium      |
| `substring` | Via substring pattern          | Lower       |
| `fuzzy`     | Auto-fallback (sparse results) | Lowest      |

## Auto-Fuzzy Fallback

When exact query returns <3 results, CASS automatically retries with wildcards:

- `auth` → `*auth*`
- Results flagged with `wildcard_fallback: true`

## Flexible Time Input

CASS accepts a wide variety of time/date formats:

| Format             | Examples                               |
| ------------------ | -------------------------------------- |
| **Relative**       | `-7d`, `-24h`, `-30m`, `-1w`           |
| **Keywords**       | `now`, `today`, `yesterday`            |
| **ISO 8601**       | `2024-11-25`, `2024-11-25T14:30:00Z`   |
| **US Dates**       | `11/25/2024`, `11-25-2024`             |
| **Unix Timestamp** | `1732579200` (seconds or milliseconds) |
