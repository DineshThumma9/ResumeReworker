
import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { AuthForm } from "../components/AuthForm";
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


/* ── main landing ─────────────────────────────────────────────────── */
export function LandingView() {
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();

  const expand = useCallback(() => setExpanded(true), []);
  const collapse = useCallback(() => setExpanded(false), []);

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-[#607456] flex flex-col">
      {/* decorative blobs */}
      <div className="pointer-events-none absolute top-[-12%] right-[-6%] w-[44vw] h-[44vw] rounded-full bg-white/6 z-0" />
      <div className="pointer-events-none absolute bottom-[-16%] right-[14%] w-[26vw] h-[26vw] rounded-full bg-white/4 z-0" />

      {/* ── NAVBAR ── single brand, top left ─────────────────────────── */}
      <nav className="relative z-50 flex items-center justify-between px-10 pt-8 pb-2 shrink-0">
        <div className="flex items-center h-8">
          {expanded ? (
            <button
              onClick={collapse}
              className="text-white/60 hover:text-white transition-colors bg-transparent border-none cursor-pointer flex items-center p-1 -ml-1"
              aria-label="Go back"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
            </button>
          ) : (
            <BrandLogo />
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/login")}
            className="font-sans text-[13px] font-medium text-white/60 hover:text-white
              bg-transparent border-none cursor-pointer transition-colors"
          >
            Sign in
          </button>
          <button
            onClick={expand}
            className="font-sans text-[13px] font-semibold text-[#607456] bg-white rounded-full
              px-5 py-2 cursor-pointer hover:bg-white/90 transition-all duration-150"
          >
            Get started
          </button>
        </div>
      </nav>

      {/* ════════════════════════════════════════════════════════════════
          CLOSED STATE
      ════════════════════════════════════════════════════════════════ */}
      <div
        className={`relative z-10 flex-1 flex items-center transition-all duration-300 ease-in-out
          ${expanded ? "opacity-0 pointer-events-none" : "opacity-100"}`}
      >
        {/* Hero — left column */}
        <div className="pl-10 pr-4 w-[40%] flex flex-col justify-center">
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
            onClick={expand}
            className="self-start font-sans text-[14px] font-semibold text-white
              bg-white/15 border border-white/30 rounded-full px-8 py-3
              cursor-pointer hover:bg-white/25 transition-all duration-200"
          >
            Get started →
          </button>
        </div>

        {/* Resume fan — right column, taller container */}
        <div className="flex-1 relative h-[min(680px,85vh)] min-w-0">
          <ResumeCard card={CARDS[0]} exitLeft={expanded} />
          <ResumeCard card={CARDS[1]} />
          <ResumeCard card={CARDS[2]} exitRight={expanded} />
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════
          OPEN STATE
      ════════════════════════════════════════════════════════════════ */}

      {/* Editorial left — open state, NO extra brand logo here */}
      <div
        className={`absolute inset-y-0 left-0 flex flex-col justify-center px-12 z-10
          w-[54%] transition-opacity duration-350 ease-in-out
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
          bg-[#2d3b28] transition-[width] duration-650 ease-in-out
          ${expanded ? "w-[46%]" : "w-0"} overflow-hidden`}
      >
        <div
          className={`w-[min(400px,88%)] bg-white rounded-xl shadow-2xl px-9 py-8 flex flex-col
            transition-opacity duration-300 ${expanded ? "delay-500 opacity-100" : "opacity-0"}`}
        >
          <AuthForm
            onSuccess={() => navigate("/library")}
            onSignInClick={() => navigate("/login")}
          />
        </div>
      </div>
    </div>
  );
}
