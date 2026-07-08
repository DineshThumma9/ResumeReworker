import { useEffect, useState } from "react";
import { Loader2, Save, Trash2, Plus } from "lucide-react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { authApi } from "../apis/auth";

interface SectionItem {
  id: string;
  title?: string;
  subtitle?: string;
  date?: string;
  skills?: string;
  link?: string;
  description?: string;
}

const AVAILABLE_SECTIONS = [
  { id: "experience", label: "Experience" },
  { id: "education", label: "Education" },
  { id: "projects", label: "Projects" },
  { id: "skills", label: "Skills" },
  { id: "open_source", label: "Open Source" },
  { id: "achievements", label: "Achievements" },
  { id: "hackathons", label: "Hackathons" },
  { id: "certifications", label: "Certifications" },
  { id: "coursework", label: "Coursework" },
];

const SECTION_FIELDS: Record<
  string,
  {
    title?: string;
    subtitle?: string;
    date?: string;
    skills?: string;
    link?: string;
    description?: string;
  }
> = {
  experience: {
    title: "Job Title",
    subtitle: "Company Name",
    date: "Dates / Duration",
    skills: "Skills / Tech Used",
    description: "Responsibilities & Achievements",
  },
  education: {
    title: "Degree / Major",
    subtitle: "School Name",
    date: "Dates / Duration",
    description: "GPA / Honors / Details",
  },
  projects: {
    title: "Project Title",
    subtitle: "Role / Contribution",
    skills: "Skills / Tech",
    link: "Project Link / URL",
    description: "Project Description",
  },
  skills: {
    title: "Category",
    skills: "Skills List (comma-separated)",
  },
  open_source: {
    title: "Repository Name",
    subtitle: "Contribution / Role",
    date: "Dates",
    link: "Contribution Link",
    description: "Details",
  },
  achievements: {
    title: "Achievement Title",
    date: "Date Received",
    description: "Details",
  },
  hackathons: {
    title: "Hackathon Name",
    subtitle: "Project Name / Award",
    date: "Date",
    description: "Project Description",
  },
  certifications: {
    title: "Certificate Title",
    subtitle: "Issuer",
    date: "Date Earned",
    link: "Credential URL",
  },
  coursework: {
    title: "Category",
    description: "Courses List",
  },
};

export function ProfileView() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const isOnboarding = searchParams.get("onboarding") === "true";

  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Profile metadata (display only)
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");

  // Form states
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");
  const [github, setGithub] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [website, setWebsite] = useState("");

  // Sections state
  const [sections, setSections] = useState<Record<string, SectionItem[]>>({});
  const [showAddMenu, setShowAddMenu] = useState(false);

  // Autofill states
  const [isAutofilling, setIsAutofilling] = useState(false);
  const [autofillError, setAutofillError] = useState<string | null>(null);

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

      if (data.sections) {
        setSections(data.sections);
      }

      setSuccess(
        "Profile autofilled successfully from resume! Don't forget to save changes.",
      );
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      console.error("Autofill error:", err);
      setAutofillError(
        err instanceof Error ? err.message : "Failed to parse resume.",
      );
    } finally {
      setIsAutofilling(false);
      e.target.value = "";
    }
  };

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await authApi.getProfile();
      setUsername(data.username || "");
      setEmail(data.email || "");
      setName(data.name || "");
      setPhone(data.phone || "");
      setLocation(data.location || "");
      setGithub(data.github || "");
      setLinkedin(data.linkedin || "");
      setWebsite(data.website || "");

      // Parse structured sections if it's JSON
      if (data.raw_resume) {
        try {
          const parsed = JSON.parse(data.raw_resume);
          if (typeof parsed === "object" && parsed !== null) {
            setSections(parsed);
          } else {
            // Fallback if plain text
            setSections({
              experience: [{ id: "1", description: data.raw_resume }],
            });
          }
        } catch {
          // Fallback if raw_resume is just raw text
          setSections({
            experience: [{ id: "1", description: data.raw_resume }],
          });
        }
      } else {
        setSections({});
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      setError("Failed to load profile details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSaving(true);
    try {
      // Serialize structured sections to raw_resume JSON
      const serializedSections = JSON.stringify(sections);

      await authApi.updateProfile({
        name,
        email,
        phone: phone || null,
        location: location || null,
        github: github || null,
        linkedin: linkedin || null,
        website: website || null,
        raw_resume: serializedSections,
      });
      setSuccess("Profile updated successfully.");
      if (isOnboarding) {
        setTimeout(() => navigate("/library"), 1000);
      } else {
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error("Failed to update profile:", err);
      setError("Failed to update profile details.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSection = (sectionId: string) => {
    if (sections[sectionId] !== undefined) return;
    setSections((prev) => ({
      ...prev,
      [sectionId]: [{ id: Math.random().toString(36).substring(7) }],
    }));
    setShowAddMenu(false);
  };

  const handleRemoveSection = (sectionId: string) => {
    const updated = { ...sections };
    delete updated[sectionId];
    setSections(updated);
  };

  const handleAddItem = (sectionId: string) => {
    setSections((prev) => ({
      ...prev,
      [sectionId]: [
        ...(prev[sectionId] || []),
        { id: Math.random().toString(36).substring(7) },
      ],
    }));
  };

  const handleRemoveItem = (sectionId: string, itemId: string) => {
    setSections((prev) => {
      const items = (prev[sectionId] || []).filter(
        (item) => item.id !== itemId,
      );
      return {
        ...prev,
        [sectionId]: items,
      };
    });
  };

  const handleFieldChange = (
    sectionId: string,
    itemId: string,
    field: keyof SectionItem,
    val: string,
  ) => {
    setSections((prev) => {
      const items = (prev[sectionId] || []).map((item) => {
        if (item.id === itemId) {
          return { ...item, [field]: val };
        }
        return item;
      });
      return {
        ...prev,
        [sectionId]: items,
      };
    });
  };

  const getUnusedSections = () => {
    return AVAILABLE_SECTIONS.filter((s) => sections[s.id] === undefined);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24 text-center text-muted-foreground h-full w-full">
        <Loader2 size={24} className="animate-spin text-primary" />
        <p className="font-medium text-xs">Loading profile details...</p>
      </div>
    );
  }

  // Generate default color for profile pic based on username letter
  const getAvatarBgColor = (char: string) => {
    const code = char.charCodeAt(0) || 0;
    const hues = [120, 160, 200, 240, 280, 320, 360];
    const selectedHue = hues[code % hues.length];
    return `hsl(${selectedHue}, 35%, 45%)`;
  };

  const firstLetter = (username || email || "?").charAt(0).toUpperCase();
  const avatarBg = getAvatarBgColor(firstLetter);

  return (
    <div className="px-6 py-10 flex flex-col gap-10 overflow-y-auto h-full w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col items-center text-center gap-4">
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center text-white text-3xl font-semibold shadow-xs select-none"
          style={{ backgroundColor: avatarBg }}
        >
          {firstLetter}
        </div>
        <div className="flex flex-col gap-1">
          <h1 className="font-['EB_Garamond'] text-[32px] font-semibold text-foreground tracking-tight leading-none">
            {name || username}
          </h1>
          <p className="font-sans text-[12px] text-muted-foreground tracking-wide uppercase">
            {username} <span className="mx-1.5 opacity-40">|</span> {email}
          </p>
        </div>
      </div>

      {/* ── AUTOFILL FROM RESUME ZONE ── */}
      <div className="flex flex-col items-center gap-4 bg-muted/10 dark:bg-muted/5 border border-dashed border-border rounded-xl p-6 text-center max-w-xl mx-auto w-full">
        <div className="flex flex-col gap-1">
          <h3 className="font-['EB_Garamond'] text-[18px] font-semibold text-foreground">
            Autofill Profile from Resume
          </h3>
          <p className="text-xs text-muted-foreground leading-relaxed max-w-md">
            Upload your existing PDF resume, and our AI will automatically parse
            and fill out your contact links, experience, education, projects,
            skills, and more!
          </p>
        </div>
        <div className="relative mt-2">
          <input
            type="file"
            accept=".pdf"
            onChange={handleAutofillUpload}
            disabled={isAutofilling}
            className="hidden"
            id="autofill-file-input"
          />
          <label
            htmlFor="autofill-file-input"
            className="flex items-center gap-2 bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[13px] font-semibold tracking-wider uppercase rounded-md px-5 py-2.5 cursor-pointer transition-colors shadow-sm disabled:opacity-50"
          >
            {isAutofilling ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Parsing Resume...
              </>
            ) : (
              <>
                <Plus size={15} />
                Upload Resume PDF
              </>
            )}
          </label>
        </div>
        {autofillError && (
          <p className="text-xs text-red-500 font-medium mt-1">
            {autofillError}
          </p>
        )}
      </div>

      {isOnboarding && (
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">✨</span>
            <h3 className="font-['EB_Garamond'] text-[20px] font-semibold text-foreground">
              Welcome to Resume Reworker!
            </h3>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Let's set up your contact links. Providing these now helps the AI
            automatically format, inject, and hyperlink them (like GitHub or
            LinkedIn) on your tailored resumes—even if they are missing from
            your uploaded files.
          </p>
          <p className="text-[11px] text-muted-foreground/80 italic">
            This setup is optional. You can fill out as much or as little as you
            like, or skip it entirely.
          </p>
        </div>
      )}

      <form onSubmit={handleSave} className="flex flex-col gap-10 w-full">
        {/* ── CONTACT & LINKS MATRIX (Grid layout) ── */}
        <div className="flex flex-col gap-6 bg-card dark:bg-muted/10 p-6 rounded-xl shadow-xs w-full">
          <div className="font-['EB_Garamond'] text-[18px] font-semibold tracking-wider uppercase text-foreground">
            Contact & Links
          </div>
          <hr className="border-t border-border -mt-2" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-6">
            {[
              {
                id: "name",
                label: "Full Name",
                val: name,
                set: setName,
                required: true,
                ph: "e.g. John Doe",
              },
              {
                id: "phone",
                label: "Phone",
                val: phone,
                set: setPhone,
                ph: "e.g. (555) 019-2834",
              },
              {
                id: "location",
                label: "Location",
                val: location,
                set: setLocation,
                ph: "e.g. San Francisco, CA",
              },
              {
                id: "github",
                label: "GitHub URL",
                val: github,
                set: setGithub,
                ph: "e.g. github.com/username",
              },
              {
                id: "linkedin",
                label: "LinkedIn URL",
                val: linkedin,
                set: setLinkedin,
                ph: "e.g. linkedin.com/in/username",
              },
              {
                id: "website",
                label: "Website",
                val: website,
                set: setWebsite,
                ph: "e.g. portfolio.com",
              },
            ].map((f) => (
              <div key={f.id} className="flex items-baseline gap-2">
                <span className="font-['EB_Garamond'] text-[16px] font-medium text-foreground whitespace-nowrap w-[90px]">
                  {f.label}{" "}
                  {f.required && <span className="text-red-500">*</span>}
                </span>
                <span className="font-['EB_Garamond'] text-[16px] text-muted-foreground shrink-0">
                  :
                </span>
                <input
                  type="text"
                  placeholder={f.ph}
                  value={f.val}
                  onChange={(e) => f.set(e.target.value)}
                  required={f.required}
                  className="font-sans text-sm border-0 border-b border-border bg-transparent text-foreground placeholder:text-muted-foreground/40 placeholder:text-xs py-1 outline-none w-full focus:border-primary transition-colors"
                />
              </div>
            ))}
          </div>
        </div>

        {/* ── Structured sections builder ── */}
        <div className="flex flex-col gap-6 bg-card dark:bg-muted/10 p-6 rounded-xl shadow-xs w-full">
          <div className="flex justify-between items-center">
            <div className="font-['EB_Garamond'] text-[18px] font-semibold tracking-wider uppercase text-foreground">
              Résumé Sections
            </div>
            {/* Horizontal Add Section Button */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowAddMenu(!showAddMenu)}
                className="flex items-center gap-1.5 bg-transparent text-foreground font-['EB_Garamond'] text-[13px] font-medium tracking-wider uppercase border border-border rounded-md px-3.5 py-1.5 cursor-pointer hover:bg-muted/40 transition-colors"
              >
                <Plus size={14} />
                Add Section
              </button>

              {showAddMenu && (
                <div className="absolute right-0 mt-2 z-50 w-48 bg-background border border-border rounded-lg shadow-lg py-1.5 animate-in fade-in slide-in-from-top-2 duration-150">
                  {getUnusedSections().length === 0 ? (
                    <div className="px-3 py-2 text-xs text-muted-foreground text-center">
                      All sections added
                    </div>
                  ) : (
                    getUnusedSections().map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => handleAddSection(s.id)}
                        className="w-full text-left font-sans text-xs hover:bg-muted px-4 py-2 text-foreground transition-colors"
                      >
                        {s.label}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
          <hr className="border-t border-border -mt-2" />

          {/* List of active sections */}
          <div className="flex flex-col gap-10 mt-2 w-full">
            {Object.keys(sections).length === 0 ? (
              <div className="py-12 border border-dashed border-border rounded-xl text-center flex flex-col items-center justify-center gap-2">
                <p className="text-sm font-semibold text-muted-foreground">
                  No sections configured
                </p>
                <p className="text-xs text-muted-foreground/80 max-w-md">
                  Click "Add Section" above to start building your professional
                  profile details.
                </p>
              </div>
            ) : (
              Object.keys(sections).map((key) => {
                const label =
                  AVAILABLE_SECTIONS.find((s) => s.id === key)?.label || key;
                const fieldsConfig = SECTION_FIELDS[key] || {};
                const activeFieldKeys = Object.keys(fieldsConfig).filter(
                  (k) => k !== "description",
                ) as Array<keyof SectionItem>;
                const items = sections[key] || [];

                return (
                  <div
                    key={key}
                    className="flex flex-col gap-4 border-b border-border pb-8 last:border-b-0 last:pb-0 animate-in fade-in duration-200"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-['EB_Garamond'] text-[19px] font-semibold text-foreground tracking-wide uppercase">
                        {label}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleAddItem(key)}
                          className="flex items-center gap-1 text-xs text-primary font-medium hover:underline cursor-pointer"
                        >
                          <Plus size={12} /> Add Item
                        </button>
                        <span className="text-muted-foreground/40 font-light">
                          |
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSection(key)}
                          className="text-red-500 hover:text-red-600 text-xs font-medium hover:underline cursor-pointer"
                          title={`Remove all ${label}`}
                        >
                          Remove Section
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-col gap-6">
                      {items.length === 0 ? (
                        <p className="text-xs text-muted-foreground italic pl-2">
                          No entries added. Click "Add Item" to add one.
                        </p>
                      ) : (
                        items.map((item) => (
                          <div
                            key={item.id}
                            className="flex flex-col gap-4 bg-muted/20 dark:bg-muted/5 p-5 rounded-lg relative group/item border border-transparent hover:border-border/30 transition-all"
                          >
                            {/* Remove Item Button */}
                            <button
                              type="button"
                              onClick={() => handleRemoveItem(key, item.id)}
                              className="absolute top-4 right-4 text-red-500 hover:text-red-600 opacity-0 group-hover/item:opacity-100 p-1 transition-opacity cursor-pointer"
                              title="Delete Entry"
                            >
                              <Trash2 size={14} />
                            </button>

                            {/* Inputs subgrid */}
                            {activeFieldKeys.length > 0 && (
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4 pr-6">
                                {activeFieldKeys.map((fKey) => {
                                  const fieldLabel =
                                    fieldsConfig[
                                      fKey as keyof typeof fieldsConfig
                                    ];
                                  return (
                                    <div
                                      key={fKey}
                                      className="flex flex-col gap-1.5"
                                    >
                                      <span className="font-sans text-[11px] font-semibold text-foreground/70 uppercase tracking-wider">
                                        {fieldLabel}
                                      </span>
                                      <input
                                        type="text"
                                        placeholder={`Enter ${fieldLabel?.toLowerCase()}`}
                                        value={item[fKey] || ""}
                                        onChange={(e) =>
                                          handleFieldChange(
                                            key,
                                            item.id,
                                            fKey,
                                            e.target.value,
                                          )
                                        }
                                        className="font-sans text-[13px] border-0 border-b border-border/50 bg-transparent text-foreground placeholder:text-muted-foreground/30 py-1.5 outline-none w-full focus:border-primary transition-colors"
                                      />
                                    </div>
                                  );
                                })}
                              </div>
                            )}

                            {/* Description Textarea */}
                            {fieldsConfig.description && (
                              <div className="flex flex-col gap-1.5 mt-2">
                                <span className="font-['EB_Garamond'] text-[15px] font-medium text-foreground">
                                  {fieldsConfig.description}
                                </span>
                                <textarea
                                  placeholder={`Detail your ${label.toLowerCase()} details here...`}
                                  value={item.description || ""}
                                  onChange={(e) =>
                                    handleFieldChange(
                                      key,
                                      item.id,
                                      "description",
                                      e.target.value,
                                    )
                                  }
                                  className="w-full min-h-[80px] font-sans text-xs leading-relaxed p-3 bg-background dark:bg-background/50 border border-border rounded-lg outline-none focus:border-primary transition-colors resize-y"
                                />
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col items-end gap-3 border-t border-border pt-6 mt-2 w-full">
          {error && <div className="text-red-500 text-sm">{error}</div>}
          {success && <div className="text-green-500 text-sm">{success}</div>}

          <div className="flex items-center gap-3">
            {isOnboarding && (
              <button
                type="button"
                onClick={() => navigate("/library")}
                className="bg-transparent text-muted-foreground font-['EB_Garamond'] text-[14px] font-medium tracking-widest uppercase border border-border rounded-md px-6 py-3 cursor-pointer hover:bg-muted/40 transition-all duration-150"
              >
                Skip Onboarding
              </button>
            )}
            <button
              type="submit"
              disabled={isSaving}
              className="bg-transparent text-foreground font-['EB_Garamond'] text-[14px] font-medium tracking-widest uppercase border-[1.5px] border-foreground rounded px-8 py-3.5 cursor-pointer hover:bg-foreground hover:text-background transition-all duration-150 disabled:opacity-50"
            >
              {isSaving ? (
                <Loader2 className="h-4 w-4 animate-spin mx-auto" />
              ) : (
                <div className="flex items-center gap-2">
                  <Save size={16} />
                  {isOnboarding ? "Save & Continue" : "Save Changes"}
                </div>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
