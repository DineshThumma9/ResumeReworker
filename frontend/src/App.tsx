import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";

import { LibraryView } from "./views/LibraryView";
import { TemplatesView } from "./views/TemplatesView";
import { LandingView } from "./views/LandingView";
import { ProfileView } from "./views/ProfileView";
import { ShareView } from "./views/ShareView";
import ApiKeysPage from "./views/ApiKeyPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingView />} />
        <Route path="/login" element={<LandingView startMode="signin" />} />
        <Route path="/share/:token" element={<ShareView />} />

        {/* App shell (authenticated) */}
        <Route element={<AppLayout />}>
          <Route path="/analyze" element={null} />
          <Route path="/library" element={<LibraryView />} />
          <Route path="/templates" element={<TemplatesView />} />
          <Route path="/apikeys" element={<ApiKeysPage />} />
          <Route path="/profile" element={<ProfileView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
