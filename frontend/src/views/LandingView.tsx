import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../apis/auth";
import { AuthForm } from "../components/AuthForm";
import { useAuthStore } from "../store/authStore";
import { BrandLogo } from "../components/BrandLogo";
import { ResumeCard, type CardData } from "../components/HeroResumeCard";

const CARDS: CardData[] = [
  {
    id: "a",
    name: "Jake Taylor",
    contact: "jake.t@email.com · (555) 123-4567 · linkedin.com/in/jt",
    edu: {
      school: "State University — B.S. Computer Science",
      years: "2018 – 2022",
    },
    exp: [
      {
        title: "Software Engineer · Acme Corp",
        years: "2022 – present",
        bars: ["f", "m", "s"],
      },
      {
        title: "Engineering Intern · StartupCo",
        years: "Summer 2021",
        bars: ["m", "s"],
      },
    ],
    skills: ["Python", "React", "TypeScript", "PostgreSQL", "Docker", "AWS"],
    score: { val: "88 / 100", bg: "#eaf3de", color: "#3b6d11" },
  },
  {
    id: "b",
    name: "Alex Morgan",
    contact: "alex@email.com · (555) 987-6543 · linkedin.com/in/am",
    edu: {
      school: "Tech Institute — M.S. Software Engineering",
      years: "2017 – 2021",
    },
    exp: [
      {
        title: "Senior Developer · MegaCorp",
        years: "2021 – present",
        bars: ["f", "f", "m"],
      },
      {
        title: "Junior Developer · Agency",
        years: "2019 – 2021",
        bars: ["m", "s"],
      },
    ],
    projects: [
      {
        title: "Open Source CLI Tool",
        year: "2022",
        bars: ["m"],
        skills: ["TypeScript", "Go", "Redis"],
      },
    ],
    score: { val: "64 / 100", bg: "#faeeda", color: "#633806" },
  },
  {
    id: "c",
    name: "Jake Ryan",
    contact: "jake@email.com · (555) 000-1234 · github.com/jryan",
    edu: {
      school: "Southwestern University — B.S. Information Systems",
      years: "2018 – 2022",
    },
    exp: [
      {
        title: "Undergraduate Researcher · SWU Lab",
        years: "2022 – present",
        bars: ["f", "m", "s"],
      },
      {
        title: "IT Support Specialist · Campus IT",
        years: "2020 – 2022",
        bars: ["m", "s"],
      },
    ],
    skills: ["Java", "C++", "Linux", "Git", "Bash", "Kubernetes"],
    score: { val: "41 / 100", bg: "#fcebeb", color: "#791f1f" },
  },
];

export function LandingView({
  startMode,
}: {
  startMode?: "signin" | "signup";
}) {
  const [expanded, setExpanded] = useState(!!startMode);
  const [authMode, setAuthMode] = useState<"signin" | "signup">(
    startMode || "signup",
  );
  const navigate = useNavigate();
  const [notification, setNotification] = useState<{
    title: string;
    message: string;
    isNew?: boolean;
  } | null>(null);

  // Sync state if URL changes directly
  useEffect(() => {
    if (startMode) {
      setExpanded(true);
      setAuthMode(startMode);
    } else {
      setExpanded(false);
    }
  }, [startMode]);

  // Extract OAuth code on callback redirection
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");

    if (code) {
      // Clear the code from the URL so we don't exchange it again on refresh
      window.history.replaceState({}, document.title, window.location.pathname);

      authApi
        .googleExchange(code)
        .then((res) => {
          useAuthStore.getState().setAuthenticated(true);
          if (res.new) {
            setNotification({
              title: "Account Created",
              message:
                "Welcome! Your account has been successfully created via Google.",
              isNew: true,
            });
          } else {
            setNotification({
              title: "Welcome Back",
              message: "You have been successfully logged in via Google.",
              isNew: false,
            });
          }
        })
        .catch((err) => {
          console.error("Google authentication failed:", err);
          setNotification({
            title: "Authentication Failed",
            message:
              "There was a problem signing in with Google. Please try again.",
            isNew: false,
          });
        });
    }
  }, [navigate]);

  const handleNotificationDismiss = () => {
    const isNew = notification?.isNew;
    setNotification(null);
    if (isNew) {
      navigate("/onboarding", { replace: true });
    } else {
      navigate("/analyze", { replace: true });
    }
  };

  const expand = useCallback(
    (mode: "signin" | "signup" = "signup") => {
      setAuthMode(mode);
      setExpanded(true);
      if (mode === "signin") {
        navigate("/login", { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    },
    [navigate],
  );

  const collapse = useCallback(() => {
    setExpanded(false);
    navigate("/", { replace: true });
  }, [navigate]);

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-[#607456] flex flex-col">
      {/* decorative blobs */}
      <div className="pointer-events-none absolute top-[-12%] right-[-6%] w-[44vw] h-[44vw] rounded-full bg-white/6 z-0" />
      <div className="pointer-events-none absolute bottom-[-16%] right-[14%] w-[26vw] h-[26vw] rounded-full bg-white/4 z-0" />

      {/* ── NAVBAR ── */}
      <nav className="relative z-50 flex items-center justify-between px-4 md:px-10 pt-8 pb-2 shrink-0">
        <div className="flex items-center gap-3 h-8 shrink-0">
          {expanded && (
            <button
              onClick={collapse}
              className="text-white/60 hover:text-white transition-colors bg-transparent border-none cursor-pointer flex items-center p-1 shrink-0"
              aria-label="Go back"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            </button>
          )}
          <BrandLogo />
        </div>
        <div className="flex items-center gap-3 shrink-0">
          {!expanded && (
            <>
              <button
                onClick={() => expand("signin")}
                className="font-sans text-[13px] font-medium text-white/60 hover:text-white
                  bg-transparent border-none cursor-pointer transition-colors"
              >
                Sign in
              </button>
              <button
                onClick={() => expand("signup")}
                className="font-sans text-[13px] font-semibold text-[#607456] bg-white rounded-full
                  px-5 py-2 cursor-pointer hover:bg-white/90 transition-all duration-150"
              >
                Get started
              </button>
            </>
          )}
        </div>
      </nav>

      {/* ════════════════════════════════════════════════════════════════
          CLOSED STATE
      ════════════════════════════════════════════════════════════════ */}
      <div
        className={`relative z-10 flex-1 flex flex-col md:flex-row items-center transition-all duration-300 ease-in-out
          ${expanded ? "opacity-0 pointer-events-none" : "opacity-100"}`}
      >
        {/* Hero — left column */}
        <div className="px-6 md:px-0 md:pl-24 xl:pl-40 mt-8 md:mt-0 w-full md:w-[50%] flex flex-col justify-center items-center md:items-start text-center md:text-left">
          <h1 className="font-heading text-[clamp(3rem,5.8vw,5.2rem)] leading-[1.02] text-white mb-4">
            Your résumé,
            <br />
            <em className="not-italic text-[#b8d4a4]">rewritten</em>
            <br />
            for the role.
          </h1>
          <p className="font-sans text-[15px] text-white/55 leading-[1.8] max-w-[290px] mb-8">
            Paste a job description. Get a tailored resume and ATS fit score in
            under 30 seconds.
          </p>
          <button
            onClick={() => expand("signup")}
            className="self-center md:self-start font-sans text-[14px] font-semibold text-white
              bg-white/15 border border-white/30 rounded-full px-8 py-3
              cursor-pointer hover:bg-white/25 transition-all duration-200"
          >
            Get started →
          </button>
        </div>

        {/* Resume fan — right column, taller container */}
        <div className="w-full md:flex-1 relative h-[350px] md:h-[min(680px,85vh)] min-w-0 mt-8 md:mt-0">
          <ResumeCard card={CARDS[0]} exitLeft={expanded} />
          <ResumeCard card={CARDS[1]} />
          <ResumeCard card={CARDS[2]} exitRight={expanded} />
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════
          OPEN STATE
      ════════════════════════════════════════════════════════════════ */}

      {/* Editorial left — open state */}
      <div
        className={`absolute inset-y-0 left-0 flex-col justify-center px-8 md:px-16 xl:px-28 z-10
          w-full md:w-[54%] transition-opacity duration-350 ease-in-out
          hidden md:flex
          ${expanded ? "opacity-100 pointer-events-auto delay-300" : "opacity-0 pointer-events-none"}`}
      >
        <h2 className="font-heading text-[clamp(2.8rem,4.8vw,4.4rem)] leading-[1.04] text-white mb-5">
          Your résumé,
          <br />
          <em className="not-italic text-[#b8d4a4]">rewritten</em>
          <br />
          for the role.
        </h2>
        <p className="font-sans text-[15px] text-white/52 leading-[1.8] mb-10 max-w-[380px]">
          Paste a job description. Get a tailored resume and ATS fit score in
          under 30 seconds.
        </p>

        <div className="flex gap-4 max-w-[460px]">
          {[
            { val: "30", unit: "s", lbl: "Average rewrite time" },
            { val: "∞", unit: "", lbl: "Roles you can tailor" },
            { val: "0", unit: "$", lbl: "To get started" },
          ].map((s) => (
            <div
              key={s.lbl}
              className="flex-1 bg-white/9 border border-white/15 rounded-xl px-4 py-4"
            >
              <div className="font-heading text-[clamp(1.8rem,2.8vw,2.4rem)] text-white leading-none mb-1.5">
                {s.val}
                <em className="not-italic text-[#b8d4a4]">{s.unit}</em>
              </div>
              <div className="font-sans text-[11px] text-white/45 leading-[1.45]">
                {s.lbl}
              </div>
            </div>
          ))}
        </div>
        <p className="font-sans text-[11px] text-white/28 mt-7">
          Anonymous · No data stored
        </p>
      </div>

      {/* Auth panel */}
      <div
        className={`absolute inset-y-0 right-0 z-30 flex items-center justify-center
          bg-[#2d3b28] md:transition-[width] duration-650 ease-in-out
          ${expanded ? "w-full md:w-[46%]" : "w-0"} overflow-hidden`}
      >
        <div
          className={`w-[min(480px,95%)] bg-white rounded-xl shadow-2xl px-6 md:px-10 py-8 md:py-9 flex flex-col
            transition-opacity duration-300 ${expanded ? "delay-500 opacity-100" : "opacity-0"}`}
        >
          <AuthForm
            key={authMode}
            initialMode={authMode}
            onSuccess={(mode) => {
              if (mode === "signup") {
                navigate("/onboarding");
              } else {
                navigate("/analyze");
              }
            }}
          />
        </div>
      </div>

      {/* OAUTH NOTIFICATION MODAL */}
      {notification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 animate-in fade-in zoom-in-95 duration-200 text-center">
            <h3 className="font-['EB_Garamond'] text-2xl font-semibold text-[#1a1a1a] mb-2">
              {notification.title}
            </h3>
            <p className="text-xs text-[#666] mb-6">{notification.message}</p>
            <div className="flex justify-center">
              <button
                className="bg-[#2d3b28] hover:bg-[#202a1c] text-white font-['EB_Garamond'] text-[13px] font-medium tracking-wider uppercase rounded px-6 py-2 cursor-pointer transition-colors"
                onClick={handleNotificationDismiss}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
