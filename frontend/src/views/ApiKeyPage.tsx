import { useEffect, useState } from "react";
import { mutate } from "swr";
import { Trash, Edit, Copy, Check, Loader2 } from "lucide-react";
import { getApiConfigs, setApiProvider } from "../apis/setup";
import type { ApiConfig } from "../apis/setup";

import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";

export const PROVIDERS_CONFIG: Record<string, { id: string; displayName: string }> = {
  groq: { id: "groq", displayName: "Groq" },
  openai: { id: "openai", displayName: "OpenAI" },
  anthropic: { id: "anthropic", displayName: "Anthropic" },
  mistralai: { id: "mistralai", displayName: "Mistral AI" },
  openrouter: { id: "openrouter", displayName: "OpenRouter" },
  google_genai: { id: "google_genai", displayName: "Google GenAI" },
  huggingface: { id: "huggingface", displayName: "Hugging Face" },
};

const ApiKeysPage = () => {
  const [keys, setKeys] = useState<ApiConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Form state
  const [selectedProvider, setSelectedProvider] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [apiKeyError, setApiKeyError] = useState<string | null>(null);

  const fetchKeys = async () => {
    try {
      setLoading(true);
      const data = await getApiConfigs();
      setKeys(data);
    } catch (err) {
      console.error("Failed to load API keys:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleSave = async () => {
    if (!selectedProvider) return;
    setApiKeyError(null);
    try {
      setIsSubmitting(true);
      await setApiProvider(selectedProvider, apiKeyInput);
      await fetchKeys();
      // Clear SWR model caches immediately
      mutate("/setup/api-models");
      mutate("/setup/current-model");
      // Reset form
      setApiKeyInput("");
      setSelectedProvider("");
      setIsEditing(false);
    } catch (err: unknown) {
      // @ts-expect-error accessing nested property on unknown error
      const detail = err?.response?.data?.detail;
      if (detail?.error_type === "invalid_api_key") {
        setApiKeyError(detail.message || "Invalid API key");
      } else {
        console.error("Failed to save key:", err);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (provider: string) => {
    try {
      setLoading(true);
      await setApiProvider(provider, "");
      await fetchKeys();
      // Clear SWR model caches immediately
      mutate("/setup/api-models");
      mutate("/setup/current-model");
      if (selectedProvider === provider) {
        setSelectedProvider("");
        setApiKeyInput("");
        setIsEditing(false);
      }
    } catch (err) {
      console.error("Failed to delete key:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (config: ApiConfig) => {
    setSelectedProvider(config.provider);
    setApiKeyInput(config.encrypted_key);
    setIsEditing(true);
  };

  const handleCopy = (provider: string, val: string) => {
    navigator.clipboard.writeText(val);
    setCopiedId(provider);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getUnusedProviders = () => {
    const usedProviders = new Set(keys.map((k) => k.provider));
    return Object.values(PROVIDERS_CONFIG).filter(
      (p) => !usedProviders.has(p.id),
    );
  };

  const getDisplayName = (id: string) => {
    if (!id) return "";
    const config = Object.values(PROVIDERS_CONFIG).find((p) => p.id === id);
    return config ? config.displayName : id.toUpperCase();
  };

  const maskKey = (key: string) => {
    if (!key) return "Not Set / Empty";
    if (key.length <= 8) return "********";
    return key.substring(0, 4) + "..." + key.substring(key.length - 4);
  };

  return (
    <div className="px-6 py-10 flex flex-col gap-6 overflow-y-auto h-full w-full">
      {/* Header */}
      <div>
        <h1 className="font-['EB_Garamond'] text-[36px] font-semibold text-foreground tracking-tight">
          API Keys
        </h1>
        <p className="text-[13px] text-muted-foreground mt-1">
          Manage credentials and endpoints for LLM providers securely.
        </p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center text-muted-foreground">
          <Loader2 size={24} className="animate-spin text-primary" />
          <p className="font-medium text-xs">Loading API keys...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Side: Keys Grid (8 columns) */}
          <div className="col-span-1 lg:col-span-8 flex flex-col gap-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Active Providers ({keys.length})
            </h2>

            {keys.length === 0 ? (
              <div className="p-8 bg-muted/20 rounded-xl text-center">
                <p className="text-sm text-muted-foreground">
                  No API keys configured yet.
                </p>
                <p className="text-xs text-muted-foreground/80 mt-1">
                  Use the form on the right to configure your first provider key.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {keys.map((config) => (
                  <div
                    key={config.provider}
                    className="p-5 bg-card dark:bg-muted/10 rounded-xl shadow-xs transition-all duration-300 hover:bg-muted/30 dark:hover:bg-muted/20"
                  >
                    <div className="flex flex-col gap-4">
                      <div className="flex justify-between items-center">
                        <span className="font-['EB_Garamond'] text-[17px] font-semibold text-foreground">
                          {getDisplayName(config.provider)}
                        </span>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-lg"
                            onClick={() => handleEdit(config)}
                            aria-label="Edit Key"
                          >
                            <Edit size={14} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-lg text-red-500 hover:text-red-600 hover:bg-red-500/10"
                            onClick={() => handleDelete(config.provider)}
                            aria-label="Delete Key"
                          >
                            <Trash size={14} />
                          </Button>
                        </div>
                      </div>

                      <div className="flex justify-between items-center bg-muted/60 dark:bg-muted/20 p-3 rounded-lg gap-2">
                        <span className="font-mono text-xs text-foreground overflow-hidden text-ellipsis whitespace-nowrap">
                          {maskKey(config.encrypted_key)}
                        </span>
                        {config.encrypted_key && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 rounded-md shrink-0"
                            onClick={() =>
                              handleCopy(config.provider, config.encrypted_key)
                            }
                            aria-label="Copy Key"
                          >
                            {copiedId === config.provider ? (
                              <Check size={14} className="text-primary" />
                            ) : (
                              <Copy size={12} />
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Side: Add / Update Form (4 columns) */}
          <div className="col-span-1 lg:col-span-4">
            <div className="p-6 bg-card dark:bg-muted/10 rounded-xl shadow-xs">
              <div className="flex flex-col gap-5">
                <div className="font-['EB_Garamond'] text-lg font-semibold tracking-wider uppercase text-foreground">
                  {isEditing ? "Modify Provider" : "New Provider"}
                </div>
                <hr className="border-t border-border" />

                {isEditing ? (
                  <div className="p-3 bg-primary/10 text-primary rounded-lg text-xs font-medium">
                    Editing API key for{" "}
                    <span className="font-bold">
                      {getDisplayName(selectedProvider)}
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <label className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px]">
                      Provider
                    </label>
                    <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">:</span>
                    <div className="w-full">
                      <Select
                        value={selectedProvider}
                        onValueChange={setSelectedProvider}
                      >
                        <SelectTrigger className="w-full h-8 bg-transparent border-0 border-b border-border rounded-none shadow-none px-0 text-sm font-normal focus:ring-0 focus-visible:ring-0">
                          <SelectValue placeholder="Select provider" />
                        </SelectTrigger>
                        <SelectContent className="rounded-lg">
                          {getUnusedProviders().map((p) => (
                            <SelectItem
                              key={p.id}
                              value={p.id}
                              className="rounded-md"
                            >
                              {p.displayName}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}

                <div className="flex items-baseline gap-2">
                  <label className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px]">
                    API Key
                  </label>
                  <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">:</span>
                  <div className="w-full">
                    <input
                      placeholder="sk-..."
                      value={apiKeyInput}
                      onChange={(e) => {
                        setApiKeyInput(e.target.value);
                        if (apiKeyError) setApiKeyError(null);
                      }}
                      type="password"
                      className="font-sans text-sm border-0 border-b border-border bg-transparent text-foreground placeholder:text-muted-foreground/40 placeholder:text-xs py-1.5 outline-none w-full focus:border-primary transition-colors"
                    />
                    {apiKeyError && (
                      <div className="mt-1.5 text-xs text-red-500 font-medium">
                        ⚠ {apiKeyError}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  {isEditing && (
                    <button
                      className="flex-1 bg-transparent text-foreground font-['EB_Garamond'] text-[13px] font-medium tracking-wider uppercase border border-border rounded py-2 cursor-pointer hover:bg-muted/40 transition-all duration-150"
                      onClick={() => {
                        setIsEditing(false);
                        setSelectedProvider("");
                        setApiKeyInput("");
                      }}
                    >
                      Cancel
                    </button>
                  )}
                  <button
                    className="flex-1 bg-transparent text-foreground font-['EB_Garamond'] text-[13px] font-medium tracking-wider uppercase border-[1.5px] border-foreground rounded py-2 cursor-pointer hover:bg-foreground hover:text-background transition-all duration-150 disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-foreground"
                    disabled={
                      !selectedProvider || !apiKeyInput.trim() || isSubmitting
                    }
                    onClick={handleSave}
                  >
                    {isSubmitting ? (
                      <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                    ) : isEditing ? (
                      "Update Key"
                    ) : (
                      "Save Key"
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiKeysPage;