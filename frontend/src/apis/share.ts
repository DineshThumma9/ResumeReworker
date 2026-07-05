import { fetchJSON } from "./api";

export interface SharedResume {
  tex_source: string;
  pdf_url: string;
  view_count: number;
}

export const shareApi = {
  share: async (
    latex_code: string,
    mask: Record<string, boolean>,
  ): Promise<string> => {
    const raw = await fetchJSON(`/share`, {
      method: "POST",
      body: JSON.stringify({ tex_source: latex_code, mask }),
    });
    return raw.token;
  },
  get: async (token: string): Promise<SharedResume> => {
    const raw = await fetchJSON(`/share/${token}`);
    return raw as SharedResume;
  },
};
