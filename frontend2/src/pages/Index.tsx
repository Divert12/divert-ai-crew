
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import Features from '@/components/Features';
import Testimonials from '@/components/Testimonials';
import Pricing from '@/components/Pricing';
import Footer from '@/components/Footer';

const Index = () => {
  const { isLoggedIn, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Attendre que l'auth soit chargée avant de rediriger
    if (!isLoading) {
      if (isLoggedIn) {
        // Utilisateur connecté -> rediriger vers dashboard
        navigate('/dashboard', { replace: true });
      }
      // Utilisateur non connecté -> rester sur la page d'accueil
    }
  }, [isLoggedIn, isLoading, navigate]);

  // Pendant le chargement de l'auth, afficher un loader
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Si l'utilisateur est connecté, ne pas afficher la page d'accueil
  // (il sera redirigé vers dashboard)
  if (isLoggedIn) {
    return null;
  }

  // Afficher la page d'accueil pour les utilisateurs non connectés
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Header />
      <main>
        <HeroSection />
        <Features />
        <Testimonials />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}; 

export default Index;
