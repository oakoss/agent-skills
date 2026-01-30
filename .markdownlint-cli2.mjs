// markdownlint-cli2 configuration
// See: https://github.com/DavidAnson/markdownlint-cli2#configuration

export default {
  // markdownlint configuration
  config: {
    default: true,
    // MD001: Heading levels should only increment by one level at a time
    MD001: false,
    // MD007: Unordered list indentation
    MD007: {
      indent: 2,
    },
    // MD012: Multiple consecutive blank lines
    MD012: false,
    // MD013: Line length
    MD013: false,
    // MD024: Multiple headings with the same content
    MD024: false,
    // MD025: Multiple top-level headings in the same document
    MD025: false,
    // MD026: Trailing punctuation in heading
    MD026: false,
    // MD029: Ordered list item prefix
    MD029: false,
    // MD033: Inline HTML
    MD033: false,
    // MD036: Emphasis used instead of a heading
    MD036: false,
    // MD037: Spaces inside emphasis markers
    MD037: false,
    // MD041: First line in a file should be a top-level heading
    MD041: false,
    // MD046: Code block style
    MD046: {
      style: 'fenced',
    },
    // MD060: Table column alignment
    MD060: false,
  },
  // Use .gitignore patterns automatically
  gitignore: true,
};
