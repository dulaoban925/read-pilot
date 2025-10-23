# Frontend Setup Guide

## Prerequisites

- Node.js 22 LTS
- pnpm 9.14+

## Installation Steps

### 1. Install Dependencies

```bash
cd frontend

# Install dependencies
pnpm install
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local and update:
# - NEXT_PUBLIC_API_URL (backend API URL)
```

### 3. Start Development Server

```bash
pnpm dev
```

Visit:
- Frontend: http://localhost:3000

## Available Scripts

```bash
# Development
pnpm dev              # Start dev server with hot reload
pnpm build            # Build for production
pnpm start            # Start production server
pnpm lint             # Run ESLint
pnpm type-check       # Run TypeScript compiler check

# Testing (to be added in Phase 2)
pnpm test             # Run unit tests
pnpm test:e2e         # Run E2E tests with Playwright
```

## Project Structure

```
frontend/
├── app/                    # Next.js 15 App Router
│   ├── (auth)/            # Authentication pages
│   ├── reader/[id]/       # Document reader page
│   ├── profile/           # User profile page
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
│
├── components/            # React components
│   ├── reader/           # Document viewer components
│   │   ├── DocumentViewer/
│   │   ├── Annotation/
│   │   └── TextSelection.tsx
│   ├── chat/             # Chat interface components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageItem.tsx
│   │   ├── SummaryCard.tsx
│   │   └── GuidingQuestions.tsx
│   ├── notes/            # Notes management
│   │   ├── NotesList.tsx
│   │   └── NoteItem.tsx
│   ├── profile/          # Profile components
│   │   └── ReadingTrendChart.tsx
│   └── ui/               # Reusable UI components (shadcn/ui style)
│
├── lib/                   # Utility libraries
│   ├── api.ts            # API client (Axios instance with interceptors)
│   ├── auth.ts           # Authentication utilities
│   ├── hooks/            # Custom React hooks
│   │   └── useDocuments.ts
│   └── utils.ts          # Utility functions (cn, formatters)
│
├── stores/               # Zustand state management
│   ├── authStore.ts      # Authentication state
│   └── documentStore.ts  # Document state
│
├── public/               # Static assets
├── styles/               # Global styles
└── types/                # TypeScript type definitions
```

## Development Workflow

### Adding a New Component

```bash
# Create component file
touch components/my-component.tsx

# Use TypeScript and follow conventions
```

Example component:
```typescript
'use client';

import { useState } from 'react';

interface MyComponentProps {
  title: string;
  onAction?: () => void;
}

export function MyComponent({ title, onAction }: MyComponentProps) {
  const [state, setState] = useState<string>('');

  return (
    <div className="my-component">
      <h2>{title}</h2>
      {/* Component content */}
    </div>
  );
}
```

### Adding a New Page

```bash
# Create page in app directory
mkdir -p app/my-page
touch app/my-page/page.tsx
```

### Working with API

```typescript
// Use TanStack Query hooks from lib/hooks
import { useDocuments } from '@/lib/hooks/useDocuments';

// In component
const { data, isLoading, error } = useDocuments(page, pageSize);
```

### State Management

```typescript
// Use Zustand stores
import { useDocumentStore } from '@/stores/documentStore';
import { useAuthStore } from '@/stores/authStore';

function MyComponent() {
  const { currentDocument, setCurrentDocument } = useDocumentStore();
  const { user, isAuthenticated } = useAuthStore();

  // Use state...
}
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS 4.0 for styling:

```typescript
<div className="flex items-center justify-between p-4 rounded-lg bg-gray-100">
  <span className="text-lg font-bold">Title</span>
  <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Action
  </button>
</div>
```

### shadcn/ui Components

Use shadcn/ui style components with Radix UI primitives:

```typescript
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

<Button variant="default" size="default" onClick={handleClick}>
  Click Me
</Button>

<Input label="Email" type="email" placeholder="your@email.com" />
```

## Code Quality

### Linting

```bash
# Run ESLint
pnpm lint

# Auto-fix issues
pnpm lint:fix
```

### Type Checking

```bash
# Check types
pnpm type-check

# Build (includes type checking)
pnpm build
```

### Formatting

The project uses ESLint and Prettier for formatting:

```bash
# Format all files
pnpm format

# Check formatting
pnpm format:check
```

## Building for Production

```bash
# Build the application
pnpm build

# Test production build locally
pnpm start
```

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:

```bash
# Use a different port
PORT=3001 pnpm dev
```

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules .next
pnpm install
```

### API Connection Issues

Check that:
1. Backend server is running on http://localhost:8000
2. NEXT_PUBLIC_API_URL in .env.local is correct
3. CORS is properly configured in backend

### TypeScript Errors

```bash
# Clean and rebuild
rm -rf .next
pnpm type-check
pnpm build
```

## Next Steps

Once the frontend is set up:
1. Implement document upload component (Phase 2)
2. Create PDF/EPUB viewer (Phase 2)
3. Build chat interface (Phase 3)
4. Add annotation system (Phase 4)

See [tasks.md](../.specify/specs/001-core-reading-experience/tasks.md) for detailed implementation tasks.
