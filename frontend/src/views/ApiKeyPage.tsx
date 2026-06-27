import { useEffect, useState } from "react";
import { Trash, Edit, Copy, Check, Loader2 } from "lucide-react";
import { getApiConfigs, setApiProvider } from "../apis/setup";
import type { ApiConfig } from "../apis/setup";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
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

  // Mask the API key for display
  const maskKey = (key: string) => {
    if (!key) return "Not Set / Empty";
    if (key.length <= 8) return "********";
    return key.substring(0, 4) + "..." + key.substring(key.length - 4);
  };

  return (
    <div className="px-6 py-10 flex flex-col gap-6 overflow-y-auto h-full w-full">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-foreground">
          API Keys
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage credentials and endpoints for LLM providers securely.
        </p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center text-muted-foreground">
          <Loader2 size={32} className="animate-spin text-primary" />
          <p className="font-medium text-sm">Loading API keys...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Side: Keys Grid (8 columns) */}
          <div className="col-span-1 lg:col-span-8 flex flex-col gap-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Active Providers ({keys.length})
            </h2>

            {keys.length === 0 ? (
              <div className="p-8 bg-card rounded-xl border border-dashed border-border text-center">
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
                    className="p-5 bg-card rounded-xl border border-border transition-all duration-300 hover:border-primary/40 hover:shadow-sm"
                  >
                    <div className="flex flex-col gap-4">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-sm text-foreground">
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

                      <div className="flex justify-between items-center bg-muted/60 p-3 rounded-lg border border-border gap-2">
                        <span className="font-mono text-xs text-foreground overflow-hidden text-ellipsis whitespace-nowrap">
                          {maskKey(config.encrypted_key)}
                        </span>
                        {config.encrypted_key && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 rounded-md shrink-0"
                            onClick={() =>
                              handleCopy(
                                config.provider,
                                config.encrypted_key,
                              )
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
            <div
              className={`p-5 bg-card rounded-xl border ${
                isEditing ? "border-primary/50" : "border-border"
              } shadow-sm`}
            >
              <div className="flex flex-col gap-4">
                <h2 className="text-sm font-semibold text-foreground">
                  {isEditing ? "Update API Key" : "Add Provider Key"}
                </h2>

                {isEditing ? (
                  <div className="p-3 bg-primary/10 text-primary rounded-lg text-xs font-medium">
                    Editing API key for{" "}
                    <span className="font-bold">
                      {getDisplayName(selectedProvider)}
                    </span>
                  </div>
                ) : (
                  <div>
                    <label className="block mb-1.5 font-medium text-xs text-muted-foreground">
                      Provider
                    </label>
                    <Select
                      value={selectedProvider}
                      onValueChange={setSelectedProvider}
                    >
                      <SelectTrigger className="w-full h-10 rounded-lg bg-muted/40 border-border font-normal text-sm">
                        <SelectValue placeholder="Select a provider" />
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
                )}

                <div>
                  <label className="block mb-1.5 font-medium text-xs text-muted-foreground">
                    API Key
                  </label>
                  <Input
                    placeholder="sk-..."
                    value={apiKeyInput}
                    onChange={(e) => {
                      setApiKeyInput(e.target.value);
                      if (apiKeyError) setApiKeyError(null);
                    }}
                    type="password"
                    className={`h-10 rounded-lg bg-muted/40 border ${
                      apiKeyError
                        ? "border-red-500 focus-visible:ring-red-500"
                        : "border-border"
                    }`}
                  />
                  {apiKeyError && (
                    <div className="mt-1.5 text-xs text-red-500 font-medium flex items-center gap-1">
                      ⚠ {apiKeyError}
                    </div>
                  )}
                </div>

                <div className="flex gap-2 pt-2">
                  {isEditing && (
                    <Button
                      variant="ghost"
                      className="flex-1 h-10 rounded-lg text-sm"
                      onClick={() => {
                        setIsEditing(false);
                        setSelectedProvider("");
                        setApiKeyInput("");
                      }}
                    >
                      Cancel
                    </Button>
                  )}
                  <Button
                    className="flex-1 h-10 rounded-lg text-primary-foreground text-sm font-semibold shadow-sm"
                    disabled={
                      !selectedProvider || !apiKeyInput.trim() || isSubmitting
                    }
                    onClick={handleSave}
                  >
                    {isSubmitting ? (
                      <Loader2 className="h-4 w-4 animate-spin text-primary-foreground" />
                    ) : isEditing ? (
                      "Update Key"
                    ) : (
                      "Save Key"
                    )}
                  </Button>
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