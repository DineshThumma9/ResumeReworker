import { z } from "zod";

// ─── Mirrors Template response in backend/router.py ──────────────────────────

export const TemplateSchema = z.object({
  id: z.number(),
  name: z.string(),
  tex_source: z.string(),
  is_builtin: z.boolean(),
  preview_url: z.string().nullable().optional(),
  created_at: z.string().nullable().optional(),
});

export type Template = z.infer<typeof TemplateSchema>;

export const PaginatedTemplateSchema = z.object({
  templates: z.array(TemplateSchema),
  skip: z.number(),
  limit: z.number(),
  total_count: z.number(),
});

export type PaginatedTemplate = z.infer<typeof PaginatedTemplateSchema>;
