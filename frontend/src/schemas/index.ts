/**
 * src/schemas/index.ts
 *
 * Single source of truth for all API shapes on the frontend.
 * Every schema here mirrors a Pydantic model in backend/models.py.
 *
 * The pattern:
 *   1. Pydantic defines the shape on the backend.
 *   2. Zod mirrors it here (same fields, same constraints).
 *   3. Every API response goes through safeParse — no silent shape mismatches.
 *   4. TypeScript types are derived from Zod schemas via z.infer<>.
 *      You never manually write a `type Resume = { ... }` again.
 */


export * from "./resumes";
export * from "./templates";
export * from "./share";
