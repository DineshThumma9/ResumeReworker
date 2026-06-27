import { z } from "zod";

// ─── Mirrors ShareLinkOut in backend/models.py ───────────────────────────────

export const ShareLinkSchema = z.object({
  token: z.string().uuid(),
  resume_id: z.number(),
  is_active: z.boolean(),
  view_count: z.number(),
});

export type ShareLink = z.infer<typeof ShareLinkSchema>;
