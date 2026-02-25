---
title: Nushell Structured Data
description: Using Nushell as a structured data engine for tables, APIs, scripting, and interoperability with standard Unix tools
tags: [nushell, structured-data, tables, API, shell-scripting, unix-interop]
---

# Nushell Structured Data

Nushell (Nu) is a modern shell that works with structured data (tables) rather than raw strings. Every command output is a table, making data manipulation intuitive and type-safe.

## The Table Paradigm

In Nushell, all command output is structured. No more parsing text with `awk` and `sed`.

```bash
# List files over 1MB, sorted by size
ls | where size > 1mb | sort-by size

# Get top 5 processes by memory usage
ps | sort-by mem | last 5

# Count files by extension
ls **/* | group-by {|f| $f.name | path parse | get extension} | transpose ext count | sort-by count -r

# Filter and transform in a single pipeline
ls | where type == "file" | select name size | sort-by size -r | first 10
```

## Working with APIs

Nushell handles HTTP requests and JSON natively.

```bash
# Fetch a JSON API and extract a field
http get https://api.github.com/repos/nushell/nushell | get stargazers_count

# POST with JSON body
http post https://api.example.com/data {name: "test", active: true}

# Fetch and filter API results
http get https://api.github.com/users/octocat/repos | where stargazers_count > 100 | select name stargazers_count

# Convert between formats
open data.csv | save data.json
open config.yaml | to json
```

## Scripting with Nushell

Nushell scripts are typed, eliminating common shell scripting bugs like word splitting and globbing.

```bash
# Typed function with error handling
def deploy-check [env: string] {
  let status = (http get $"https://($env).example.com/health")
  if $status.ok {
    print $"($env) is healthy"
  } else {
    error make {msg: $"Deploy check failed for ($env)"}
  }
}

# Function with default parameters
def search-logs [pattern: string, --lines(-n): int = 100] {
  open app.log | lines | where {|line| $line | str contains $pattern} | last $lines
}

# Pipeline as a variable
let large_files = (ls **/* | where size > 10mb | sort-by size -r)
$large_files | each {|f| print $"Large file: ($f.name) - ($f.size)"}
```

## Data Format Conversion

```bash
# CSV to JSON
open data.csv | to json | save data.json

# JSON to YAML
open config.json | to yaml | save config.yaml

# TSV to table display
open data.tsv | table

# Space-separated values to structured table
"10240 src/app" | from ssv | rename size path
```

## Unix Interoperability

Move between Nushell tables and standard Unix text with `to text` and `from ssv`.

```bash
# Convert Unix command output to a Nushell table
du -sk * | from ssv | rename size path | upsert size {|r| $r.size | into int} | sort-by size -r | first 10

# Pipe Nushell output to Unix tools
ls | get name | to text | xargs wc -l

# Use external commands and capture output
let result = (^git log --oneline -10 | lines)
$result | length
```

## Audit Pipelines

```bash
# Audit disk usage as formatted JSON
du -sk * | from ssv | rename size path | upsert size {|r| $r.size | into int} | sort-by size -r | first 10 | to json

# Find duplicate files by size
ls **/* | where type == "file" | group-by size | where {|g| ($g.items | length) > 1} | each {|g| $g.items | get name}

# Summarize git log by author
^git log --format="%an" | lines | uniq -c | sort-by count -r | first 10
```

## Advantages Over Traditional Shell

| Issue               | Bash/Zsh                       | Nushell                            |
| ------------------- | ------------------------------ | ---------------------------------- |
| Word splitting bugs | Common with unquoted variables | Not possible (typed values)        |
| Globbing surprises  | `*` expands unexpectedly       | Explicit glob operator             |
| Error handling      | `set -e` or manual checks      | Built-in error propagation         |
| Data processing     | Pipe through awk/sed/grep      | Native table operations            |
| Type safety         | Everything is a string         | Numbers, dates, durations, records |
| Parallel execution  | Complex `xargs` or `parallel`  | `par-each` built-in                |
