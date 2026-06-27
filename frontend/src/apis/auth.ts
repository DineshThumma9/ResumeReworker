import { fetchJSON } from "./api";

export const authApi = {
  signup: async (name: string, email: string, password: string) => {
    // Basic username extraction
    const username = email.split("@")[0] + Math.floor(Math.random() * 10000);
    const raw = await fetchJSON("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, name, email, password }),
    });
    return raw as { access_token: string; token_type: string };
  },
  login: async (email: string, password: string) => {
    const raw = await fetchJSON("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email_or_username: email, password }),
    });
    return raw as { access_token: string; token_type: string };
  },
  logout: async () => {
    await fetchJSON("/auth/logout", {
      method: "POST",
    });
  },
  googleLoginUrl: () => {
    return "http://localhost:8000/api/auth/google";
  },
};
