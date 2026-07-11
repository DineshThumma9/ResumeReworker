import { fetchJSON, API_URL } from "./api";
import { useAuthStore } from "../store/authStore";

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
    return `${API_URL}/auth/google`;
  },
  googleExchange: async (code: string) => {
    return await fetchJSON("/auth/google/exchange", {
      method: "POST",
      body: JSON.stringify({ code }),
    }) as { access_token: string; token_type: string; new: boolean };
  },
  getProfile: async (): Promise<UserProfile> => {
    return await fetchJSON("/auth/profile");
  },
  updateProfile: async (
    profile: Omit<UserProfile, "id" | "username">,
  ): Promise<UserProfile> => {
    return await fetchJSON("/auth/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    });
  },
  autofillProfile: async (
    file: File,
  ): Promise<{
    name: string;
    phone: string;
    location: string;
    github: string;
    linkedin: string;
    website: string;
    sections: any;
  }> => {
    const token = useAuthStore.getState().token;
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_URL}/auth/profile/autofill`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      let msg = res.statusText;
      try {
        const errData = await res.json();
        if (errData.detail) {
          msg =
            typeof errData.detail === "string"
              ? errData.detail
              : JSON.stringify(errData.detail);
        }
      } catch (e) {}
      throw new Error(msg || "Failed to autofill profile");
    }
    return res.json();
  },
};

export interface UserProfile {
  id: number;
  username: string;
  name: string;
  email: string;
  github?: string | null;
  linkedin?: string | null;
  website?: string | null;
  location?: string | null;
  phone?: string | null;
  raw_resume?: string | null;
}
