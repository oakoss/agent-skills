---
title: Modern Idioms
description: Modern JavaScript idioms enforced by eslint-plugin-unicorn — arrays, strings, errors, DOM, modules
tags:
  [
    unicorn,
    for-of,
    reduce,
    forEach,
    modern-js,
    eslint,
    array,
    string,
    error,
    dom,
    node-protocol,
  ]
---

# Modern Idioms

Modern JavaScript/TypeScript idioms commonly enforced by `eslint-plugin-unicorn`. Prefer these patterns over legacy alternatives.

## Arrays

```ts
// Use for-of instead of reduce
array.reduce((acc, item) => acc + item, 0); // Avoid
let sum = 0;
for (const item of array) sum += item; // Preferred

// Use for-of instead of forEach
array.forEach((item) => console.log(item)); // Avoid
for (const item of array) console.log(item); // Preferred

// Use for-of instead of traditional for loops
for (let i = 0; i < array.length; i++) {} // Avoid
for (const item of array) {
} // Preferred
for (const [index, item] of array.entries()) {
} // When index needed

// Use Array.from instead of new Array
new Array(10); // Avoid
Array.from({ length: 10 }); // Preferred
```

### Modern Array Methods

```ts
array.at(-1); // not array[array.length - 1]
array.includes(x); // not array.indexOf(x) !== -1
array.find((x) => x.id === id); // not array.filter(...)[0]
array.some((x) => x.valid); // not array.filter(...).length > 0
array.flat(); // not [].concat(...array)
array.flatMap((x) => x.items); // not array.map(...).flat()
array.toSorted(); // not [...array].sort()
array.toReversed(); // not [...array].reverse()
```

## Strings

```ts
str.replaceAll('a', 'b'); // not str.replace(/a/g, 'b')
str.slice(1, 3); // not str.substr() or str.substring()
str.startsWith('x'); // not str.indexOf('x') === 0
str.endsWith('x'); // not str.slice(-1) === 'x'
str.trimStart(); // not str.trimLeft()
str.trimEnd(); // not str.trimRight()
str.codePointAt(0); // not str.charCodeAt(0)
str.at(-1); // not str.charAt(str.length - 1)
```

## Errors

```ts
// Always use "throw new Error" with a message
throw new Error('Something went wrong'); // Correct
throw Error('msg'); // Missing "new"
throw 'error'; // Not an Error object
throw new Error(); // Missing message

// Catch variable must be named "error"
catch (error) {} // Correct
catch (e) {} // Avoid
catch (err) {} // Avoid

// Use TypeError for type validation
if (typeof x !== 'string') throw new TypeError('Expected string');
```

## ES Modules

```ts
// Use ES module syntax
import x from 'module'; // Correct
export { x }; // Correct
const x = require('module'); // Avoid CommonJS
module.exports = x; // Avoid CommonJS

// Use node: protocol for Node.js builtins
import fs from 'node:fs'; // Correct
import path from 'node:path'; // Correct
import fs from 'fs'; // Missing protocol

// Use globalThis instead of environment-specific globals
globalThis.setTimeout; // Correct
window.setTimeout; // Browser-specific
global.setTimeout; // Node-specific
```

## Conditionals

```ts
// No nested ternaries
const x = a ? (b ? 1 : 2) : 3; // Avoid — use if-else or extract to functions

// Prefer nullish coalescing over ternary
const x = a ?? b; // not: a !== null ? a : b
const x = a || b; // not: a ? a : b

// No negated conditions with else
if (!condition) {
  /* ... */
} else {
  /* ... */
} // Avoid
if (condition) {
  /* ... */
} else {
  /* ... */
} // Preferred — flip the condition
```

## Functions and Classes

```ts
// No static-only classes — use plain objects or functions
class Utils {
  static helper() {}
} // Avoid
function helper() {} // Preferred

// Use class fields for initialization
class Foo {
  bar = 'value'; // Preferred over constructor assignment
}
```

## DOM

```ts
// Modern DOM APIs
element.append(child); // not appendChild
element.remove(); // not parent.removeChild(element)
element.querySelector('.x'); // not getElementById or getElementsByClassName
element.closest('.x'); // not manual parent traversal
element.dataset.value; // not getAttribute('data-value')
element.addEventListener('click', fn); // not onclick = fn
element.classList.toggle('active'); // not manual add/remove

// Use KeyboardEvent.key
event.key === 'Enter'; // not event.keyCode === 13
```

## Numbers

```ts
Number.isNaN(x); // not isNaN(x)
Number.isFinite(x); // not isFinite(x)
Number.parseInt(x); // not parseInt(x)

Math.trunc(x); // not x | 0 or ~~x

// Use numeric separators for readability
const billion = 1_000_000_000;
```

## Miscellaneous

```ts
// Explicit length check
if (array.length > 0) {
} // Preferred
if (array.length) {
} // Avoid — implicit boolean coercion

// Use Set for repeated has() checks
const set = new Set(array);
set.has(x);

// Re-export directly
export { x } from './module'; // not import then export

// Optional catch binding when error unused
try {
  /* ... */
} catch {} // Omit variable if unused

// Avoid process.exit() — throw errors instead
// Avoid document.cookie — use a cookie library
```

## Quick Reference

| Legacy Pattern            | Modern Replacement            |
| ------------------------- | ----------------------------- |
| `array.reduce()`          | `for-of` loop                 |
| `array.forEach()`         | `for-of` loop                 |
| `for (let i = 0; ...)`    | `for-of` or `array.entries()` |
| `array[array.length - 1]` | `array.at(-1)`                |
| `[...array].sort()`       | `array.toSorted()`            |
| `str.replace(/x/g, 'y')`  | `str.replaceAll('x', 'y')`    |
| `import fs from 'fs'`     | `import fs from 'node:fs'`    |
| `catch (e)`               | `catch (error)`               |
| `throw 'error'`           | `throw new Error('message')`  |
| `isNaN(x)`                | `Number.isNaN(x)`             |
| `element.appendChild(x)`  | `element.append(x)`           |
| `event.keyCode === 13`    | `event.key === 'Enter'`       |
