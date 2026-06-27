import { create } from "zustand";

interface ResumeState {
  resumeId: number | null;
  latexCode: string;
  pdfUrl: string | null;
  label: string;
  templateId: string;
  setResumeState: (state: Partial<ResumeState>) => void;
  resetResumeState: () => void;
}

const initialState = {
  resumeId: null,
  latexCode: "",
  pdfUrl: null,
  label: "",
  templateId: "",
};

export const useResumeStore = create<ResumeState>((set) => ({
  ...initialState,
  setResumeState: (state) => set((prev) => ({ ...prev, ...state })),
  resetResumeState: () => set(initialState),
}));
