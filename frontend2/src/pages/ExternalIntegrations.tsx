import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  ExternalLink, 
  Eye, 
  EyeOff, 
  LayoutDashboard, 
  Link2, 
  Loader2, 
  LogOut, 
  Mail, 
  MessageSquare, 
  Plus, 
  Settings, 
  Shield, 
  Store, 
  Trash2, 
  Users2, 
  Zap,
  HardDrive,
  FileSpreadsheet,
  Bot
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface Integration {
  service_name: string;
  display_name: string;
  service_type: string;
  fields: Array<{
    name: string;
    type: string;
    required: boolean;
    description: string;
  }>;
  instructions: string;
  status: string;
  is_configured: boolean;
  configured_at?: string;
  icon: string;
}

interface FormData {
  [key: string]: string;
}

const getServiceIcon = (serviceName: string) => {
  const iconMap: Record<string, React.ComponentType<any>> = {
    telegram: MessageSquare,
    discord: MessageSquare,
    slack: MessageSquare,
    gmail: Mail,
    google_drive: HardDrive,
    google_sheets: FileSpreadsheet,
    openai: Bot,
    twitter: MessageSquare,
    facebook: MessageSquare,
    instagram: MessageSquare,
    linkedin: MessageSquare,
    youtube: MessageSquare,
    notion: FileSpreadsheet,
    airtable: FileSpreadsheet,
    zapier: Zap,
    hubspot: Users2,
    salesforce: Users2,
    stripe: Bot,
    paypal: Bot,
    shopify: Store,
    aws: HardDrive,
    azure: HardDrive,
    gcp: HardDrive
  };
  
  return iconMap[serviceName] || Link2;
};

const getServiceColor = (serviceName: string, status: string) => {
  if (status === 'connected') return 'bg-green-500';
  if (status === 'error') return 'bg-red-500';
  
  const colorMap: Record<string, string> = {
    telegram: 'bg-blue-500',
    discord: 'bg-indigo-600',
    slack: 'bg-green-600',
    gmail: 'bg-red-500',
    google_drive: 'bg-yellow-500',
    google_sheets: 'bg-green-500',
    openai: 'bg-gray-800',
    twitter: 'bg-blue-400',
    facebook: 'bg-blue-600',
    instagram: 'bg-pink-500',
    linkedin: 'bg-blue-700',
    youtube: 'bg-red-600',
    notion: 'bg-gray-900',
    airtable: 'bg-orange-500',
    zapier: 'bg-orange-600',
    hubspot: 'bg-orange-500',
    salesforce: 'bg-blue-500',
    stripe: 'bg-purple-600',
    paypal: 'bg-blue-600',
    shopify: 'bg-green-600',
    aws: 'bg-orange-500',
    azure: 'bg-blue-600',
    gcp: 'bg-blue-500'
  };
  
  return colorMap[serviceName] || 'bg-gray-500';
};

const ExternalIntegrations = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [formData, setFormData] = useState<FormData>({});
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testingService, setTestingService] = useState<string | null>(null);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Store', href: '/store', icon: Store },
    { name: 'My Teams & agents', href: '/my-teams', icon: Users2 },
    { name: 'External Integrations', href: '/integrations', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    toast.success('Successfully logged out');
    navigate('/');
  };

  const fetchIntegrations = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      
      let response;
      if (token) {
        // Try authenticated endpoint first
        response = await fetch('http://localhost:8000/integrations/integrations', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        // If authentication fails, fall back to public templates
        if (response.status === 401) {
          console.log('Authentication failed, falling back to public templates');
          response = await fetch('http://localhost:8000/integrations/templates', {
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }
      } else {
        // No token, use public endpoint
        response = await fetch('http://localhost:8000/integrations/templates', {
          headers: {
            'Content-Type': 'application/json',
          },
        });
      }

      if (!response.ok) {
        throw new Error('Failed to fetch integrations');
      }

      const data = await response.json();
      setIntegrations(data);
    } catch (error) {
      console.error('Error fetching integrations:', error);
      toast.error('Failed to load integrations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfigureIntegration = async (integration: Integration) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please log in to configure integrations');
      navigate('/login');
      return;
    }
    
    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/integrations/configure', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_name: integration.service_name,
          credentials: formData,
        }),
      });

      if (response.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
        return;
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to configure integration');
      }

      const result = await response.json();
      toast.success(result.message);
      
      // Reset form and close dialog
      setFormData({});
      setSelectedIntegration(null);
      
      // Refresh integrations
      await fetchIntegrations();
    } catch (error: any) {
      console.error('Error configuring integration:', error);
      toast.error(error.message || 'Failed to configure integration');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTestIntegration = async (serviceName: string) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please log in to test integrations');
      navigate('/login');
      return;
    }
    
    setTestingService(serviceName);
    try {
      const response = await fetch(`http://localhost:8000/integrations/${serviceName}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error('Test failed');
      }

      const result = await response.json();
      toast.success(result.message);
      
      // Refresh integrations
      await fetchIntegrations();
    } catch (error: any) {
      console.error('Error testing integration:', error);
      toast.error(error.message || 'Test failed');
    } finally {
      setTestingService(null);
    }
  };

  const handleRemoveIntegration = async (serviceName: string) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please log in to remove integrations');
      navigate('/login');
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/integrations/${serviceName}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to remove integration');
      }

      const result = await response.json();
      toast.success(result.message);
      
      // Refresh integrations
      await fetchIntegrations();
    } catch (error: any) {
      console.error('Error removing integration:', error);
      toast.error(error.message || 'Failed to remove integration');
    }
  };

  const handleInputChange = (fieldName: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const togglePasswordVisibility = (fieldName: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const openConfigDialog = (integration: Integration) => {
    setSelectedIntegration(integration);
    // Initialize form with empty values
    const initialData: FormData = {};
    integration.fields.forEach(field => {
      initialData[field.name] = '';
    });
    setFormData(initialData);
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const ConfigurationDialog = () => {
    if (!selectedIntegration) return null;

    return (
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className={`h-12 w-12 rounded-lg ${getServiceColor(selectedIntegration.service_name, selectedIntegration.status)} flex items-center justify-center`}>
              {(() => {
                const Icon = getServiceIcon(selectedIntegration.service_name);
                return <Icon className="h-6 w-6 text-white" />;
              })()}
            </div>
            <div>
              <h2 className="text-2xl font-bold">Configure {selectedIntegration.display_name}</h2>
              <DialogDescription className="text-base mt-1">
                Set up your {selectedIntegration.display_name} integration
              </DialogDescription>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <ExternalLink className="h-4 w-4" />
              Setup Instructions
            </h3>
            <div className="text-sm text-blue-800 whitespace-pre-line">
              {selectedIntegration.instructions}
            </div>
          </div>

          {/* Form Fields */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Configuration</h3>
            
            {selectedIntegration.fields.map((field) => (
              <div key={field.name} className="space-y-2">
                <Label htmlFor={field.name} className="flex items-center gap-2">
                  {field.description}
                  {field.required && <span className="text-red-500">*</span>}
                </Label>
                
                {field.type === 'textarea' ? (
                  <Textarea
                    id={field.name}
                    placeholder={field.description}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    required={field.required}
                    rows={4}
                  />
                ) : (
                  <div className="relative">
                    <Input
                      id={field.name}
                      type={field.type === 'password' && !showPasswords[field.name] ? 'password' : 'text'}
                      placeholder={field.description}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      required={field.required}
                    />
                    {field.type === 'password' && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => togglePasswordVisibility(field.name)}
                      >
                        {showPasswords[field.name] ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                  </div>
                )}
                
                <p className="text-xs text-gray-500">{field.description}</p>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={() => setSelectedIntegration(null)}
              variant="outline"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={() => handleConfigureIntegration(selectedIntegration)}
              disabled={isSubmitting || !selectedIntegration.fields.filter(f => f.required).every(f => formData[f.name])}
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Configuring...
                </>
              ) : (
                <>
                  <Shield className="mr-2 h-4 w-4" />
                  Configure Integration
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    );
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-border bg-background px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
            <h1 className="text-xl font-bold">Divert.ai</h1>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={cn(
                            location.pathname === item.href
                              ? 'bg-accent text-accent-foreground'
                              : 'text-muted-foreground hover:text-foreground hover:bg-accent/50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium'
                          )}
                        >
                          <Icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                          {item.name}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </li>
              <li className="mt-auto">
                <Button variant="ghost" className="w-full justify-start" onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72 flex flex-col flex-1">
        {/* Header */}
        <header className="border-b border-border">
          <div className="h-16 flex items-center gap-x-4 px-6 lg:px-8">
            <div className="flex flex-1 items-center justify-between">
              <h1 className="text-2xl font-bold text-foreground">External Integrations</h1>
              <div className="flex items-center gap-3">
                {/* Clean header without refresh button and welcome text */}
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 px-6 py-8">
          <div className="mb-8 text-center">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Connect Your Favorite Services</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-2">
              🚀 <strong>Unlock the Power of Automation!</strong> Connect 20+ popular platforms in seconds and watch your productivity soar.
            </p>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From Gmail to Google Drive, Slack to Shopify - all your tools working together seamlessly. Military-grade encryption keeps your data safe.
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Connected</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {integrations.filter(i => i.status === 'connected').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Clock className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Pending</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {integrations.filter(i => i.status === 'not_configured').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Errors</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {integrations.filter(i => i.status === 'error').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Integrations Grid */}
          <div className="space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center p-8">
                <div className="text-muted-foreground flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading integrations...
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {integrations.map((integration) => {
                  const Icon = getServiceIcon(integration.service_name);
                  
                  return (
                    <Card key={integration.service_name} className="hover:shadow-lg transition-all duration-200 hover:scale-105 border-2 hover:border-primary/20">
                      <CardHeader className="pb-3">
                        <div className="flex flex-col items-center text-center">
                          <div className={`h-16 w-16 rounded-2xl ${getServiceColor(integration.service_name, integration.status)} flex items-center justify-center mb-3 shadow-lg`}>
                            <Icon className="h-8 w-8 text-white" />
                          </div>
                          <CardTitle className="text-lg font-bold">{integration.display_name}</CardTitle>
                          <Badge 
                            variant={integration.status === 'connected' ? 'default' : 
                                    integration.status === 'error' ? 'destructive' : 'secondary'}
                            className="mt-2"
                          >
                            {integration.status === 'connected' ? '✅ Connected' :
                             integration.status === 'error' ? '❌ Error' : '⚪ Not Configured'}
                          </Badge>
                        </div>
                      </CardHeader>
                      
                      <CardContent className="pt-0">
                        <div className="text-center mb-4">
                          <p className="text-sm text-muted-foreground mb-2">
                            {integration.service_type === 'oauth' ? '🔐 OAuth2 Integration' :
                             integration.service_type === 'api_key' ? '🔑 API Key Integration' :
                             integration.service_type === 'service_account' ? '👤 Service Account' : 
                             '🔗 Integration'}
                          </p>
                          
                          {integration.configured_at && (
                            <p className="text-xs text-gray-500">
                              Configured: {new Date(integration.configured_at).toLocaleDateString()}
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          {integration.is_configured ? (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleTestIntegration(integration.service_name)}
                                disabled={testingService === integration.service_name}
                                className="w-full"
                              >
                                {testingService === integration.service_name ? (
                                  <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Testing...
                                  </>
                                ) : (
                                  <>
                                    <Zap className="mr-2 h-4 w-4" />
                                    Test Connection
                                  </>
                                )}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleRemoveIntegration(integration.service_name)}
                                className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Remove
                              </Button>
                            </>
                          ) : (
                            localStorage.getItem('access_token') ? (
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button 
                                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
                                    onClick={() => openConfigDialog(integration)}
                                  >
                                    <Plus className="mr-2 h-4 w-4" />
                                    Connect Now
                                  </Button>
                                </DialogTrigger>
                                <ConfigurationDialog />
                              </Dialog>
                            ) : (
                              <Button 
                                className="w-full bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg"
                                onClick={() => {
                                  toast.info('Please log in to configure integrations');
                                  navigate('/login');
                                }}
                              >
                                <Plus className="mr-2 h-4 w-4" />
                                Log in to Connect
                              </Button>
                            )
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ExternalIntegrations;