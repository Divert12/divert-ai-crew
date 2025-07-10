
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import Spline from '@splinetool/react-spline';
import { Briefcase, Loader, Mic, Users } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TaskBoard from './TaskBoard';

const HeroSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const { isLoggedIn, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  const handleGetStarted = () => {
    if (isLoading) return;
    
    if (isLoggedIn) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  const handleCustomTeam = () => {
    navigate('/custom-team');
  };

  return (
    <section className="relative w-full py-12 md:py-20 px-6 md:px-12 flex flex-col items-center justify-center overflow-hidden bg-background">
      {/* Cosmic particle effect (background dots) */}
      <div className="absolute inset-0 cosmic-grid opacity-30"></div>
      
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full">
        <div className="w-full h-full opacity-10 bg-primary blur-[120px]"></div>
      </div>

      {/* 3D Character Integration - Moved up to top-[16%] */}
      <div className="absolute top-[22%] left-1/2 -translate-x-1/2 w-full h-[400px] opacity-70 z-5">
        <Spline scene="https://prod.spline.design/CAZhLjC8kMG483An/scene.splinecode" />
      </div>
      
      <div className={`relative z-10 max-w-4xl text-center space-y-6 transition-all duration-700 transform ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <div className="flex justify-center">
          <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-muted text-primary">
            <span className="flex h-2 w-2 rounded-full bg-primary"></span>
            AI-Powered Agent Teams
            <Loader className="h-3 w-3 animate-spin text-primary" />
          </span>
        </div>
        
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-medium tracking-tighter text-balance text-foreground">
  Stop Working <span className="text-primary">Harder</span>, Start Working <span className="text-primary">Smarter</span>
</h1>

<p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
  Transform 40-hour workweeks into 10-hour results. Our AI agent teams execute complex workflows while you focus on what truly matters - growing your business.
</p>
        
        {/* Buttons positioned with significantly more space */}
        <div className="flex flex-col sm:flex-row gap-24 justify-center pt-20 items-center mt-20">
          <Button 
            onClick={handleGetStarted}
            disabled={isLoading}
            className="bg-primary text-primary-foreground hover:bg-primary/80 hover:text-primary-foreground text-base h-12 px-8 transition-all duration-200 min-h-[48px]"
          >
            {isLoading ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : isLoggedIn ? (
              'Go to Dashboard'
            ) : (
              'Get Started Free'
            )}
          </Button>
          <Button 
            variant="outline" 
            onClick={handleCustomTeam}
            className="border-border text-foreground hover:bg-accent hover:text-accent-foreground text-base h-12 px-8 transition-all duration-200 min-h-[48px]"
          >
            Get Custom Team
          </Button>
        </div>
      </div>
      
      {/* AI Agent Dashboard UI - Changed top margin to mt-38 */}
      <div className={`w-full max-w-7xl mt-32 z-10 transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-20'}`}>
        <div className="cosmic-glow relative rounded-xl overflow-hidden border border-border backdrop-blur-sm bg-card shadow-lg">
          <div className="bg-card backdrop-blur-md w-full">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-4">
                <div className="h-8 w-8 rounded-md bg-muted flex items-center justify-center">
                  <div className="h-3 w-3 rounded-sm bg-foreground"></div>
                </div>
                <span className="text-foreground font-medium">AI Agent Teams Dashboard</span>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex -space-x-2">
                  <div className="h-8 w-8 rounded-full bg-green-500 border-2 border-card flex items-center justify-center text-xs text-white">VA</div>
                  <div className="h-8 w-8 rounded-full bg-blue-500 border-2 border-card flex items-center justify-center text-xs text-white">MK</div>
                  <div className="h-8 w-8 rounded-full bg-purple-500 border-2 border-card flex items-center justify-center text-xs text-white">JF</div>
                  <div className="h-8 w-8 rounded-full bg-muted border-2 border-card flex items-center justify-center text-xs text-foreground">+12</div>
                </div>
                
                <div className="h-8 px-3 rounded-md bg-muted flex items-center justify-center text-foreground text-sm">
                  My Teams
                </div>
              </div>
            </div>
            
            <div className="flex h-[600px] overflow-hidden">
              <div className="w-64 border-r border-border p-4 space-y-4 hidden md:block bg-card">
                <div className="space-y-2">
                  <div className="text-xs text-muted-foreground uppercase">Navigation</div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md bg-muted text-foreground">
                      <div className="h-3 w-3 rounded-sm bg-foreground"></div>
                      <span>Dashboard</span>
                    </div>
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <div className="h-3 w-3 rounded-sm bg-muted-foreground/30"></div>
                      <span>Agent Store</span>
                    </div>
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <div className="h-3 w-3 rounded-sm bg-muted-foreground/30"></div>
                      <span>My Teams</span>
                    </div>
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <div className="h-3 w-3 rounded-sm bg-muted-foreground/30"></div>
                      <span>Analytics</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2 pt-4">
                  <div className="text-xs text-muted-foreground uppercase">Available Teams</div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <Mic className="h-3 w-3 text-green-500" />
                      <span>Voice Assistant</span>
                    </div>
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <Users className="h-3 w-3 text-blue-500" />
                      <span>Marketing Team</span>
                    </div>
                    <div className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-muted/50">
                      <Briefcase className="h-3 w-3 text-purple-500" />
                      <span>Job Finder Team</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex-1 p-4 bg-background overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-card p-4 rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Mic className="h-4 w-4 text-green-500" />
                      <div className="text-sm font-medium text-foreground">Voice Assistant</div>
                    </div>
                    <div className="text-xs text-muted-foreground">AI-powered voice interactions, natural conversation handling, and voice command processing for seamless user experience.</div>
                  </div>
                  <div className="bg-card p-4 rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="h-4 w-4 text-blue-500" />
                      <div className="text-sm font-medium text-foreground">Marketing Team</div>
                    </div>
                    <div className="text-xs text-muted-foreground">Complete marketing automation with content creation, social media management, and campaign optimization agents.</div>
                  </div>
                  <div className="bg-card p-4 rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Briefcase className="h-4 w-4 text-purple-500" />
                      <div className="text-sm font-medium text-foreground">Job Finder Team</div>
                    </div>
                    <div className="text-xs text-muted-foreground">Intelligent job matching, resume optimization, and interview preparation with personalized career guidance.</div>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-6 min-w-0">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <h3 className="font-medium text-foreground">Active Agent Teams</h3>
                    <span className="text-xs bg-muted px-2 py-1 rounded-full text-muted-foreground">3 Running</span>
                  </div>
                  
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="h-8 px-3 rounded-md bg-foreground text-background flex items-center justify-center text-sm font-medium whitespace-nowrap">
                      Add Agent Team
                    </div>
                  </div>
                </div>
                
                <div className="overflow-hidden">
                  <TaskBoard />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
