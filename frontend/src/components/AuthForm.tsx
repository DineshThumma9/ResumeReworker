import { useState } from "react";
import { GoogleIcon } from "./GoogleIcon";
import { authApi } from "../apis/auth";
import { useAuthStore } from "../store/authStore";

export function AuthForm({
  onSuccess,
  initialMode = "signup",
}: {
  onSuccess: (mode: "signin" | "signup") => void;
  initialMode?: "signin" | "signup";
}) {
  const [mode, setMode] = useState<"signin" | "signup">(initialMode);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "signup") {
        const res = await authApi.signup(name, email, password);
        useAuthStore.getState().setToken(res.access_token);
      } else {
        const res = await authApi.login(email, password);
        useAuthStore.getState().setToken(res.access_token);
      }
      onSuccess(mode);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const displayName = mode === "signup" ? (name.trim() || "John Doe") : "Welcome Back";
  const displayEmail = email.trim() || "john.doe@email.com";

  const fields = mode === "signup"
    ? [
        { lbl: "Full Name", type: "text", ph: "Dinesh Thumma", val: name, set: setName },
        { lbl: "Email", type: "email", ph: "you@example.com", val: email, set: setEmail },
        { lbl: "Password", type: "password", ph: "At least 8 characters", val: password, set: setPassword },
      ]
    : [
        { lbl: "Email", type: "email", ph: "you@example.com", val: email, set: setEmail },
        { lbl: "Password", type: "password", ph: "••••••••", val: password, set: setPassword },
      ];

  return (
    <form onSubmit={handleSubmit} className="contents">
      <div className="font-['EB_Garamond'] text-[22px] font-semibold tracking-wider uppercase text-[#1a1a1a] text-center">
        {displayName}
      </div>
      <div className="font-sans text-[10px] text-[#999] text-center mt-1 mb-4">
        {displayEmail}
        <span className="text-[#ccc] mx-1.5">|</span>
        {mode === "signup" ? "Create your account" : "Sign in to continue"}
      </div>
      <hr className="border-t-[1.5px] border-[#1a1a1a] mb-4" />

      <div className="font-['EB_Garamond'] text-[10px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-3">
        Account Details
      </div>

      {fields.map((f) => (
        <div key={f.lbl} className="flex items-baseline gap-2 mb-4">
          <div className="font-['EB_Garamond'] text-[15px] font-medium text-[#1a1a1a] whitespace-nowrap w-[90px]">
            {f.lbl}
          </div>
          <div className="font-['EB_Garamond'] text-[15px] text-[#ccc] shrink-0">
            :
          </div>
          <input
            type={f.type}
            placeholder={f.ph}
            value={f.val}
            onChange={(e) => f.set(e.target.value)}
            required
            className="font-sans text-[13px] border-0 border-b border-[#d0ccc8] bg-transparent text-[#1a1a1a]
              placeholder:text-[#c0bcb8] placeholder:text-[11px] py-1 outline-none w-full
              focus:border-[#607456] transition-colors duration-150"
          />
        </div>
      ))}

      {error && (
        <div className="text-red-500 text-[11px] text-center mb-2 font-sans">{error}</div>
      )}

      <hr className="border-t-[0.5px] border-[#e8e8e8] my-3" />

      <div className="font-['EB_Garamond'] text-[10px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-3">
        Continue With
      </div>
      <div className="flex items-center gap-2 mb-1">
        <div className="font-['EB_Garamond'] text-[15px] font-medium text-[#1a1a1a] w-[90px]">
          Auth
        </div>
        <div className="font-['EB_Garamond'] text-[15px] text-[#ccc] shrink-0">
          :
        </div>
        <button
          type="button"
          onClick={() => {
            window.location.href = authApi.googleLoginUrl();
          }}
          className="font-sans text-[12px] text-[#333] flex items-center gap-2
            border border-[#d8d4d0] rounded px-3 py-1.5 cursor-pointer bg-[#f9f8f6]
            hover:bg-[#efe9e0] transition-colors duration-150"
        >
          <GoogleIcon />
          Google
        </button>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-5 w-full bg-transparent text-[#1a1a1a] font-['EB_Garamond'] text-[14px] font-medium
          tracking-widest uppercase border-[1.5px] border-[#1a1a1a] rounded py-3 cursor-pointer
          hover:bg-[#607456] hover:text-white hover:border-[#607456] transition-all duration-150 disabled:opacity-50"
      >
        {loading ? "Loading..." : (mode === "signup" ? "Submit Application" : "Sign In")}
      </button>

      <p className="font-sans text-[9px] text-[#ccc] text-center mt-4 leading-[1.7]">
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
    </form>
  );
}
