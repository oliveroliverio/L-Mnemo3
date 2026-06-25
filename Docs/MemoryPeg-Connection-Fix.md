# Memory Peg API Connection & Rendering Fixes

## Problem Description
There were two major issues preventing the frontend from correctly connecting to and displaying data from the Memory Peg API:
1. **CORS (Cross-Origin Resource Sharing) Block**: The frontend ran on `localhost:3000` while the Memory Peg API was hosted on `http://100.88.124.124:3000`. The browser blocked direct fetch requests to the remote IP for security reasons, resulting in the Memory Peg status showing as "Offline".
2. **React Object Rendering Error**: Once the API connected, the frontend crashed with `Objects are not valid as a React child (found: object with keys {weekday, theme, props, note})`. The original interface assumption expected strings for properties like `dayTheme`, but the actual API returned deeply nested objects.

## Step-by-Step Solution

### 1. Bypassing CORS with Next.js Rewrites
Instead of fetching data directly from the browser to the remote IP, we configured Next.js to proxy the requests through the Next.js development server.

**Changes Made:**
Updated `next.config.ts` to include rewrites that map local `/api/...` endpoints to the remote API URLs injected via `.env`.

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the user's remote IP for Hot Module Reloading
  allowedDevOrigins: ['10.53.4.247'],
  async rewrites() {
    return [
      {
        source: '/api/memory-peg/:path*',
        destination: `${process.env.NEXT_PUBLIC_MEMORY_PEG_API}/:path*`,
      },
      {
        source: '/api/sqlite/:path*',
        destination: `${process.env.NEXT_PUBLIC_SQLITE_API}/:path*`,
      }
    ];
  },
};

export default nextConfig;
```

Updated API Services (`FRONTEND/services/MemoryPegService.ts` & `FRONTEND/services/SubmissionService.ts`) to use the new rewrite endpoints instead of the `.env` URLs directly:
```typescript
const API_URL = '/api/memory-peg';
```

### 2. Fixing the React Child Object Error
We used `curl` to inspect the actual JSON structure returned by the Memory Peg API and updated our TypeScript interfaces and React components to match.

**Terminal Command Used for Investigation:**
```bash
curl -s http://100.88.124.124:3000/getCharacters | jq .
```

**Changes Made:**
Updated `FRONTEND/types/index.ts` to reflect the nested structure:
```typescript
export interface MemoryPegMetadata {
  weekCreature: { creature: string; /* ... */ };
  dayTheme: { theme: string; /* ... */ };
  timeCharacter: { peg: string; character: string; /* ... */ };
  // ...
}
```

Updated `FRONTEND/components/layout/LeftSidebar.tsx` to safely access nested string properties:
```tsx
<p className="font-medium text-sm">{memoryPeg?.dayTheme?.theme || '...'}</p>
<p className="font-medium text-sm">{memoryPeg?.weekCreature?.creature || '...'}</p>
<p className="font-medium text-sm">{memoryPeg?.timeCharacter?.character || '...'}</p>
<p className="font-medium text-sm">{memoryPeg?.timeCharacter?.peg || '...'}</p>
```

We applied identical nested property access in `FRONTEND/hooks/useSubmission.ts`.

### 3. Restarting the Server
To ensure the `next.config.ts` rewrites and `.env` changes were picked up, the old production server was killed and a dev server was started.

**Terminal Command Executed:**
```bash
lsof -ti :3000 | xargs kill -9 && npm run dev
```

## Result
The Next.js rewrites successfully routed requests server-side to the Memory Peg API, bypassing browser CORS restrictions, and the React components successfully rendered the nested string values without crashing.
