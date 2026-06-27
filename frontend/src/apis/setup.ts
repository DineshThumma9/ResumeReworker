import { fetchJSON } from "./api";

export interface ApiConfig {
  provider: string;
  encrypted_key: string; // From the backend, this is actually the plaintext key
}

export const getApiConfigs = async (): Promise<ApiConfig[]> => {
  return await fetchJSON("/setup/api-config");
};

export const setApiProvider = async (
  provider: string,
  apiKey: string,
): Promise<unknown> => {
  return await fetchJSON("/setup/init", {
    method: "POST",
    body: JSON.stringify({
      api_provider: provider,
      api_key: apiKey,
    }),
  });
};

export const getApiModels = async (): Promise<Record<string, string[]>> => {
  return await fetchJSON("/setup/api-models");
};

export const apiKeySelection = async (api_prov: string, api_key: string) => {
  try {
    const res = await setApiProvider(api_prov, api_key);
    return res;
  } catch (error) {
    console.error("API error in apiKeySelection:", error);
    throw error;
  }
};

export const llmSelection = async (providerId: string) => {
  return await fetchJSON("/setup/providers", {
    method: "POST",
    body: JSON.stringify({ provider: providerId }),
  });
};

export const modelSelection = async (model: string, provider: string) => {
  return await fetchJSON("/setup/models", {
    method: "POST",
    body: JSON.stringify({ model: model, provider: provider }),
  });
};

export const getCurrentModel = async (): Promise<{ provider: string; model: string }> => {
  return await fetchJSON("/setup/current-model");
};

