
import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, Shield, Zap, Users, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const CustomTeam = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft size={20} />
            Back to Home
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            Get Your <span className="text-primary">Custom AI Team</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Tailored AI agents designed specifically for your business needs. 
            Enhanced security, reliability, and capability for complex enterprise tasks.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Features */}
          <div className="space-y-8">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-6">
                Why Choose Custom AI Teams?
              </h2>
              
              <div className="space-y-6">
                <div className="flex gap-4">
                  <Shield className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-2">Enterprise Security</h3>
                    <p className="text-muted-foreground">
                      Advanced security protocols, data encryption, and compliance with industry standards 
                      to protect your sensitive business information.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Zap className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-2">Enhanced Performance</h3>
                    <p className="text-muted-foreground">
                      Custom-trained agents optimized for your specific workflows, delivering superior 
                      performance and accuracy for complex business tasks.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Users className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-2">Dedicated Support</h3>
                    <p className="text-muted-foreground">
                      24/7 priority support, dedicated account management, and ongoing optimization 
                      to ensure your AI teams perform at their best.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-2">Full Customization</h3>
                    <p className="text-muted-foreground">
                      Agents tailored to your industry, processes, and requirements. Complete integration 
                      with your existing tools and workflows.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Pricing Tiers */}
            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-foreground">Custom Solutions</h3>
              <div className="grid gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Professional Team</CardTitle>
                    <CardDescription>Perfect for small to medium businesses</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">Starting at $2,999/month</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Up to 5 custom AI agents</li>
                      <li>• Basic integrations</li>
                      <li>• Standard support</li>
                    </ul>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle>Enterprise Team</CardTitle>
                    <CardDescription>For large organizations with complex needs</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">Custom Pricing</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Unlimited custom AI agents</li>
                      <li>• Advanced integrations</li>
                      <li>• 24/7 priority support</li>
                      <li>• Dedicated account manager</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>

          {/* Contact Form */}
          <Card>
            <CardHeader>
              <CardTitle>Request Your Custom AI Team</CardTitle>
              <CardDescription>
                Tell us about your needs and we'll create a tailored solution for you.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName">First Name</Label>
                    <Input id="firstName" placeholder="John" />
                  </div>
                  <div>
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input id="lastName" placeholder="Doe" />
                  </div>
                </div>

                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="john@company.com" />
                </div>

                <div>
                  <Label htmlFor="company">Company Name</Label>
                  <Input id="company" placeholder="Your Company Inc." />
                </div>

                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" placeholder="+1 (555) 123-4567" />
                </div>

                <div>
                  <Label htmlFor="teamSize">Team Size</Label>
                  <Input id="teamSize" placeholder="e.g., 10-50 employees" />
                </div>

                <div>
                  <Label htmlFor="industry">Industry</Label>
                  <Input id="industry" placeholder="e.g., Finance, Healthcare, Technology" />
                </div>

                <div>
                  <Label htmlFor="useCase">Describe Your Use Case</Label>
                  <Textarea 
                    id="useCase" 
                    placeholder="Tell us about your specific needs, challenges, and what you'd like your custom AI team to accomplish..."
                    rows={4}
                  />
                </div>

                <div>
                  <Label htmlFor="budget">Estimated Budget Range</Label>
                  <Input id="budget" placeholder="e.g., $5,000 - $15,000 per month" />
                </div>

                <div>
                  <Label htmlFor="timeline">Desired Timeline</Label>
                  <Input id="timeline" placeholder="e.g., Within 30 days" />
                </div>

                <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
                  Request Custom Quote
                </Button>

                <p className="text-sm text-muted-foreground text-center">
                  We'll respond within 24 hours with a detailed proposal tailored to your needs.
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CustomTeam;
