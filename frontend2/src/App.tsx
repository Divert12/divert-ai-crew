import ProtectedRoute from "@/components/ProtectedRoute";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import CustomTeam from "./pages/CustomTeam";
import Dashboard from "./pages/Dashboard";
import ExternalIntegrations from "./pages/ExternalIntegrations";
import Index from "./pages/Index";
import Login from "./pages/Login";
import MyTeams from "./pages/MyTeams";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";
import Store from "./pages/store";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/custom-team" element={<CustomTeam />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/store" element={<Store />} />
            <Route path="/my-teams" element={
              <ProtectedRoute>
                <MyTeams />
              </ProtectedRoute>
            } />
            <Route path="/integrations" element={<ExternalIntegrations />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
