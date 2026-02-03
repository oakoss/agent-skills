#!/usr/bin/env node
'use strict';

const https = require('https');
const { execFileSync } = require('child_process');

const ANSI_RE = /\x1b\[[0-9;]*m/g;
const ANSI_RESET = '\x1b[0m';
const ANSI_BOLD = '\x1b[1m';
const ANSI_BLUE = '\x1b[34m';
const ANSI_GRAY = '\x1b[90m';

function stripAnsi(text) {
  return text.replace(ANSI_RE, '');
}

function style(text, ansi) {
  return `${ansi}${text}${ANSI_RESET}`;
}

function formatName(text) {
  return style(text, ANSI_BOLD);
}

function formatUrl(text) {
  return style(text, ANSI_BLUE);
}

function formatDescription(text) {
  return style(text, ANSI_GRAY);
}

function decodeHtml(text) {
  return text
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(Number(code)))
    .replace(/&amp;/g, '&');
}

function stripTags(html) {
  return html.replace(/<[^>]+>/g, ' ');
}

function collapseWhitespace(text) {
  return text.replace(/\s+/g, ' ').trim();
}

function runFind(query) {
  const parts = query.split(/\s+/).filter(Boolean);
  const output = execFileSync('pnpm', ['dlx', 'skills', 'find', ...parts], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  return output;
}

function parseResults(output) {
  const cleaned = stripAnsi(output);
  const lines = cleaned
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  const results = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (
      line.includes('@') &&
      line.includes('/') &&
      !line.includes('Install with')
    ) {
      let url = '';
      for (let j = i + 1; j < lines.length; j += 1) {
        if (lines[j].includes('skills.sh/')) {
          const parts = lines[j].split(/\s+/);
          url = parts[parts.length - 1];
          break;
        }
      }
      if (url) {
        results.push([line, url]);
      }
    }
  }
  return results;
}

function fetchUrl(url, timeoutMs, redirects = 0) {
  return new Promise((resolve, reject) => {
    const req = https.get(
      url,
      { headers: { 'User-Agent': 'agent-skills-find' } },
      (res) => {
        if (
          res.statusCode &&
          res.statusCode >= 300 &&
          res.statusCode < 400 &&
          res.headers.location
        ) {
          if (redirects >= 3) {
            reject(new Error('Too many redirects'));
            res.resume();
            return;
          }
          const nextUrl = new URL(res.headers.location, url).toString();
          res.resume();
          resolve(fetchUrl(nextUrl, timeoutMs, redirects + 1));
          return;
        }
        if (res.statusCode && res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}`));
          res.resume();
          return;
        }
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => resolve(data));
      },
    );
    req.on('error', reject);
    req.setTimeout(timeoutMs, () => {
      req.destroy(new Error('Request timeout'));
    });
  });
}

function extractMetaDescription(html) {
  const patterns = [
    /<meta[^>]+name="description"[^>]+content="([^"]+)"/i,
    /<meta[^>]+property="og:description"[^>]+content="([^"]+)"/i,
    /<meta[^>]+name='description'[^>]+content='([^']+)'/i,
    /<meta[^>]+property='og:description'[^>]+content='([^']+)'/i,
  ];
  for (const re of patterns) {
    const m = html.match(re);
    if (m && m[1]) {
      return collapseWhitespace(decodeHtml(m[1]));
    }
  }
  return null;
}

function extractFirstParagraph(html) {
  const idx = html.indexOf('prose');
  const slice = idx >= 0 ? html.slice(idx) : html;
  const m = slice.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
  if (!m || !m[1]) return null;
  const text = collapseWhitespace(decodeHtml(stripTags(m[1])));
  return text || null;
}

async function fetchDescription(url, timeoutMs) {
  const body = await fetchUrl(url, timeoutMs);
  const first = extractFirstParagraph(body);
  if (first) return first;
  const meta = extractMetaDescription(body);
  if (meta) return meta;
  return null;
}

function agentSkillsUrl(skillsUrl) {
  const m = skillsUrl.match(
    /^https?:\/\/skills\.sh\/([^/]+)\/([^/]+)\/([^/]+)/,
  );
  if (!m) return null;
  const [, owner, repo, skill] = m;
  return `https://agent-skills.md/skills/${owner}/${repo}/${skill}`;
}

function parseArgs(argv) {
  const args = {
    query: null,
    max: 10,
    timeout: 10,
    concurrency: 5,
    noFetch: false,
  };
  const rest = [];
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--max') {
      args.max = Number(argv[++i] || '10');
    } else if (token === '--timeout') {
      args.timeout = Number(argv[++i] || '10');
    } else if (token === '--concurrency') {
      args.concurrency = Number(argv[++i] || '5');
    } else if (token === '--no-fetch') {
      args.noFetch = true;
    } else if (token.startsWith('-')) {
      throw new Error(`Unknown option: ${token}`);
    } else {
      rest.push(token);
    }
  }
  args.query = rest.join(' ').trim();
  if (!args.query) {
    throw new Error('Missing query. Usage: enrich_find.js <query>');
  }
  return args;
}

async function mapWithConcurrency(items, limit, mapper) {
  const results = new Array(items.length);
  let index = 0;

  async function worker() {
    while (true) {
      const current = index;
      index += 1;
      if (current >= items.length) return;
      results[current] = await mapper(items[current], current);
    }
  }

  const workers = [];
  const count = Math.max(1, Math.min(limit, items.length));
  for (let i = 0; i < count; i += 1) {
    workers.push(worker());
  }
  await Promise.all(workers);
  return results;
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(String(err.message || err));
    process.exit(2);
  }

  let output;
  try {
    output = runFind(args.query);
  } catch (err) {
    console.error(String(err.message || err));
    process.exit(1);
  }

  const results = parseResults(output);
  if (results.length === 0) {
    console.log('No skills found.');
    return;
  }

  const timeoutMs = Math.max(1, args.timeout) * 1000;
  const maxCount = Math.max(0, args.max);
  const limited = results.slice(0, maxCount);

  if (args.noFetch) {
    for (const [name, url] of limited) {
      console.log(formatName(name));
      console.log(`└ ${formatUrl(url)}`);
      console.log(formatDescription('[description skipped]'));
      console.log('');
    }
    return;
  }

  const descriptions = await mapWithConcurrency(
    limited,
    Math.max(1, args.concurrency || 1),
    async ([, url]) => {
      let desc = null;
      try {
        desc = await fetchDescription(url, timeoutMs);
      } catch (_) {
        desc = null;
      }
      if (!desc) {
        const alt = agentSkillsUrl(url);
        if (alt) {
          try {
            desc = await fetchDescription(alt, timeoutMs);
          } catch (_) {
            desc = null;
          }
        }
      }
      return desc || '[no description found]';
    },
  );

  for (let i = 0; i < limited.length; i += 1) {
    const [name, url] = limited[i];
    console.log(formatName(name));
    console.log(`└ ${formatUrl(url)}`);
    console.log(formatDescription(descriptions[i]));
    console.log('');
  }
}

main().catch((err) => {
  console.error(String(err.message || err));
  process.exit(1);
});
