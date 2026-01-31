---
title: Focus Management
description: Custom focus indicators with focus-visible, dialog focus traps with Escape and restore, and SPA route change focus management
tags: [focus, focus-visible, focus-trap, dialog, spa-navigation]
---

# Focus Management

## Focus Indicators

```css
/* WRONG: removes focus outline */
button:focus {
  outline: none;
}

/* CORRECT: custom accessible outline */
button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

Never remove focus outlines without replacement. Use `:focus-visible` to show outlines only for keyboard users. Ensure 3:1 contrast ratio for focus indicators.

## Focus Not Obscured (WCAG 2.4.11)

When an element receives keyboard focus, it must not be entirely hidden by sticky headers, footers, cookie banners, or other author-created overlays. At least a portion of the focused element must remain visible.

```css
/* Account for sticky header when focusing elements */
:target {
  scroll-margin-top: 80px;
}

/* Ensure focused elements are not hidden under sticky elements */
*:focus-visible {
  scroll-margin-top: 80px;
  scroll-margin-bottom: 40px;
}
```

Common violations: sticky navigation bars, fixed cookie consent banners, chat widgets overlapping focused content.

## Dialog with Focus Trap

```tsx
function Dialog({ isOpen, onClose, title, children }: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const previousFocus = document.activeElement as HTMLElement;

    const firstFocusable = dialogRef.current?.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    ) as HTMLElement;
    firstFocusable?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        const focusableElements = dialogRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        );
        if (!focusableElements?.length) return;

        const first = focusableElements[0] as HTMLElement;
        const last = focusableElements[
          focusableElements.length - 1
        ] as HTMLElement;

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previousFocus?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      <div className="dialog-backdrop" onClick={onClose} aria-hidden="true" />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <h2 id="dialog-title">{title}</h2>
        {children}
        <button onClick={onClose} aria-label="Close dialog">
          x
        </button>
      </div>
    </>
  );
}
```

Key requirements: trap focus inside, restore focus on close, close on Escape.

## SPA Focus Management

SPAs do not reset focus on navigation. Handle it explicitly:

```tsx
function App() {
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);

  useEffect(() => {
    mainRef.current?.focus();
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.textContent = `Navigated to ${document.title}`;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
  }, [location.pathname]);

  return (
    <main ref={mainRef} tabIndex={-1} id="main-content">
      ...
    </main>
  );
}
```
