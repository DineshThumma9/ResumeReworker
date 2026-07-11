import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BrandLogo } from "../components/BrandLogo";
import { GoogleIcon } from "../components/GoogleIcon";

import { authApi } from "../apis/auth";
import { useAuthStore } from "../store/authStore";

type Mode = "signin" | "signup";

export function AuthView() {
  const [mode, setMode] = useState<Mode>("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (code) {
      setLoading(true);
      authApi
        .googleExchange(code)
        .then((res) => {
          useAuthStore.getState().setToken(res.access_token);
          navigate("/analyze");
        })
        .catch((err) => {
          setError(
            err instanceof Error ? err.message : "Google authentication failed"
          );
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "signup") {
        const res = await authApi.signup(name, email, password);
        useAuthStore.getState().setToken(res.access_token);
        navigate("/analyze");
      } else {
        const res = await authApi.login(email, password);
        useAuthStore.getState().setToken(res.access_token);
        navigate("/analyze");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const signupFields = [
    {
      lbl: "Full Name",
      type: "text",
      ph: "Dinesh Thumma",
      value: name,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setName(e.target.value),
    },
    {
      lbl: "Email",
      type: "email",
      ph: "you@example.com",
      value: email,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setEmail(e.target.value),
    },
    {
      lbl: "Password",
      type: "password",
      ph: "At least 8 characters",
      value: password,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setPassword(e.target.value),
    },
  ];
  const signinFields = [
    {
      lbl: "Email",
      type: "email",
      ph: "you@example.com",
      value: email,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setEmail(e.target.value),
    },
    {
      lbl: "Password",
      type: "password",
      ph: "••••••••",
      value: password,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setPassword(e.target.value),
    },
  ];
  const fields = mode === "signup" ? signupFields : signinFields;

  const displayName =
    mode === "signup" ? name.trim() || "John Doe" : "Welcome Back";
  const displayEmail = email.trim() || "john.doe@email.com";

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row">
      {/* ── LEFT — editorial green, left-aligned like LandingView ────── */}
      <div className="relative flex-1 bg-[#607456] flex flex-col justify-center px-12 py-20 overflow-hidden text-left z-10">
        {/* blobs */}
        <div className="pointer-events-none absolute top-[-15%] right-[-8%] w-[40vw] h-[40vw] rounded-full bg-white/6" />
        <div className="pointer-events-none absolute bottom-[-12%] left-[15%] w-[25vw] h-[25vw] rounded-full bg-white/4" />

        {/* Brand lockup — top left */}
        <div className="absolute top-8 left-10">
          <BrandLogo />
        </div>

        {/* Headline — left aligned */}
        <h1 className="font-heading text-[clamp(2.8rem,5vw,4.6rem)] leading-[1.04] text-white mb-5 z-10">
          Your résumé,
          <br />
          <em className="not-italic text-[#b8d4a4]">rewritten</em>
          <br />
          for the role.
        </h1>

        {/* Subtitle — left aligned */}
        <p className="font-sans text-[15px] text-white/55 leading-[1.8] mb-10 max-w-[380px] z-10">
          Paste a job description. Get a tailored resume and ATS fit score in
          under 30 seconds.
        </p>

        {/* Stat cards */}
        <div className="flex gap-4 z-10 w-full max-w-[460px]">
          {[
            { val: "30", unit: "s", lbl: "Avg rewrite time" },
            { val: "∞", unit: "", lbl: "Roles you can tailor" },
            { val: "0", unit: "$", lbl: "To get started" },
          ].map((s) => (
            <div
              key={s.lbl}
              className="flex-1 bg-white/9 border border-white/15 rounded-xl px-4 py-4"
            >
              <div className="font-heading text-[clamp(1.6rem,2.5vw,2.2rem)] text-white leading-none mb-1">
                {s.val}
                <em className="not-italic text-[#b8d4a4]">{s.unit}</em>
              </div>
              <div className="font-sans text-[11px] text-white/45 leading-[1.45]">
                {s.lbl}
              </div>
            </div>
          ))}
        </div>

        <p className="font-sans text-[11px] text-white/28 mt-7 z-10">
          Anonymous · No data stored
        </p>
      </div>

      {/* ── RIGHT — dark auth panel ───────────────────────────────────── */}
      <div className="w-full md:w-[480px] lg:w-[520px] xl:w-[560px] bg-[#2d3b28] flex items-center justify-center px-10 py-16 md:py-0">
        <div className="w-full max-w-[480px] bg-white rounded-xl shadow-2xl px-10 py-9 flex flex-col">
          {/* Resume-style header */}
          <div className="font-['EB_Garamond'] text-[22px] font-semibold tracking-wider uppercase text-[#1a1a1a] text-center">
            {displayName}
          </div>
          <div className="font-sans text-[10px] text-[#999] text-center mt-1.5 mb-4">
            {displayEmail}
            <span className="text-[#ccc] mx-2">|</span>
            {mode === "signup" ? "Create your account" : "Sign in to continue"}
          </div>
          <hr className="border-t-[1.5px] border-[#1a1a1a] mb-5" />

          <form onSubmit={handleSubmit} className="flex flex-col">
            <div className="font-['EB_Garamond'] text-[10px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-4">
              Account Details
            </div>

            {fields.map((f) => (
              <div key={f.lbl} className="flex items-baseline gap-2 mb-5">
                <div className="font-['EB_Garamond'] text-[16px] font-medium text-[#1a1a1a] whitespace-nowrap w-[90px]">
                  {f.lbl}
                </div>
                <div className="font-['EB_Garamond'] text-[16px] text-[#ccc] shrink-0">
                  :
                </div>
                <input
                  type={f.type}
                  placeholder={f.ph}
                  value={f.value}
                  onChange={f.onChange}
                  required
                  className="font-sans text-[14px] border-0 border-b border-[#d0ccc8] bg-transparent text-[#1a1a1a]
                    placeholder:text-[#c0bcb8] placeholder:text-[12px] py-1.5 outline-none w-full
                    focus:border-[#607456] transition-colors duration-150"
                />
              </div>
            ))}

            {error && (
              <div className="text-red-500 text-xs text-center mt-2 font-sans">
                {error}
              </div>
            )}

            <hr className="border-t-[0.5px] border-[#e8e8e8] my-4" />

            <div className="font-['EB_Garamond'] text-[10px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-4">
              Continue With
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="font-['EB_Garamond'] text-[16px] font-medium text-[#1a1a1a] w-[90px]">
                Auth
              </div>
              <div className="font-['EB_Garamond'] text-[16px] text-[#ccc] shrink-0">
                :
              </div>
              <button
                type="button"
                onClick={() => {
                  window.location.href = authApi.googleLoginUrl();
                }}
                className="font-sans text-[13px] text-[#333] flex items-center gap-2
                  border border-[#d8d4d0] rounded px-4 py-2 cursor-pointer bg-[#f9f8f6]
                  hover:bg-[#efe9e0] transition-colors duration-150"
              >
                <GoogleIcon />
                Google
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full bg-transparent text-[#1a1a1a] font-['EB_Garamond'] text-[15px] font-medium
                tracking-widest uppercase border-[1.5px] border-[#1a1a1a] rounded py-3.5 cursor-pointer
                hover:bg-[#607456] hover:text-white hover:border-[#607456] transition-all duration-150 disabled:opacity-50"
            >
              {loading
                ? "Loading..."
                : mode === "signup"
                  ? "Submit Application"
                  : "Sign In"}
            </button>
          </form>

          <p className="font-sans text-[9px] text-[#ccc] text-center mt-5 leading-[1.7]">
            {mode === "signup" ? (
              <>
                By signing up, you agree to the{" "}
                <a href="#" className="text-[#8aaa78] hover:underline">
                  Terms
                </a>{" "}
                and{" "}
                <a href="#" className="text-[#8aaa78] hover:underline">
                  Privacy Policy
                </a>
                .
                <br />
                We never store passwords in plain text.
              </>
            ) : (
              <>
                Forgot your password?{" "}
                <a href="#" className="text-[#8aaa78] hover:underline">
                  Reset it here
                </a>
                .
              </>
            )}
          </p>

          <p className="font-sans text-[11px] text-[#aaa] text-center mt-2">
            {mode === "signup" ? (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => setMode("signin")}
                  className="text-[#607456] font-medium bg-transparent border-0 cursor-pointer p-0
                    underline underline-offset-2 text-[11px] hover:text-[#4a5c38] transition-colors"
                >
                  Sign in
                </button>
              </>
            ) : (
              <>
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => setMode("signup")}
                  className="text-[#607456] font-medium bg-transparent border-0 cursor-pointer p-0
                    underline underline-offset-2 text-[11px] hover:text-[#4a5c38] transition-colors"
                >
                  Sign up
                </button>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
