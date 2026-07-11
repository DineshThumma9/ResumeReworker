import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Check, ArrowRight, User, Key, Upload } from "lucide-react";
import { authApi } from "../apis/auth";
import {
  setApiProvider,
  getApiModels,
  llmSelection,
  modelSelection,
} from "../apis/setup";
import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";

const PROVIDERS: Record<string, string> = {
  groq: "Groq",
  openai: "OpenAI",
  anthropic: "Anthropic",
  mistralai: "Mistral AI",
  openrouter: "OpenRouter",
  google_genai: "Google GenAI",
  huggingface: "Hugging Face",
};

export function OnboardingView() {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);

  // Step 1: LLM Setup State
  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [step1Error, setStep1Error] = useState<string | null>(null);

  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [isSettingModel, setIsSettingModel] = useState(false);

  // Step 2: Profile Setup State
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");
  const [github, setGithub] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [website, setWebsite] = useState("");
  const [sections, setSections] = useState<any>({});

  const [isAutofilling, setIsAutofilling] = useState(false);
  const [autofillError, setAutofillError] = useState<string | null>(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [step2Error, setStep2Error] = useState<string | null>(null);

  // Load available models once provider key is saved successfully
  const fetchModelsForProvider = async (provId: string) => {
    try {
      const modelsMap = await getApiModels();
      const models = modelsMap[provId] || [];
      setAvailableModels(models);
      if (models.length > 0) {
        setSelectedModel(models[0]);
      }
    } catch (err) {
      console.error("Failed to load models:", err);
    }
  };

  const handleValidateKey = async () => {
    if (!provider || !apiKey.trim()) return;
    setStep1Error(null);
    setIsValidating(true);
    try {
      // 1. Save and validate API key
      await setApiProvider(provider, apiKey.trim());
      // 2. Select active LLM provider
      await llmSelection(provider);
      // 3. Fetch model list
      await fetchModelsForProvider(provider);
    } catch (err: any) {
      console.error("Key validation failed:", err);
      let msg = "Failed to validate API key. Please check your credentials.";
      if (err instanceof Error) {
        msg = err.message;
      }
      setStep1Error(msg);
    } finally {
      setIsValidating(false);
    }
  };

  const handleSaveModel = async () => {
    if (!selectedModel) return;
    setStep1Error(null);
    setIsSettingModel(true);
    try {
      await modelSelection(selectedModel, provider);
      // Advance to profile step
      setStep(2);
    } catch (err: any) {
      setStep1Error(err.message || "Failed to set model.");
    } finally {
      setIsSettingModel(false);
    }
  };

  // Profile Autofill Upload Handler
  const handleAutofillUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsAutofilling(true);
    setAutofillError(null);
    try {
      const data = await authApi.autofillProfile(file);

      if (data.name) setName(data.name);
      if (data.phone) setPhone(data.phone);
      if (data.location) setLocation(data.location);
      if (data.github) setGithub(data.github);
      if (data.linkedin) setLinkedin(data.linkedin);
      if (data.website) setWebsite(data.website);
      if (data.sections) setSections(data.sections);
    } catch (err: any) {
      console.error("Autofill error:", err);
      setAutofillError(err.message || "Failed to parse resume.");
    } finally {
      setIsAutofilling(false);
      e.target.value = "";
    }
  };

  const handleFinishOnboarding = async (e: React.FormEvent) => {
    e.preventDefault();
    setStep2Error(null);
    setIsSavingProfile(true);
    try {
      const serializedSections = JSON.stringify(sections);

      const profile = await authApi.getProfile();
      await authApi.updateProfile({
        name: name || profile.name || "Untitled Candidate",
        email: profile.email,
        phone: phone || null,
        location: location || null,
        github: github || null,
        linkedin: linkedin || null,
        website: website || null,
        raw_resume: serializedSections || null,
      });
      // Redirect to Main Library Dashboard
      navigate("/analyze");
    } catch (err: any) {
      console.error("Profile save error:", err);
      setStep2Error(err.message || "Failed to save profile.");
    } finally {
      setIsSavingProfile(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#607456] flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">
      {/* decorative blobs */}
      <div className="pointer-events-none absolute top-[-12%] right-[-6%] w-[44vw] h-[44vw] rounded-full bg-white/6 z-0" />
      <div className="pointer-events-none absolute bottom-[-16%] left-[14%] w-[26vw] h-[26vw] rounded-full bg-white/4 z-0" />

      {/* Main Container Card */}
      <div className="bg-white dark:bg-[#1f281b] w-full max-w-2xl rounded-2xl shadow-2xl p-8 md:p-10 relative z-10 animate-in fade-in zoom-in-95 duration-400">
        {/* Header Title */}
        <div className="text-center mb-8 flex flex-col items-center gap-2">
          <div className="h-10 w-10 bg-[#2d3b28] rounded-xl flex items-center justify-center text-white text-lg font-bold">
            R
          </div>
          <h1 className="font-['EB_Garamond'] text-[32px] font-bold text-foreground leading-tight tracking-tight mt-2">
            Welcome to Resume Reworker
          </h1>
          <p className="text-xs text-muted-foreground/80 max-w-sm">
            Let's get your AI capabilities configured and your profile set up so
            you can start rewriting resumes in seconds.
          </p>
        </div>

        {/* Steps Indicators */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${step === 1 ? "bg-[#2d3b28] text-white border-transparent" : "bg-muted text-muted-foreground border-border"}`}
          >
            <Key size={12} />
            1. API Configuration
          </div>
          <ArrowRight size={14} className="text-muted-foreground/40" />
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${step === 2 ? "bg-[#2d3b28] text-white border-transparent" : "bg-muted text-muted-foreground border-border"}`}
          >
            <User size={12} />
            2. Profile Setup
          </div>
        </div>

        {/* STEP 1: API KEYS CONFIGURATION */}
        {step === 1 && (
          <div className="flex flex-col gap-6 animate-in fade-in duration-300">
            <div className="bg-muted/40 dark:bg-muted/10 p-5 rounded-xl border border-border/40">
              <h3 className="font-['EB_Garamond'] text-[18px] font-bold text-foreground mb-1.5 flex items-center gap-2">
                🔑 Configure AI Provider
              </h3>
              <p className="text-[11px] text-muted-foreground/90 leading-relaxed">
                Choose your preferred LLM provider, supply your API Key, and
                select a model. The key is validated in real-time with the
                provider's official servers.
              </p>
            </div>

            {/* Provider Select */}
            <div className="flex items-center gap-4">
              <label className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px] shrink-0">
                Provider
              </label>
              <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">
                :
              </span>
              <div className="w-full">
                <Select
                  value={provider}
                  onValueChange={setProvider}
                  disabled={availableModels.length > 0}
                >
                  <SelectTrigger className="w-full h-9 bg-transparent border-0 border-b border-border rounded-none shadow-none px-0 text-sm font-normal focus:ring-0 focus-visible:ring-0">
                    <SelectValue placeholder="Select LLM provider" />
                  </SelectTrigger>
                  <SelectContent className="rounded-lg">
                    {Object.entries(PROVIDERS).map(([id, name]) => (
                      <SelectItem key={id} value={id} className="rounded-md">
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* API Key Input */}
            {availableModels.length === 0 && (
              <div className="flex items-baseline gap-4">
                <label className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px] shrink-0">
                  API Key
                </label>
                <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">
                  :
                </span>
                <div className="w-full">
                  <input
                    type="password"
                    placeholder={`Enter ${provider ? PROVIDERS[provider] : ""} API Key`}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={!provider}
                    className="font-sans text-sm border-0 border-b border-border bg-transparent text-foreground placeholder:text-muted-foreground/40 placeholder:text-xs py-1.5 outline-none w-full focus:border-primary transition-colors disabled:opacity-40"
                  />
                </div>
              </div>
            )}

            {/* Model Select (rendered once key is validated) */}
            {availableModels.length > 0 && (
              <div className="flex items-center gap-4 animate-in fade-in duration-300">
                <label className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px] shrink-0">
                  Model
                </label>
                <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">
                  :
                </span>
                <div className="w-full">
                  <Select
                    value={selectedModel}
                    onValueChange={setSelectedModel}
                  >
                    <SelectTrigger className="w-full h-9 bg-transparent border-0 border-b border-border rounded-none shadow-none px-0 text-sm font-normal focus:ring-0 focus-visible:ring-0">
                      <SelectValue placeholder="Select LLM model" />
                    </SelectTrigger>
                    <SelectContent className="rounded-lg">
                      {availableModels.map((m) => (
                        <SelectItem key={m} value={m} className="rounded-md">
                          {m}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {step1Error && (
              <p className="text-xs text-red-500 font-semibold bg-red-500/5 border border-red-500/10 p-3 rounded-lg leading-relaxed">
                ⚠ {step1Error}
              </p>
            )}

            {/* Step 1 Actions */}
            <div className="flex justify-end gap-3 mt-4 border-t border-border pt-6">
              {availableModels.length > 0 ? (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setAvailableModels([]);
                      setSelectedModel("");
                      setApiKey("");
                    }}
                    className="font-['EB_Garamond'] text-xs font-semibold tracking-wider uppercase"
                  >
                    Reset Credentials
                  </Button>
                  <Button
                    onClick={handleSaveModel}
                    disabled={isSettingModel}
                    className="bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[13px] font-semibold tracking-wider uppercase rounded-md px-6 shadow-sm"
                  >
                    {isSettingModel ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        Continue to Profile{" "}
                        <ArrowRight size={14} className="ml-1" />
                      </>
                    )}
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => setStep(2)}
                    className="font-['EB_Garamond'] text-xs font-semibold tracking-wider uppercase text-muted-foreground/80 hover:text-foreground"
                  >
                    Configure Later / Skip Setup
                  </Button>
                  <Button
                    onClick={handleValidateKey}
                    disabled={!provider || !apiKey.trim() || isValidating}
                    className="bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[13px] font-semibold tracking-wider uppercase rounded-md px-6 shadow-sm"
                  >
                    {isValidating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-1" />
                        Validating...
                      </>
                    ) : (
                      "Validate & Save Key"
                    )}
                  </Button>
                </>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: PROFILE & RESUME AUTOFILL */}
        {step === 2 && (
          <form
            onSubmit={handleFinishOnboarding}
            className="flex flex-col gap-6 animate-in fade-in duration-300 max-h-[70vh] overflow-y-auto pr-2"
          >
            {/* Autofill PDF Box */}
            <div className="flex flex-col items-center gap-4 bg-muted/15 dark:bg-muted/5 border border-dashed border-border rounded-xl p-6 text-center w-full">
              <div className="h-8 w-8 bg-[#2d3b28]/10 text-[#2d3b28] dark:bg-white/10 dark:text-white rounded-full flex items-center justify-center">
                <Upload size={16} />
              </div>
              <div className="flex flex-col gap-1">
                <h3 className="font-['EB_Garamond'] text-[17px] font-semibold text-foreground">
                  Autofill from Resume (Highly Recommended)
                </h3>
                <p className="text-[11px] text-muted-foreground leading-relaxed max-w-sm">
                  Upload your existing PDF resume, and our AI will automatically
                  parse and fill out your contact details, education,
                  experiences, projects, and skills.
                </p>
              </div>
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleAutofillUpload}
                  disabled={isAutofilling}
                  className="hidden"
                  id="onboarding-file-input"
                />
                <label
                  htmlFor="onboarding-file-input"
                  className="flex items-center gap-2 bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[12px] font-semibold tracking-wider uppercase rounded-md px-4 py-2 cursor-pointer transition-colors shadow-sm disabled:opacity-50"
                >
                  {isAutofilling ? (
                    <>
                      <Loader2 size={13} className="animate-spin" />
                      Parsing Resume...
                    </>
                  ) : (
                    "Upload Resume PDF"
                  )}
                </label>
              </div>
              {autofillError && (
                <p className="text-[11px] text-red-500 font-medium">
                  {autofillError}
                </p>
              )}
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                {
                  label: "Full Name",
                  val: name,
                  set: setName,
                  ph: "e.g. John Doe",
                },
                {
                  label: "Phone",
                  val: phone,
                  set: setPhone,
                  ph: "e.g. (555) 019-2834",
                },
                {
                  label: "Location",
                  val: location,
                  set: setLocation,
                  ph: "e.g. San Francisco, CA",
                },
                {
                  label: "GitHub URL",
                  val: github,
                  set: setGithub,
                  ph: "e.g. github.com/username",
                },
                {
                  label: "LinkedIn URL",
                  val: linkedin,
                  set: setLinkedin,
                  ph: "e.g. linkedin.com/in/username",
                },
                {
                  label: "Website",
                  val: website,
                  set: setWebsite,
                  ph: "e.g. portfolio.com",
                },
              ].map((f) => (
                <div key={f.label} className="flex flex-col gap-1">
                  <label className="font-sans text-[11px] font-semibold text-foreground">
                    {f.label}
                  </label>
                  <input
                    type="text"
                    placeholder={f.ph}
                    value={f.val}
                    onChange={(e) => f.set(e.target.value)}
                    className="font-sans text-xs border border-border rounded-lg bg-transparent text-foreground placeholder:text-muted-foreground/30 p-2.5 outline-none w-full focus:border-primary transition-colors"
                  />
                </div>
              ))}
            </div>

            {Object.keys(sections).length > 0 && (
              <div className="bg-green-500/5 border border-green-500/10 p-3 rounded-lg flex items-center gap-2">
                <Check size={14} className="text-green-500 shrink-0" />
                <span className="text-[11px] text-green-600 font-medium leading-relaxed">
                  Successfully parsed resume sections (Experience, Education,
                  Projects, Skills)! These will be saved to your profile.
                </span>
              </div>
            )}

            {step2Error && (
              <p className="text-xs text-red-500 font-semibold bg-red-500/5 border border-red-500/10 p-3 rounded-lg leading-relaxed">
                ⚠ {step2Error}
              </p>
            )}

            {/* Step 2 Actions */}
            <div className="flex justify-between items-center mt-4 border-t border-border pt-6">
              <Button
                variant="ghost"
                type="button"
                onClick={() => setStep(1)}
                className="font-['EB_Garamond'] text-xs font-semibold tracking-wider uppercase text-muted-foreground/80 hover:text-foreground"
              >
                Back to API Setup
              </Button>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  type="button"
                  onClick={() => navigate("/analyze")}
                  className="font-['EB_Garamond'] text-xs font-semibold tracking-wider uppercase text-muted-foreground/60 hover:text-foreground"
                >
                  Skip Profile Setup
                </Button>
                <Button
                  type="submit"
                  disabled={isSavingProfile}
                  className="bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[13px] font-semibold tracking-wider uppercase rounded-md px-6 shadow-sm"
                >
                  {isSavingProfile ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    "Complete Setup"
                  )}
                </Button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
