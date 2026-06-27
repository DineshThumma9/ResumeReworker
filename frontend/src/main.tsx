import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "./App.css";
import App from "./App.tsx";
import { ThemeProvider } from "./components/theme-provider.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider
      attribute="class" // applies `class="dark"` to <html>
      defaultTheme="system" // respects OS preference on first load
      enableSystem // re-syncs when OS preference changes
      disableTransitionOnChange // prevents flash during switch
    >
      <App />
    </ThemeProvider>
  </StrictMode>,
);
