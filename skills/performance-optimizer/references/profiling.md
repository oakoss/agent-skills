---
title: Profiling and Measurement
description: Frontend profiling with Chrome DevTools and React Profiler, backend profiling for Node.js and Python, database query profiling for PostgreSQL and MongoDB
tags:
  [
    profiling,
    chrome-devtools,
    react-profiler,
    node-profiling,
    python-profiling,
    database-profiling,
  ]
---

# Profiling and Measurement

**Goal**: Identify actual bottlenecks, not perceived ones.

## Frontend Profiling

### Chrome DevTools

```javascript
// 1. Performance tab → Record → Reload page
// 2. Analyze:
//    - Main thread activity
//    - Network waterfall
//    - JavaScript execution time
//    - Rendering time

// 3. Lighthouse audit
// Run: chrome://lighthouse or `npm i -g lighthouse`
lighthouse https://yoursite.com --view
```

### React DevTools Profiler

```javascript
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

<Profiler id="ExpensiveComponent" onRender={onRenderCallback}>
  <ExpensiveComponent />
</Profiler>;
```

## Backend Profiling

### Node.js

```bash
# Generate CPU profile
node --prof app.js

# Process profile
node --prof-process isolate-0x*.log > processed.txt

# Flame graphs (better visualization)
npm i -g 0x
0x app.js
```

### Python

```python
import cProfile
import pstats

# Profile function
cProfile.run('slow_function()', 'output.prof')

# Analyze
p = pstats.Stats('output.prof')
p.sort_stats('cumulative').print_stats(20)
```

## Database Profiling

### PostgreSQL

```sql
-- Enable query logging
ALTER DATABASE yourdb SET log_min_duration_statement = 100; -- Log queries >100ms

-- Analyze query
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE email = 'test@example.com';

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### MongoDB

```javascript
// Enable profiling
db.setProfilingLevel(1, { slowms: 100 });

// View slow queries
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 });

// Explain query
db.collection.find({ email: 'test@example.com' }).explain('executionStats');
```
