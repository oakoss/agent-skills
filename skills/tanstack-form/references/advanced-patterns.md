---
title: Advanced Patterns
description: Multi-step forms, file uploads, conditional fields, and accessibility
tags: [multi-step, wizard, file-upload, conditional, accessibility]
---

# Advanced Patterns

## Multi-Step Wizard Form

Step-by-step validation with progress tracking:

```tsx
import { useState } from 'react';
import { useForm } from '@tanstack/react-form';
import { z } from 'zod';

type WizardStep = 'account' | 'profile' | 'preferences';

const wizardSchema = {
  account: z.object({
    email: z.string().email(),
    password: z.string().min(8),
  }),
  profile: z.object({
    name: z.string().min(1),
  }),
  preferences: z.object({
    notifications: z.boolean(),
  }),
};

function WizardForm() {
  const [step, setStep] = useState<WizardStep>('account');

  const form = useForm({
    defaultValues: {
      email: '',
      password: '',
      name: '',
      notifications: true,
    },
    onSubmit: async ({ value }) => {
      await api.createAccount(value);
    },
  });

  const validateStep = async (): Promise<boolean> => {
    const schema = wizardSchema[step];
    const stepValues = getStepValues(form.state.values, step);
    const result = schema.safeParse(stepValues);

    if (!result.success) {
      for (const issue of result.error.issues) {
        const fieldName = issue.path.join('.');
        form.setFieldMeta(fieldName, (prev) => ({
          ...prev,
          errors: [issue.message],
        }));
      }
      return false;
    }

    return true;
  };

  const nextStep = async () => {
    if (await validateStep()) {
      const steps: WizardStep[] = ['account', 'profile', 'preferences'];
      const currentIndex = steps.indexOf(step);

      if (currentIndex < steps.length - 1) {
        setStep(steps[currentIndex + 1]);
      } else {
        form.handleSubmit();
      }
    }
  };

  return (
    <form onSubmit={(e) => e.preventDefault()}>
      {step === 'account' && <AccountStep form={form} />}
      {step === 'profile' && <ProfileStep form={form} />}
      {step === 'preferences' && <PreferencesStep form={form} />}

      <div className="flex justify-between">
        {step !== 'account' && (
          <button type="button" onClick={() => setStep('account')}>
            Back
          </button>
        )}
        <button type="button" onClick={nextStep}>
          {step === 'preferences' ? 'Complete' : 'Next'}
        </button>
      </div>
    </form>
  );
}

function getStepValues(values: any, step: WizardStep) {
  const fieldMap: Record<WizardStep, string[]> = {
    account: ['email', 'password'],
    profile: ['name'],
    preferences: ['notifications'],
  };
  return fieldMap[step].reduce(
    (acc, key) => ({ ...acc, [key]: values[key] }),
    {},
  );
}
```

## File Upload Field

Single file upload with preview:

```tsx
import { useState } from 'react';
import { useFieldContext } from '@/hooks/form-context';

export function FileUploadField() {
  const field = useFieldContext<string>();
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      field.handleChange(data.url);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <label htmlFor={field.name}>Image</label>
      {field.state.value && (
        <img
          src={field.state.value}
          alt="Preview"
          className="w-32 h-32 object-cover"
        />
      )}
      <input
        id={field.name}
        type="file"
        accept="image/*"
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
    </div>
  );
}
```

## Multiple File Upload

Upload multiple files with progress:

```tsx
import { useState } from 'react';
import { useFieldContext } from '@/hooks/form-context';

export function MultiFileUpload() {
  const field = useFieldContext<string[]>();
  const [uploads, setUploads] = useState<Map<string, number>>(new Map());

  const uploadFile = async (
    file: File,
    onProgress: (progress: number) => void,
  ): Promise<string> => {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          onProgress((e.loaded / e.total) * 100);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          resolve(JSON.parse(xhr.responseText).url);
        } else {
          reject(new Error('Upload failed'));
        }
      });

      xhr.open('POST', '/api/upload');
      xhr.send(formData);
    });
  };

  const handleFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);

    for (const file of files) {
      const id = crypto.randomUUID();
      setUploads((prev) => new Map(prev).set(id, 0));

      try {
        const url = await uploadFile(file, (progress) => {
          setUploads((prev) => new Map(prev).set(id, progress));
        });
        field.pushValue(url);
      } finally {
        setUploads((prev) => {
          const next = new Map(prev);
          next.delete(id);
          return next;
        });
      }
    }
  };

  return (
    <div>
      <input type="file" multiple onChange={handleFiles} />

      {Array.from(uploads).map(([id, progress]) => (
        <div key={id} className="h-2 bg-gray-200 rounded">
          <div
            className="h-full bg-blue-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      ))}

      <div className="grid grid-cols-4 gap-2">
        {field.state.value.map((url, index) => (
          <div key={index}>
            <img src={url} className="w-20 h-20 object-cover" alt="" />
            <button type="button" onClick={() => field.removeValue(index)}>
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Conditional Fields

Show/hide fields based on other field values:

```tsx
function ConditionalForm() {
  const form = useForm({
    defaultValues: {
      accountType: 'personal',
      companyName: '',
    },
  });

  return (
    <form>
      <form.Field
        name="accountType"
        children={(field) => (
          <select
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
          >
            <option value="personal">Personal</option>
            <option value="business">Business</option>
          </select>
        )}
      />

      <form.Subscribe selector={(state) => state.values.accountType}>
        {(accountType) =>
          accountType === 'business' ? (
            <form.Field
              name="companyName"
              validators={{
                onChange: ({ value }) =>
                  !value ? 'Company name is required' : undefined,
              }}
              children={(field) => (
                <div>
                  <input
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors[0] && (
                    <span>{field.state.meta.errors[0]}</span>
                  )}
                </div>
              )}
            />
          ) : null
        }
      </form.Subscribe>
    </form>
  );
}
```

## Dependent Select Fields

Country/province cascading selects:

```tsx
const COUNTRIES = [
  { code: 'us', name: 'United States' },
  { code: 'ca', name: 'Canada' },
];

const PROVINCES: Record<string, Array<{ code: string; name: string }>> = {
  us: [
    { code: 'ca', name: 'California' },
    { code: 'ny', name: 'New York' },
  ],
  ca: [
    { code: 'on', name: 'Ontario' },
    { code: 'qc', name: 'Quebec' },
  ],
};

function DependentSelectForm() {
  const form = useForm({
    defaultValues: {
      country: '',
      province: '',
    },
  });

  return (
    <form>
      <form.Field
        name="country"
        listeners={{
          onChange: () => form.setFieldValue('province', ''),
        }}
        children={(field) => (
          <select
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
          >
            <option value="">Select country</option>
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        )}
      />

      <form.Subscribe selector={(state) => state.values.country}>
        {(country) =>
          country ? (
            <form.Field
              name="province"
              children={(field) => (
                <select
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                >
                  <option value="">Select province</option>
                  {PROVINCES[country]?.map((p) => (
                    <option key={p.code} value={p.code}>
                      {p.name}
                    </option>
                  ))}
                </select>
              )}
            />
          ) : null
        }
      </form.Subscribe>
    </form>
  );
}
```

## Accessibility Requirements

| Requirement    | Implementation                                 |
| -------------- | ---------------------------------------------- |
| Label          | `<label htmlFor={field.name}>`                 |
| Error message  | `aria-invalid`, `aria-describedby`             |
| Help text      | `aria-describedby` with description ID         |
| Required field | `aria-required="true"` or `required` attribute |
| Fieldset       | Group related fields with `<fieldset>`         |
| Live region    | `aria-live="polite"` for async feedback        |

### Accessible Field Example

```tsx
<form.Field
  name="email"
  children={(field) => {
    const isInvalid =
      field.state.meta.isTouched && field.state.meta.errors.length > 0;
    const errorId = `${field.name}-error`;
    const descId = `${field.name}-desc`;

    return (
      <div>
        <label htmlFor={field.name}>Email</label>
        <p id={descId}>We'll never share your email.</p>
        <input
          id={field.name}
          value={field.state.value}
          onChange={(e) => field.handleChange(e.target.value)}
          aria-invalid={isInvalid}
          aria-describedby={isInvalid ? `${descId} ${errorId}` : descId}
          required
        />
        {isInvalid && (
          <span id={errorId} role="alert">
            {field.state.meta.errors.join(', ')}
          </span>
        )}
      </div>
    );
  }}
/>
```

## Form Persistence

Save form state to localStorage:

```tsx
import { useEffect } from 'react';

function PersistedForm() {
  const form = useForm({
    defaultValues: { email: '', name: '' },
    onSubmit: async ({ value }) => {
      await api.submit(value);
      localStorage.removeItem('form-draft');
    },
  });

  useEffect(() => {
    const saved = localStorage.getItem('form-draft');
    if (saved) {
      const data = JSON.parse(saved);
      Object.entries(data).forEach(([key, value]) => {
        form.setFieldValue(key, value);
      });
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      localStorage.setItem('form-draft', JSON.stringify(form.state.values));
    }, 1000);

    return () => clearInterval(interval);
  }, [form.state.values]);

  return <form>{/* fields */}</form>;
}
```

## Advanced Patterns Notes

- Use `form.Subscribe` to conditionally render fields without re-rendering the entire form
- Use `listeners` for side effects (clearing dependent fields), `validators` for validation logic
- Store file URLs in form state, not File objects
- Use semantic HTML (`fieldset`, `legend`) for better accessibility
- Add `aria-live="polite"` to error containers for screen reader announcements
- Persist form state for long forms to prevent data loss
