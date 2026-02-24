import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join, resolve, basename, dirname } from 'path';

const SKILLS_DIR = 'skills';
const SKILL_MAX_LINES = 500;
const SKILL_WARN_LINES = 400;
const SKILL_TARGET_LINES = 150;
const REF_MAX_LINES = 750;
const REF_WARN_LINES = 500;
const SKILLS_CLI_EXCLUDED = new Set(['README.md', 'metadata.json']);
const MIN_NAME_LENGTH = 4;
const RESERVED_WORDS = ['anthropic', 'claude'];
const MAX_DESCRIPTION_LENGTH = 1024;

interface Frontmatter {
  [key: string]: string | string[];
}

interface ParseResult {
  data: Frontmatter | null;
  error: string | null;
}

interface ValidationResult {
  errors: string[];
  warnings: string[];
}

const COMMON_WORDS = new Set([
  'use',
  'when',
  'for',
  'the',
  'and',
  'or',
  'to',
  'in',
  'on',
  'with',
  'this',
  'that',
  'is',
  'are',
  'be',
  'been',
  'being',
  'have',
  'has',
  'had',
  'do',
  'does',
  'did',
  'will',
  'would',
  'could',
  'should',
  'may',
  'might',
  'must',
  'shall',
  'can',
  'need',
  'about',
  'into',
  'through',
  'during',
  'before',
  'after',
  'above',
  'below',
  'from',
  'up',
  'down',
  'out',
  'off',
  'over',
  'under',
  'again',
  'further',
  'then',
  'once',
  'here',
  'there',
  'all',
  'each',
  'few',
  'more',
  'most',
  'other',
  'some',
  'such',
  'no',
  'nor',
  'not',
  'only',
  'own',
  'same',
  'so',
  'than',
  'too',
  'very',
  'just',
  'also',
  'now',
  'of',
  'a',
  'an',
  'as',
  'at',
  'by',
  'if',
  'it',
  'its',
  'any',
  'how',
  'what',
  'which',
  'who',
  'whom',
  'these',
  'those',
  'am',
  'was',
  'were',
  'you',
  'your',
  'they',
  'them',
  'their',
  'we',
  'our',
  'i',
  'me',
  'my',
  'he',
  'she',
  'him',
  'her',
  'his',
  'hers',
  'skill',
  'skills',
  'best',
  'practices',
  'patterns',
  'creating',
  'building',
  'implementing',
  'working',
  'handling',
  'managing',
  'using',
]);

const VAGUE_PATTERNS: [RegExp, string][] = [
  [/\bhelps?\s+with\b/, 'helps with'],
  [/\bworks?\s+with\b/, 'works with'],
  [/\bassists?\s+with\b/, 'assists with'],
  [/\bfor\s+working\s+with\b/, 'for working with'],
  [/\bhandles?\b/, 'handles'],
  [/\bmanages?\b/, 'manages'],
];

function parseFrontmatter(content: string): ParseResult {
  if (!content.startsWith('---')) {
    return {
      data: null,
      error: 'YAML frontmatter must start with --- on line 1',
    };
  }

  const lines = content.split('\n');
  let endIdx = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      endIdx = i;
      break;
    }
  }

  if (endIdx === -1) {
    return {
      data: null,
      error: 'Invalid YAML frontmatter: missing closing ---',
    };
  }

  const data: Frontmatter = {};
  let currentKey: string | null = null;
  let multilineValue = '';
  let inMultiline = false;

  for (let i = 1; i < endIdx; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed || trimmed.startsWith('#')) continue;

    if (inMultiline) {
      if (line.match(/^\S/) && line.includes(':')) {
        data[currentKey!] = multilineValue.trim();
        inMultiline = false;
      } else {
        multilineValue += (multilineValue ? '\n' : '') + trimmed;
        continue;
      }
    }

    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;

    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();

    if (value === '|' || value === '>') {
      currentKey = key;
      multilineValue = '';
      inMultiline = true;
      continue;
    }

    // Handle multi-line flow arrays: key:\n  [\n    val1,\n    val2,\n  ]
    if (value === '') {
      let nextNonEmpty = i + 1;
      while (nextNonEmpty < endIdx && !lines[nextNonEmpty].trim()) {
        nextNonEmpty++;
      }
      if (nextNonEmpty < endIdx && lines[nextNonEmpty].trim().startsWith('[')) {
        let arrayContent = '';
        let j = nextNonEmpty;
        while (j < endIdx) {
          arrayContent += ' ' + lines[j].trim();
          if (lines[j].trim().endsWith(']')) {
            break;
          }
          j++;
        }
        arrayContent = arrayContent.trim();
        if (arrayContent.startsWith('[') && arrayContent.endsWith(']')) {
          data[key] = arrayContent
            .slice(1, -1)
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean);
          i = j;
          continue;
        }
      }
    }

    value = value.replace(/^["']|["']$/g, '');

    if (value.startsWith('[') && value.endsWith(']')) {
      data[key] = value
        .slice(1, -1)
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
    } else {
      data[key] = value;
    }
  }

  if (inMultiline && currentKey) {
    data[currentKey] = multilineValue.trim();
  }

  return { data, error: null };
}

function extractTriggerWords(description: string): Set<string> {
  const words = description.toLowerCase().match(/[a-z]+/g) || [];
  return new Set(words.filter((w) => !COMMON_WORDS.has(w)));
}

function checkDescriptionConflicts(
  descriptions: Record<string, string>,
  threshold = 0.5,
): string[] {
  const warnings: string[] = [];
  const entries = Object.entries(descriptions);

  for (let i = 0; i < entries.length; i++) {
    const [name1, desc1] = entries[i];
    const words1 = extractTriggerWords(desc1);
    if (words1.size === 0) continue;

    for (let j = i + 1; j < entries.length; j++) {
      const [name2, desc2] = entries[j];
      const words2 = extractTriggerWords(desc2);
      if (words2.size === 0) continue;

      const intersection = new Set([...words1].filter((w) => words2.has(w)));
      const union = new Set([...words1, ...words2]);
      const similarity = intersection.size / union.size;

      if (similarity >= threshold) {
        const common = [...intersection].sort().slice(0, 5);
        warnings.push(
          `Similar descriptions: '${name1}' and '${name2}' ` +
            `(${Math.round(similarity * 100)}% overlap, common: ${common.join(', ')})`,
        );
      }
    }
  }

  return warnings;
}

function validateSkillMd(filePath: string, content: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const lines = content.split('\n');
  const lineCount = lines.length;

  const { data: frontmatter, error: fmError } = parseFrontmatter(content);

  if (fmError) {
    errors.push(fmError);
  } else if (frontmatter) {
    const dirName = basename(dirname(filePath));

    if (!frontmatter.name) {
      errors.push("Missing required field: 'name' in frontmatter");
    } else {
      const name = String(frontmatter.name);
      if (name.length > 64) {
        errors.push(
          `Field 'name' exceeds 64 characters (${name.length} chars)`,
        );
      } else if (name.length < MIN_NAME_LENGTH) {
        errors.push(
          `Field 'name' is too short (${name.length} chars, min ${MIN_NAME_LENGTH}). Use a descriptive name, not an abbreviation`,
        );
      } else if (!/^[a-z0-9-]+$/.test(name)) {
        errors.push(
          "Field 'name' must use only lowercase letters, numbers, and hyphens",
        );
      }

      if (name.startsWith('-') || name.endsWith('-')) {
        errors.push("Field 'name' must not start or end with a hyphen");
      }

      if (name.includes('--')) {
        errors.push("Field 'name' must not contain consecutive hyphens (--)");
      }

      for (const word of RESERVED_WORDS) {
        if (name.includes(word)) {
          errors.push(`Field 'name' contains reserved word '${word}'`);
        }
      }

      if (/<[^>]+>/.test(name)) {
        errors.push("Field 'name' must not contain XML tags");
      }

      if (name !== dirName) {
        errors.push(
          `Field 'name' (${name}) must match directory name (${dirName})`,
        );
      }
    }

    if (!frontmatter.description) {
      errors.push("Missing required field: 'description' in frontmatter");
    } else {
      const desc = String(frontmatter.description);
      if (desc.length > MAX_DESCRIPTION_LENGTH) {
        errors.push(
          `Field 'description' exceeds ${MAX_DESCRIPTION_LENGTH} characters (${desc.length} chars)`,
        );
      } else {
        if (/<[^>]+>/.test(desc)) {
          errors.push("Field 'description' must not contain XML tags");
        }

        const firstWord = desc.trim().split(/\s+/)[0]?.toLowerCase() || '';
        if (['i', 'you', 'we'].includes(firstWord)) {
          warnings.push(
            "Description should use third-person voice ('Extracts text from PDFs', not 'I help you' or 'You can use')",
          );
        }

        const descLower = desc.toLowerCase();
        if (!descLower.includes('use when') && !descLower.includes('use for')) {
          warnings.push(
            "Description should include trigger phrases like 'Use when...' or 'Use for...'",
          );
        }

        for (const [pattern, term] of VAGUE_PATTERNS) {
          if (pattern.test(descLower)) {
            warnings.push(
              `Vague term '${term}' in description - use specific triggers instead`,
            );
            break;
          }
        }

        if (descLower.includes('use for')) {
          const afterUseFor = descLower.split('use for')[1];
          const triggers = extractTriggerWords(afterUseFor || '');
          if (triggers.size < 5) {
            warnings.push(
              `Low trigger density: only ${triggers.size} keywords after 'Use for' (recommend 8+)`,
            );
          }
        }
      }
    }
  }

  if (lineCount > SKILL_MAX_LINES) {
    errors.push(
      `SKILL.md is ${lineCount} lines (max ${SKILL_MAX_LINES}). Split to references/`,
    );
  } else if (lineCount > SKILL_WARN_LINES) {
    warnings.push(
      `SKILL.md is ${lineCount} lines (target ~${SKILL_TARGET_LINES}, max ${SKILL_MAX_LINES})`,
    );
  }

  let inCodeBlock = false;
  let codeBlockStart = 0;
  for (let i = 0; i < lines.length; i++) {
    const stripped = lines[i].trim();
    if (stripped.startsWith('```')) {
      if (!inCodeBlock) {
        codeBlockStart = i + 1;
        const lang = stripped.slice(3).trim();
        if (!lang) {
          errors.push(
            `Line ${i + 1}: Code block missing language specifier (MD040)`,
          );
        }
      }
      inCodeBlock = !inCodeBlock;
    }
  }

  if (inCodeBlock) {
    errors.push(`Unclosed code block starting at line ${codeBlockStart}`);
  }

  const contentLower = content.toLowerCase();
  if (!contentLower.includes('## common mistakes')) {
    warnings.push("Missing '## Common Mistakes' section");
  }
  if (!contentLower.includes('## delegation')) {
    warnings.push("Missing '## Delegation' section");
  }

  return { errors, warnings };
}

function validateReferenceMd(
  filePath: string,
  content: string,
): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const lines = content.split('\n');
  const lineCount = lines.length;
  const fileName = basename(filePath);

  if (lineCount > REF_MAX_LINES) {
    errors.push(`${fileName}: ${lineCount} lines (max ${REF_MAX_LINES})`);
  } else if (lineCount > REF_WARN_LINES) {
    warnings.push(
      `${fileName}: ${lineCount} lines (consider splitting at ~${REF_WARN_LINES})`,
    );
  }

  if (!content.startsWith('---')) {
    warnings.push(
      `${fileName}: Missing YAML frontmatter (title, description, tags required)`,
    );
    return { errors, warnings };
  }

  const { data: frontmatter, error: fmError } = parseFrontmatter(content);

  if (fmError) {
    warnings.push(`${fileName}: ${fmError}`);
    return { errors, warnings };
  }

  if (!frontmatter?.title || !String(frontmatter.title).trim()) {
    warnings.push(`${fileName}: Missing 'title' in frontmatter`);
  }

  if (!frontmatter?.description || !String(frontmatter.description).trim()) {
    warnings.push(`${fileName}: Missing 'description' in frontmatter`);
  }

  const tags = frontmatter?.tags;
  if (!tags || (Array.isArray(tags) && tags.length === 0) || tags === '') {
    warnings.push(`${fileName}: Missing 'tags' in frontmatter`);
  }

  return { errors, warnings };
}

function crossValidateReferences(
  skillDir: string,
  skillContent: string,
): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  const linkPattern = /\(references\/([^)]+\.md)\)/g;
  const linkedFiles = new Set<string>();
  let match;
  while ((match = linkPattern.exec(skillContent)) !== null) {
    linkedFiles.add(match[1]);
  }

  const refsDir = join(skillDir, 'references');
  const actualFiles = new Set<string>();

  if (existsSync(refsDir)) {
    for (const file of readdirSync(refsDir)) {
      if (file.endsWith('.md') && !file.startsWith('_')) {
        actualFiles.add(file);
      }
    }
  }

  for (const linked of linkedFiles) {
    if (!actualFiles.has(linked)) {
      errors.push(
        `Broken reference link: references/${linked} (file not found)`,
      );
    }
  }

  for (const actual of actualFiles) {
    if (!linkedFiles.has(actual)) {
      errors.push(
        `Orphan reference file: references/${actual} (not linked in SKILL.md)`,
      );
    }
  }

  return { errors, warnings };
}

function validateSkill(skillDir: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const skillFile = join(skillDir, 'SKILL.md');

  const dirName = basename(skillDir);
  if (dirName.length < MIN_NAME_LENGTH) {
    errors.push(
      `Directory name '${dirName}' is too short (${dirName.length} chars, min ${MIN_NAME_LENGTH}). Use a descriptive name, not an abbreviation`,
    );
  }

  if (!existsSync(skillFile)) {
    return { errors: ['SKILL.md not found'], warnings };
  }

  const skillContent = readFileSync(skillFile, 'utf-8');
  const skillResult = validateSkillMd(skillFile, skillContent);
  errors.push(...skillResult.errors);
  warnings.push(...skillResult.warnings);

  const crossResult = crossValidateReferences(skillDir, skillContent);
  errors.push(...crossResult.errors);
  warnings.push(...crossResult.warnings);

  const refsDir = join(skillDir, 'references');
  if (existsSync(refsDir)) {
    for (const file of readdirSync(refsDir)) {
      if (!file.endsWith('.md') || file.startsWith('_')) continue;
      const refPath = join(refsDir, file);
      const refContent = readFileSync(refPath, 'utf-8');
      const refResult = validateReferenceMd(refPath, refContent);
      errors.push(...refResult.errors);
      warnings.push(...refResult.warnings);
    }
  }

  for (const file of readdirSync(skillDir)) {
    if (SKILLS_CLI_EXCLUDED.has(file) || file.startsWith('_')) {
      warnings.push(
        `'${file}' is excluded by the skills CLI during installation`,
      );
    }
  }

  const scriptsDir = join(skillDir, 'scripts');
  if (existsSync(scriptsDir)) {
    for (const file of readdirSync(scriptsDir)) {
      if (file.endsWith('.py') || file.endsWith('.sh')) {
        const scriptPath = join(scriptsDir, file);
        const mode = statSync(scriptPath).mode;
        if (!(mode & 0o111)) {
          warnings.push(
            `Script not executable: scripts/${file} (run chmod +x)`,
          );
        }
      }
    }
  }

  return { errors, warnings };
}

function resolveSkillDirs(args: string[]): string[] {
  if (args.length === 0) {
    const dir = resolve(SKILLS_DIR);
    if (!existsSync(dir)) return [];
    return readdirSync(dir)
      .map((d) => join(dir, d))
      .filter((d) => {
        try {
          return statSync(d).isDirectory() && existsSync(join(d, 'SKILL.md'));
        } catch {
          return false;
        }
      });
  }

  const skillDirs = new Set<string>();

  for (const arg of args) {
    const resolved = resolve(arg);

    if (!existsSync(resolved)) continue;

    const stat = statSync(resolved);

    if (stat.isFile() && resolved.endsWith('.md')) {
      let dir = dirname(resolved);
      if (basename(dir) === 'references') {
        dir = dirname(dir);
      }
      if (existsSync(join(dir, 'SKILL.md'))) {
        skillDirs.add(dir);
      }
    } else if (stat.isDirectory()) {
      if (existsSync(join(resolved, 'SKILL.md'))) {
        skillDirs.add(resolved);
      } else {
        for (const sub of readdirSync(resolved)) {
          const subDir = join(resolved, sub);
          try {
            if (
              statSync(subDir).isDirectory() &&
              existsSync(join(subDir, 'SKILL.md'))
            ) {
              skillDirs.add(subDir);
            }
          } catch {
            // skip non-directories
          }
        }
      }
    }
  }

  return [...skillDirs].sort();
}

function main(): void {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    console.log('Usage: node scripts/validate-skills.ts [paths...]');
    console.log();
    console.log('  No args         Validate all skills in skills/');
    console.log('  skills/name     Validate a single skill');
    console.log('  file1 file2     Validate skills containing these files');
    console.log();
    console.log('Examples:');
    console.log('  pnpm validate:skills');
    console.log('  pnpm validate:skills skills/tanstack-query');
    console.log('  pnpm validate:skills skills/tanstack-query/SKILL.md');
    process.exit(0);
  }

  const skillDirs = resolveSkillDirs(args);

  if (skillDirs.length === 0) {
    console.log('No skills found to validate');
    process.exit(1);
  }

  let totalErrors = 0;
  let totalWarnings = 0;
  const failedSkills: string[] = [];
  const descriptions: Record<string, string> = {};

  const isSingle = skillDirs.length === 1;

  if (!isSingle) {
    console.log(`Validating ${skillDirs.length} skill(s)...\n`);
  }

  for (const skillDir of skillDirs) {
    const skillName = basename(skillDir);
    const { errors, warnings } = validateSkill(skillDir);
    totalErrors += errors.length;
    totalWarnings += warnings.length;

    if (errors.length > 0) {
      failedSkills.push(skillName);
    }

    if (isSingle) {
      if (errors.length > 0) {
        console.log(`x ${skillName}: FAILED\n`);
        console.log('Errors:');
        for (const e of errors) console.log(`  x ${e}`);
        console.log();
      }
      if (warnings.length > 0) {
        console.log('Warnings:');
        for (const w of warnings) console.log(`  ! ${w}`);
        console.log();
      }
      if (errors.length === 0 && warnings.length === 0) {
        console.log(`  ${skillName}: passed`);
      } else if (errors.length === 0) {
        console.log(`  ${skillName}: valid (with warnings)`);
      }
    } else {
      if (errors.length > 0) {
        console.log(`x ${skillName}: FAILED`);
        for (const e of errors) console.log(`   x ${e}`);
      } else if (warnings.length > 0) {
        console.log(`  ${skillName}: valid (${warnings.length} warning(s))`);
      } else {
        console.log(`  ${skillName}: passed`);
      }
    }

    const skillFile = join(skillDir, 'SKILL.md');
    if (existsSync(skillFile)) {
      const content = readFileSync(skillFile, 'utf-8');
      const { data } = parseFrontmatter(content);
      if (data?.description) {
        descriptions[skillName] = String(data.description);
      }
    }
  }

  if (!isSingle && Object.keys(descriptions).length > 1) {
    const conflictWarnings = checkDescriptionConflicts(descriptions);
    totalWarnings += conflictWarnings.length;

    if (conflictWarnings.length > 0) {
      console.log('\n! Description conflicts:');
      for (const w of conflictWarnings) console.log(`   ${w}`);
    }
  }

  if (!isSingle) {
    console.log();
    if (failedSkills.length > 0) {
      console.log(
        `x ${failedSkills.length} skill(s) failed: ${failedSkills.join(', ')}`,
      );
    } else {
      console.log(`  All ${skillDirs.length} skill(s) passed`);
    }
    if (totalWarnings > 0) {
      console.log(`  ${totalWarnings} total warning(s)`);
    }
  }

  process.exit(failedSkills.length > 0 ? 1 : 0);
}

main();
