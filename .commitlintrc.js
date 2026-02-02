import { defineConfig } from 'cz-git';

export default defineConfig({
  extends: ['@commitlint/config-conventional'],
  prompt: {
    alias: {
      fd: 'docs: fix typos',
      b: 'chore(deps): bump dependencies',
    },
    allowCustomScopes: false,
    allowEmptyScopes: true,
    scopes: ['skills', 'validator', 'docs', 'config', 'deps', 'ci'],
  },
  rules: {
    // Relax line length limits for detailed commits
    'header-max-length': [2, 'always', 200],
    'body-max-line-length': [0, 'always'],
  },
});
