import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { AlertCircle, Bot, Filter, LayoutDashboard, Loader2, LogOut, Plus, RefreshCw, Search, Settings, Store, Users2, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface Automation {
  id: number;
  name: string;
  description: string;
  category: string;
  automation_type: 'crewai' | 'n8n_workflow';
  tags?: string[];
  estimated_duration?: string;
  difficulty?: string;
  integrations?: string[];
  node_count?: number;
  is_active?: boolean;
  folder_name?: string;
  missing_credentials?: string[];
}

const StorePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // States (using v1's unified automations array)
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'crews' | 'workflows'>('crews');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [userIntegrations, setUserIntegrations] = useState<Record<string, any>>({});

  // Navigation (from v2)
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Store', href: '/store', icon: Store },
    { name: 'My Teams & agents', href: '/my-teams', icon: Users2 },
    { name: 'External Integrations', href: '/integrations', icon: Settings },
  ];

  // Fetch automations (v1's logic)
  const fetchAutomations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/store/automations', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setAutomations(data.automations || []);
    } catch (err: any) {
      setError(err.message);
      toast.error('Failed to load automations');
    } finally {
      setIsLoading(false);
    }
  };

  // Sync all (v2's feature)
  const handleSyncAll = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/store/sync-all', {
        method: 'POST',
      });
      toast.success('All resources synced successfully!');
      await fetchAutomations();
    } catch (err) {
      toast.error('Sync failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Add to My Teams (for crews - v1's logic)
  const addCrewToMyTeams = async (crewId: number, crewName: string) => {
    try {
      const response = await fetch('http://localhost:8000/my-teams/add-crew', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ crew_id: crewId }),
      });
      toast.success(`✅ "${crewName}" added to your teams!`);
    } catch (err) {
      toast.error('Failed to add crew');
    }
  };

  // Add to My Teams (for workflows - NEW)
  const addWorkflowToMyTeams = async (workflowId: number, workflowName: string) => {
    try {
      const response = await fetch('http://localhost:8000/my-teams/add-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ workflow_id: workflowId }),
      });
      toast.success(`✅ "${workflowName}" added to your workflows!`);
    } catch (err) {
      toast.error('Failed to add workflow. Check required integrations.');
    }
  };

  // Clone workflow template (NOUVEAU)
  const cloneWorkflowTemplate = async (templateName: string, workflowName: string) => {
    try {
      // Récupérer les informations du workflow pour vérifier les services requis
      const workflow = automations.find(auto => auto.folder_name === templateName);
      const requiredServices = workflow?.required_services || [];
      
      let credentialMap: Record<string, number> = {};
      
      // Si le workflow nécessite des intégrations, récupérer les credentials
      if (requiredServices.length > 0) {
        const credsResponse = await fetch('http://localhost:8000/integrations/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!credsResponse.ok) {
          throw new Error('Failed to fetch user credentials');
        }
        
        const credsData = await credsResponse.json();
        
        // Mapper les credentials disponibles
        for (const integration of credsData) {
          if (integration.is_configured) {
            credentialMap[integration.service_name] = integration.id || 1;
          }
        }
        
        // Vérifier que nous avons les credentials requis
        const missingServices = requiredServices.filter(service => !credentialMap[service]);
        
        if (missingServices.length > 0) {
          toast.error(`Missing credentials for: ${missingServices.join(', ')}. Please configure them in External Integrations.`);
          navigate('/integrations');
          return;
        }
      }
      
      // Cloner le workflow
      const cloneResponse = await fetch(`http://localhost:8000/store/workflows/${templateName}/clone`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          userId: user?.id,
          credentials: credentialMap
        }),
      });
      
      if (!cloneResponse.ok) {
        const errorData = await cloneResponse.json();
        throw new Error(errorData.detail || 'Failed to clone workflow');
      }
      
      const result = await cloneResponse.json();
      
      toast.success(`✅ "${workflowName}" cloned and added to your workflows!`);
      
      // Rediriger vers MyTeams après clonage réussi
      navigate('/my-teams');
      
    } catch (err: any) {
      console.error('Clone error:', err);
      toast.error(err.message || 'Failed to clone workflow. Check required integrations.');
    }
  };
   const handleLogout = () => {
    logout(); // From useAuth()
    toast.success('Successfully logged out');
    navigate('/');
  };

  // Filter automations (v2's search/category + v1's type)
  const filteredAutomations = automations.filter((auto) => {
    const matchesSearch = auto.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         auto.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || auto.category === selectedCategory;
    const matchesTab = activeTab === 'crews' ? auto.automation_type === 'crewai' : auto.automation_type === 'n8n_workflow';
    return matchesSearch && matchesCategory && matchesTab;
  });

  const fetchUserIntegrations = async () => {
    try {
      const response = await fetch('http://localhost:8000/integrations/integrations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const integrations = await response.json();
        const integrationsMap = integrations.reduce((acc: any, integration: any) => {
          acc[integration.service_name] = integration;
          return acc;
        }, {});
        setUserIntegrations(integrationsMap);
      }
    } catch (error) {
      console.error('Error fetching user integrations:', error);
    }
  };

  useEffect(() => {
    fetchAutomations();
    fetchUserIntegrations();
  }, []);

  // Navigation and UI (v2's layout)
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
        {/* Header (unchanged from v2) */}
        <header className="border-b border-border">
          {/* ... (same as v2) ... */}
        </header>

        {/* Main content */}
        <main className="flex-1 px-6 py-8">
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-2">Available Resources</h2>
            <p className="text-muted-foreground">
              Choose from AI agent teams and automation workflows
            </p>
          </div>

          {/* Filters (v2's search + category) */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search resources..."
                  className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {/* Dynamically populate categories */}
                  {Array.from(new Set(automations.map(a => a.category))).map((cat) => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Tabs (v2's UI) */}
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'crews' | 'workflows')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="crews" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                AI Teams ({automations.filter(a => a.automation_type === 'crewai').length})
              </TabsTrigger>
              <TabsTrigger value="workflows" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Workflows ({automations.filter(a => a.automation_type === 'n8n_workflow').length})
              </TabsTrigger>
            </TabsList>

            {/* Loading/Error states (v2's style) */}
            {isLoading && (
              <div className="flex items-center justify-center py-12 mt-6">
                <Loader2 className="h-8 w-8 animate-spin mr-3" />
                <span className="text-lg">Loading resources...</span>
              </div>
            )}

            {error && !isLoading && (
              <div className="flex items-center justify-center py-12 mt-6">
                <div className="text-center">
                  <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Error loading resources</h3>
                  <p className="text-muted-foreground mb-4">{error}</p>
                  <Button onClick={fetchAutomations}>Retry</Button>
                </div>
              </div>
            )}

            {/* Crews Tab */}
            <TabsContent value="crews" className="mt-6">
              {!isLoading && !error && (
                <>
                  {filteredAutomations.filter(a => a.automation_type === 'crewai').length === 0 ? (
                    <div className="text-center py-12">
                      <h3 className="text-lg font-semibold mb-2">No teams found</h3>
                      <p className="text-muted-foreground">
                        {searchTerm || selectedCategory !== 'all' 
                          ? 'Try adjusting your search or filter criteria.'
                          : 'No AI teams available.'
                        }
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredAutomations
                        .filter(a => a.automation_type === 'crewai')
                        .map((crew) => (
                          <Card key={`crew-${crew.id}`} className="hover:shadow-md transition-shadow">
                            <CardHeader>
                              <div className="flex items-center justify-between">
                                <CardTitle className="text-lg">{crew.name}</CardTitle>
                                <Badge variant="secondary">{crew.category}</Badge>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <CardDescription className="mb-4">{crew.description}</CardDescription>
                              {crew.tags?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mb-3">
                                  {crew.tags.slice(0, 3).map((tag) => (
                                    <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                                  ))}
                                </div>
                              )}
                              <Button 
                                className="w-full" 
                                onClick={() => addCrewToMyTeams(crew.id, crew.name)}
                              >
                                <Plus className="h-4 w-4 mr-2" /> Add to My Teams
                              </Button>
                            </CardContent>
                          </Card>
                        ))}
                    </div>
                  )}
                </>
              )}
            </TabsContent>

            {/* Workflows Tab */}
            <TabsContent value="workflows" className="mt-6">
              {!isLoading && !error && (
                <>
                  {filteredAutomations.filter(a => a.automation_type === 'n8n_workflow').length === 0 ? (
                    <div className="text-center py-12">
                      <h3 className="text-lg font-semibold mb-2">No workflows found</h3>
                      <p className="text-muted-foreground mb-4">
                        {searchTerm || selectedCategory !== 'all' 
                          ? 'Try adjusting your search or filter criteria.'
                          : 'No workflows available. Sync to load workflows.'
                        }
                      </p>
                      <Button onClick={handleSyncAll}>
                        <RefreshCw className="h-4 w-4 mr-2" /> Sync Workflows
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredAutomations
                        .filter(a => a.automation_type === 'n8n_workflow')
                        .map((workflow) => (
                          <Card key={`workflow-${workflow.id}`} className="hover:shadow-md transition-shadow">
                            <CardHeader>
                              <div className="flex items-center justify-between">
                                <CardTitle className="text-lg">{workflow.name}</CardTitle>
                                <div className="flex gap-2">
                                  <Badge variant="secondary">{workflow.category}</Badge>
                                  <Badge variant="outline">{workflow.node_count} nodes</Badge>
                                </div>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <CardDescription className="mb-4">{workflow.description}</CardDescription>
                              {workflow.integrations?.length > 0 && (
                                <div className="mb-3">
                                  <p className="text-sm font-medium mb-2">Required integrations:</p>
                                  <div className="flex flex-wrap gap-1">
                                    {workflow.integrations.slice(0, 3).map((integration) => {
                                      const userIntegration = userIntegrations[integration];
                                      const isConfigured = userIntegration?.is_configured;
                                      const isConnected = userIntegration?.status === 'connected';
                                      
                                      return (
                                        <Badge 
                                          key={integration} 
                                          variant={isConnected ? "default" : isConfigured ? "secondary" : "outline"}
                                          className={cn(
                                            "text-xs",
                                            isConnected && "bg-green-100 text-green-800 border-green-300",
                                            isConfigured && !isConnected && "bg-yellow-100 text-yellow-800 border-yellow-300",
                                            !isConfigured && "bg-red-100 text-red-800 border-red-300"
                                          )}
                                        >
                                          {isConnected ? '✅' : isConfigured ? '⚠️' : '❌'} {integration}
                                        </Badge>
                                      );
                                    })}
                                  </div>
                                  {workflow.integrations.some((integration: string) => !userIntegrations[integration]?.is_configured) && (
                                    <p className="text-xs text-orange-600 mt-1">
                                      Missing integrations. <button 
                                        onClick={() => navigate('/integrations')}
                                        className="underline hover:no-underline"
                                      >
                                        Configure here
                                      </button>
                                    </p>
                                  )}
                                </div>
                              )}
                              <Button 
                                className="w-full" 
                                onClick={() => cloneWorkflowTemplate(workflow.folder_name, workflow.name)}
                                disabled={!workflow.is_active || (workflow.missing_credentials?.length ?? 0) > 0}
                              >
                                <Plus className="h-4 w-4 mr-2" /> 
                                {workflow.is_active ? 'Clone Workflow' : 'Workflow Inactive'}
                              </Button>
                              {(workflow.missing_credentials?.length ?? 0) > 0 && (
                                <p className="text-xs text-orange-600 mt-2 text-center">
                                  ⚠️ Missing credentials: {workflow.missing_credentials?.join(', ')}
                                </p>
                              )}
                            </CardContent>
                          </Card>
                        ))}
                    </div>
                  )}
                </>
              )}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
};

export default StorePage;