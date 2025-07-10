
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { BookOpen, ChevronDown, Grid3x3, Layers, LayoutDashboard, ListCheck, Star } from "lucide-react";
import { useState } from 'react';

const Features = () => {
  const [openFeature, setOpenFeature] = useState<number | null>(null);
  
  const features = [
    {
      title: "Agent Collaboration",
      description: "Multi-agent teams that work together to solve complex business challenges and automate end-to-end workflows.",
      expandedDescription: "Deploy intelligent agent crews that communicate and coordinate to handle multi-step processes. Configure role-based collaboration where agents specialize in different tasks while sharing context and outcomes. Enable dynamic workflow orchestration with automated handoffs, real-time decision making, and adaptive problem-solving capabilities that scale with your business complexity.",
      icon: (
        <Layers size={24} className="text-cosmic-accent" />
      )
    },
    {
      title: "Real-time Monitoring",
      description: "Track agent performance with live dashboards and comprehensive reporting on task completion and efficiency.",
      expandedDescription: "Monitor your AI workforce through comprehensive dashboards that display active crews, task progress, and performance metrics in real-time. Set up automated alerts for workflow bottlenecks, configure performance thresholds, and access detailed analytics on agent efficiency. Generate executive reports with KPI tracking and ROI calculations to measure automation impact across your organization.",
      icon: (
        <Grid3x3 size={24} className="text-cosmic-accent" />
      )
    },
    {
      title: "Custom Development",
      description: "Tailored AI agents designed specifically for your business needs with enhanced security and performance.",
      expandedDescription: "Build enterprise-grade agents customized to your exact specifications with our B2B development services. Implement advanced security protocols, optimize performance for your specific use cases, and integrate proprietary business logic. Benefit from faster processing speeds, enhanced reliability, and dedicated support with SLA guarantees designed for mission-critical operations.",
      icon: (
        <LayoutDashboard size={24} className="text-cosmic-accent" />
      )
    },
    {
      title: "Local LLM Integration",
      description: "Deploy agents with your proprietary language models for complete data sovereignty and control.",
      expandedDescription: "Maintain full control over your data with on-premise LLM deployment options. Integrate your fine-tuned models, proprietary datasets, and custom knowledge bases while ensuring data never leaves your infrastructure. Configure hybrid architectures that balance performance with security, enabling compliant AI operations for regulated industries and sensitive business processes.",
      icon: (
        <ListCheck size={24} className="text-cosmic-accent" />
      )
    },
    {
      title: "Marketplace Access",
      description: "Ready-to-use agents from our curated store for immediate deployment and productivity gains.",
      expandedDescription: "Browse our extensive marketplace of pre-built agents covering marketing automation, customer service, data analysis, and operational workflows. Deploy agents instantly to your 'My Teams & Agents' workspace with one-click installation. Access community-contributed solutions, enterprise-verified agents, and industry-specific templates that reduce time-to-value from months to minutes.",
      icon: (
        <Star size={24} className="text-cosmic-accent" />
      )
    },
    {
      title: "No-Code Simplicity",
      description: "Create powerful AI agents without technical expertise - designed for everyone, from beginners to experts.",
      expandedDescription: "Unlike complex AI platforms that require coding skills and technical knowledge, Divert.ai democratizes AI automation for all user levels. Deploy sophisticated agents through intuitive drag-and-drop interfaces, pre-configured templates, and guided setup wizards. Business users can create custom workflows without developers, while IT teams maintain control over security and governance. Experience the power of enterprise-grade AI automation with the simplicity of everyday software - no programming, no complicated configurations, just results.",
      icon: (
        <BookOpen size={24} className="text-cosmic-accent" />
      )
    }
  ];
  
  const toggleFeature = (index: number) => {
    setOpenFeature(openFeature === index ? null : index);
  };
  
  return (
    <section id="features" className="w-full py-12 md:py-16 px-6 md:px-12">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-medium tracking-tighter">
            Everything your business needs to automate
          </h2>
          <p className="text-cosmic-muted text-lg">
            Comprehensive AI agent solutions to streamline your operations and accelerate growth
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Collapsible
              key={index}
              open={openFeature === index}
              onOpenChange={() => toggleFeature(index)}
              className={`rounded-xl border ${openFeature === index ? 'border-cosmic-light/40' : 'border-cosmic-light/20'} cosmic-gradient transition-all duration-300`}
            >
              <CollapsibleTrigger className="w-full text-left p-6 flex flex-col">
                <div className="flex justify-between items-start">
                  <div className="h-16 w-16 rounded-full bg-cosmic-light/10 flex items-center justify-center mb-6">
                    {feature.icon}
                  </div>
                  <ChevronDown
                    className={`h-5 w-5 text-cosmic-muted transition-transform duration-200 ${
                      openFeature === index ? 'rotate-180' : ''
                    }`}
                  />
                </div>
                <h3 className="text-xl font-medium tracking-tighter mb-3">{feature.title}</h3>
                <p className="text-cosmic-muted">{feature.description}</p>
              </CollapsibleTrigger>
              <CollapsibleContent className="px-6 pb-6 pt-2">
                <div className="pt-3 border-t border-cosmic-light/10">
                  <p className="text-cosmic-muted">{feature.expandedDescription}</p>
                  <div className="mt-4 flex justify-end">
                    <button className="text-cosmic-accent hover:text-cosmic-accent/80 text-sm font-medium">
                      Learn more →
                    </button>
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
