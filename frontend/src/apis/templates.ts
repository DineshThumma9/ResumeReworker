import { fetchJSON, parse, TemplateSchema, type Template, PaginatedTemplateSchema } from "./api";

export const templateApi = {
  list: async (): Promise<Template[]> => {
    const raw = await fetchJSON("/templates");
    const paginated = parse(PaginatedTemplateSchema, raw);
    return paginated.templates;
  },
  create: async (name: string, latexCode: string): Promise<Template> => {
    const raw = await fetchJSON("/templates", {
      method: "POST",
      body: JSON.stringify({ name, tex_source: latexCode })
    });
    return parse(TemplateSchema, raw);
  },
  update: async (id: number, name: string, latexCode: string): Promise<Template> => {
    const raw = await fetchJSON(`/templates/${id}`, {
      method: "PUT",
      body: JSON.stringify({ name, tex_source: latexCode })
    });
    return parse(TemplateSchema, raw);
  },
  delete: async (id: number): Promise<void> => {
    await fetchJSON(`/templates/${id}`, { method: "DELETE" });
  }
};
