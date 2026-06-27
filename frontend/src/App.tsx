import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";

import { LibraryView } from "./views/LibraryView";
import { TemplatesView } from "./views/TemplatesView";
import { LandingView } from "./views/LandingView";
import { AuthView } from "./views/AuthView";
import { ShareView } from "./views/ShareView";
import ApiKeysPage from "./views/ApiKeyPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingView />} />
        <Route path="/login" element={<AuthView />} />
        <Route path="/share/:token" element={<ShareView />} />

        {/* App shell (authenticated) */}
        <Route element={<AppLayout />}>
          <Route path="/analyze" element={null} />
          <Route path="/library" element={<LibraryView />} />
          <Route path="/templates" element={<TemplatesView />} />
          <Route path="/apikeys" element={<ApiKeysPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
