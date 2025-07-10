import { Button } from '@/components/ui/button';

const Pricing = () => {
  const plans = [
    {
      name: "Starter",
      price: "Free",
      description: "Perfect for small teams discovering AI agent automation",
      features: [
        "Up to 3 active teams/agents",
        "Access to basic agent store",
        "Standard dashboard monitoring",
        "Email support",
        "Community templates",
        "Basic workflow automation"
      ],
      buttonText: "Get Started",
      buttonVariant: "outline",
      buttonLink: "/login",
      popular: false
    },
    {
      name: "Professional",
      price: "Coming Soon",
      period: "",
      description: "Advanced features for growing businesses scaling their automation",
      features: [
        "Up to 25 active teams/agents",
        "Premium agent marketplace access",
        "Real-time collaboration monitoring",
        "Advanced workflow builder",
        "Priority support",
        "Custom integrations",
        "Performance analytics"
      ],
      buttonText: "Not Available",
      buttonVariant: "disabled",
      buttonLink: "#",
      popular: true,
      comingSoon: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "Tailored AI agent solutions with dedicated development and support",
      features: [
        "Unlimited custom agents & teams",
        "Dedicated agent development",
        "Local LLM integration",
        "Enhanced security & compliance",
        "White-label solutions",
        "Dedicated account manager",
        "24/7 premium support",
        "On-premise deployment options"
      ],
      buttonText: "Get Custom Team",
      buttonVariant: "outline",
      buttonLink: "/custom-team",
      popular: false
    }
  ];
  
  const handleButtonClick = (link, disabled = false) => {
    if (disabled) return;
    if (link.startsWith('/')) {
      // Internal navigation - in a real app you'd use router
      window.location.href = link;
    } else if (link === '#') {
      return;
    }
  };
  
  return (
    <section id="pricing" className="w-full py-20 px-6 md:px-12 bg-background">
      <div className="max-w-7xl mx-auto space-y-16">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-medium tracking-tighter text-foreground">
            Choose Your AI Automation Journey
          </h2>
          <p className="text-muted-foreground text-lg">
            From free exploration to enterprise-grade custom solutions
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div 
              key={index}
              className={`p-6 rounded-xl border flex flex-col h-full ${
                plan.popular 
                  ? "border-primary/50 cosmic-glow bg-card" 
                  : "border-border cosmic-gradient bg-card"
              } transition-all duration-300 relative ${
                plan.comingSoon ? "opacity-90" : ""
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground text-sm rounded-full font-medium">
                  Most Requested
                </div>
              )}
              
              {plan.comingSoon && (
                <div className="absolute -top-4 right-4 px-3 py-1 bg-muted-foreground text-muted text-xs rounded-full font-medium">
                  Coming Soon
                </div>
              )}
              
              <div className="mb-auto">
                <h3 className="text-2xl font-medium tracking-tighter mb-1 text-foreground">{plan.name}</h3>
                
                <div className="mb-4">
                  <div className={`text-3xl font-bold tracking-tighter ${
                    plan.comingSoon ? "text-muted-foreground" : "text-foreground"
                  }`}>
                    {plan.price}
                  </div>
                  {plan.period && <div className="text-sm text-muted-foreground">{plan.period}</div>}
                </div>
                
                <p className="text-muted-foreground mb-6">{plan.description}</p>
                
                <div className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className={`h-5 w-5 rounded-full flex items-center justify-center ${
                        plan.comingSoon 
                          ? "bg-muted-foreground/20 text-muted-foreground" 
                          : "bg-primary/20 text-primary"
                      }`}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M5 12L10 17L19 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <span className={`text-sm ${
                        plan.comingSoon ? "text-muted-foreground" : "text-foreground"
                      }`}>
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="mt-6">
                <Button 
                  className={
                    plan.buttonVariant === "default" 
                      ? "w-full bg-primary text-primary-foreground hover:bg-primary/90" 
                      : plan.buttonVariant === "disabled"
                      ? "w-full bg-muted text-muted-foreground cursor-not-allowed"
                      : "w-full border-border text-foreground hover:bg-muted"
                  }
                  variant={plan.buttonVariant === "disabled" ? "outline" : plan.buttonVariant as "default" | "outline"}
                  disabled={plan.buttonVariant === "disabled"}
                  onClick={() => handleButtonClick(plan.buttonLink, plan.buttonVariant === "disabled")}
                >
                  {plan.buttonText}
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center space-y-4">
          <div className="text-muted-foreground">
            Have questions about custom solutions? 
            <button 
              onClick={() => handleButtonClick("/custom-team")}
              className="text-primary hover:underline ml-1 cursor-pointer"
            >
              Contact our AI specialists
            </button>
          </div>
          <div className="text-sm text-muted-foreground">
            🚀 All plans include access to our revolutionary no-code agent builder
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;