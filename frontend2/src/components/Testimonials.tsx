
const RevolutionaryImpact = () => {
  const impacts = [
    {
      quote: "Divert.ai reduced our operational workload by 75%. What used to take our team 40 hours per week now runs automatically. This is the future of work - and it's happening today.",
      author: "Alexandre Dubois",
      position: "CEO at InnovaTech Europe",
      avatar: "bg-cosmic-light/30"
    },
    {
      quote: "From Clermont-Ferrand to global impact - Divert.ai's collaborative agents solved problems we thought impossible. They're not just automating tasks, they're revolutionizing entire workflows.",
      author: "Maria Gonzalez",
      position: "Head of Digital Transformation at EuroSoft",
      avatar: "bg-cosmic-light/20"
    },
    {
      quote: "This MVP is a game-changer. Our partnership with Divert.ai has given us a competitive edge that seemed impossible just months ago. Ready to join this revolution.",
      author: "Thomas Müller",
      position: "Innovation Director at TechVision AG",
      avatar: "bg-cosmic-light/40"
    }
  ];

  return (
    <section className="w-full py-20 px-6 md:px-12 bg-card relative overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 cosmic-grid opacity-20"></div>
      
      {/* Animated background elements */}
      <div className="absolute top-10 left-10 w-32 h-32 bg-primary/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-10 right-10 w-48 h-48 bg-primary/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <div className="max-w-7xl mx-auto space-y-16 relative z-10">
        <div className="text-center space-y-6 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/20 bg-primary/5 text-primary text-sm font-medium">
            🚀 Revolutionary MVP from Clermont-Ferrand
          </div>
          
          <h2 className="text-3xl md:text-5xl font-bold tracking-tighter text-foreground">
            Transforming Work, 
            <span className="text-primary block md:inline"> One Agent at a Time</span>
          </h2>
          
          <p className="text-muted-foreground text-xl leading-relaxed">
            Join the revolution that's reducing human work hours by up to 75%. 
            <br className="hidden md:block" />
            <strong className="text-foreground">Partner with us</strong> and be part of the future we're building together.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <button className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-all duration-300 transform hover:scale-105">
              Join Our Mission
            </button>
            <button className="px-8 py-3 border border-primary text-primary rounded-lg font-semibold hover:bg-primary/5 transition-all duration-300">
              Partner With Us
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {impacts.map((impact, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl border border-border bg-background/80 backdrop-blur-sm hover:border-primary/40 transition-all duration-500 transform hover:scale-105 hover:shadow-2xl"
            >
              {/* Impact indicator */}
              <div className="flex items-center gap-2 mb-6">
                <div className="flex">
                  {[...Array(5)].map((_, i) => (
                    <span key={i} className="text-primary inline-block mr-1 text-lg group-hover:animate-pulse">★</span>
                  ))}
                </div>
                <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded-full">
                  REVOLUTIONARY
                </span>
              </div>
              
              <p className="text-lg mb-8 text-foreground/90 italic leading-relaxed">
                "{impact.quote}"
              </p>
              
              <div className="flex items-center gap-4">
                <div className={`h-14 w-14 rounded-full ${impact.avatar} bg-muted relative overflow-hidden group-hover:scale-110 transition-transform duration-300`}>
                  <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent"></div>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                    {impact.author}
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {impact.position}
                  </p>
                </div>
              </div>
              
              {/* Collaboration call-to-action */}
              <div className="mt-6 pt-6 border-t border-border/50">
                <p className="text-xs text-muted-foreground text-center">
                  Ready to collaborate? <span className="text-primary font-semibold cursor-pointer hover:underline">Let's connect</span>
                </p>
              </div>
            </div>
          ))}
        </div>
        
        {/* Bottom CTA section */}
        <div className="text-center space-y-6 pt-12">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              Ready to Reduce Your Team's Workload by 75%?
            </h3>
            <p className="text-muted-foreground text-lg mb-6">
              Join forward-thinking companies collaborating with our Clermont-Ferrand team to revolutionize work as we know it.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-4 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground rounded-xl font-bold text-lg hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                Start Your Revolution
              </button>
              <button className="px-8 py-4 border-2 border-primary text-primary rounded-xl font-bold text-lg hover:bg-primary/5 transition-all duration-300">
                Schedule Partnership Call
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RevolutionaryImpact;