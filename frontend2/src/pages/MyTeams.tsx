import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { apiService, TeamInstance } from '@/services/api';
import {
  Calendar,
  CheckCircle,
  Clock,
  LayoutDashboard,
  Loader2,
  LogOut,
  Play,
  Plus,
  Settings,
  Store,
  Tag,
  Trash2,
  Users2,
  XCircle
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface ExecutionResult {
  success: boolean;
  message: string;
  data?: any;
  team_name?: string;
  error?: string;
}

interface ExecutionState {
  isRunning: boolean;
  result: ExecutionResult | null;
  topic: string;
}

const MyTeams = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [teams, setTeams] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState<any | null>(null);
  const [executionStates, setExecutionStates] = useState<{[key: string]: ExecutionState}>({});

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

  const getTeamInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getTeamColor = (index: number) => {
    const colors = ['bg-green-500', 'bg-blue-500', 'bg-purple-500', 'bg-orange-500', 'bg-pink-500'];
    return colors[index % colors.length];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const updateExecutionState = (teamId: string, updates: Partial<ExecutionState>) => {
    setExecutionStates(prev => ({
      ...prev,
      [teamId]: { ...prev[teamId], ...updates }
    }));
  };

  const handleRunTeam = async (team: any) => {
    const teamId = team.id.toString();
    const currentState = executionStates[teamId];
    
    if (team.type === 'crew' && !currentState?.topic?.trim()) {
      toast.error('Please enter a topic for the execution');
      return;
    }

    updateExecutionState(teamId, { isRunning: true, result: null });

    try {
      if (team.type === 'crew') {
        const result = await apiService.runTeamInstance(team.id, { topic: currentState.topic });
        
        updateExecutionState(teamId, { 
          isRunning: false, 
          result: result 
        });

        toast.success(`Team "${team.name || team.crew.name}" executed successfully!`);
      } else if (team.type === 'workflow') {
        // Exécuter le workflow
        const workflowResult = await fetch(`http://localhost:8000/workflows/${team.id}/execute`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (workflowResult.ok) {
          const result = await workflowResult.json();
          updateExecutionState(teamId, { 
            isRunning: false, 
            result: {
              success: true,
              message: 'Workflow executed successfully',
              data: result.result
            }
          });
          toast.success(`Workflow "${team.name || team.workflow.name}" executed successfully!`);
        } else {
          const errorResult = {
            success: false,
            message: 'Workflow execution failed',
            error: 'Failed to execute workflow'
          };
          updateExecutionState(teamId, { 
            isRunning: false, 
            result: errorResult 
          });
          toast.error('Workflow execution failed');
        }
      }
      
      // Refresh teams to update last_executed
      fetchTeams();
    } catch (error: any) {
      const errorResult: ExecutionResult = {
        success: false,
        message: error.message || 'Execution failed',
        error: error.message
      };
      
      updateExecutionState(teamId, { 
        isRunning: false, 
        result: errorResult 
      });

      toast.error(`Execution failed: ${error.message}`);
    }
  };

  const toggleWorkflowActive = async (workflowId: string, currentActive: boolean) => {
    try {
      const response = await fetch(`http://localhost:8000/workflows/${workflowId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ active: !currentActive })
      });

      if (response.ok) {
        toast.success(`Workflow ${!currentActive ? 'activated' : 'deactivated'} successfully`);
        // Refresh teams to show updated status
        fetchTeams();
      } else {
        toast.error('Failed to toggle workflow status');
      }
    } catch (error) {
      console.error('Error toggling workflow:', error);
      toast.error('Failed to toggle workflow status');
    }
  };

  const deleteClonedWorkflow = async (teamId: string, workflowName: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete the cloned workflow "${workflowName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/my-teams/${teamId}/delete-cloned-workflow`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message || 'Cloned workflow deleted successfully');
        // Refresh teams to remove the deleted workflow
        fetchTeams();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to delete cloned workflow');
      }
    } catch (error) {
      console.error('Error deleting cloned workflow:', error);
      toast.error('Failed to delete cloned workflow');
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await fetch('http://localhost:8000/my-teams/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      const userTeams = await response.json();
      setTeams(userTeams);
      
      // Initialize execution states for new teams ONLY if not exists
      setExecutionStates(prev => {
        const newStates = { ...prev };
        userTeams.forEach((team: any) => {
          const teamId = team.id.toString();
          if (!newStates[teamId]) {
            newStates[teamId] = {
              isRunning: false,
              result: null,
              topic: ''
            };
          }
        });
        return newStates;
      });
    } catch (error) {
      console.error('Error fetching teams:', error);
      toast.error('Failed to fetch your teams');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const TeamDetailModal = ({ team }: { team: any }) => {
    const teamId = team.id.toString();
    const executionState = executionStates[teamId] || { isRunning: false, result: null, topic: '' };

    const getTeamName = (team: any) => {
      if (team.type === 'crew') {
        return team.name || team.crew?.name || 'Unknown Team';
      } else if (team.type === 'workflow') {
        return team.name || team.workflow?.name || 'Unknown Workflow';
      }
      return 'Unknown Item';
    };

    const getTeamDescription = (team: any) => {
      if (team.type === 'crew') {
        return team.crew?.description || 'No description available';
      } else if (team.type === 'workflow') {
        return team.workflow?.description || 'No description available';
      }
      return 'No description available';
    };

    const getTeamCategory = (team: any) => {
      if (team.type === 'crew') {
        return team.crew?.category || 'General';
      } else if (team.type === 'workflow') {
        return team.workflow?.category || 'General';
      }
      return 'General';
    };

    return (
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className={`h-12 w-12 rounded-full ${getTeamColor(teams.indexOf(team))} flex items-center justify-center text-white font-medium`}>
              {getTeamInitials(getTeamName(team))}
            </div>
            <div>
              <h2 className="text-2xl font-bold">{getTeamName(team)}</h2>
              <DialogDescription className="text-base mt-1">
                {getTeamDescription(team)}
              </DialogDescription>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Team Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Team Details
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Type:</span>
                    <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-full">
                      {team.type === 'crew' ? 'AI Team' : 'Workflow'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Category:</span>
                    <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-full">
                      {getTeamCategory(team)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Status:</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      team.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {team.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Folder:</span>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {team.type === 'crew' ? team.crew?.folder_name : team.workflow?.folder_name}
                    </code>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Timeline
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Created:</span>
                    <span className="text-sm">{formatDate(team.created_at)}</span>
                  </div>
                  {team.last_executed && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Last run:</span>
                      <span className="text-sm">{formatDate(team.last_executed)}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6">
            {/* Execution Section */}
            <div className="space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Play className="h-4 w-4" />
                {team.type === 'crew' ? 'Run Team' : 'Run Workflow'}
              </h3>
              
              <div className="space-y-4">
                {team.type === 'crew' ? (
                  <div>
                    <Label htmlFor={`topic-${teamId}`}>Topic / Subject</Label>
                    <Textarea
                      id={`topic-${teamId}`}
                      placeholder="Enter the topic for your AI team to work on..."
                      value={executionState.topic || ''}
                      onChange={(e) => updateExecutionState(teamId, { topic: e.target.value })}
                      disabled={executionState.isRunning}
                      className="mt-1 min-h-[80px]"
                      rows={3}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Example: "Create a marketing strategy for a mobile fitness app"
                    </p>
                  </div>
                ) : (
                  <div>
                    <Label>Required Integrations</Label>
                    <div className="mt-2 space-y-2">
                      {team.workflow?.integrations?.length > 0 ? (
                        <div className="grid grid-cols-2 gap-2">
                          {team.workflow.integrations.map((integration: string) => (
                            <div key={integration} className="flex items-center gap-2 p-2 border rounded-lg">
                              <div className="h-2 w-2 rounded-full bg-green-500"></div>
                              <span className="text-sm font-medium">{integration}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">No specific integrations required</p>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      This workflow will use your configured integrations automatically
                    </p>
                  </div>
                )}

                <div className="flex gap-2">
                  <Button 
                    onClick={() => handleRunTeam(team)}
                    disabled={executionState.isRunning || (team.type === 'crew' && !executionState.topic?.trim())}
                    className="flex-1"
                  >
                    {executionState.isRunning ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {team.type === 'crew' ? 'Running Team...' : 'Running Workflow...'}
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        {team.type === 'crew' ? 'Run Team' : 'Run Workflow'}
                      </>
                    )}
                  </Button>
                  {team.type === 'workflow' && team.workflow?.category === 'Cloned' && (
                    <Button 
                      variant="destructive"
                      onClick={() => {
                        deleteClonedWorkflow(team.id, team.name || team.workflow?.name || 'Unknown');
                      }}
                      disabled={executionState.isRunning}
                      title="Delete cloned workflow permanently"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          {executionState.result && (
            <div className="border-t border-border pt-6">
              <div className="space-y-4">
                <h3 className="font-semibold flex items-center gap-2">
                  {executionState.result.success ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                  Execution Results
                </h3>
                
                <div className={`p-4 rounded-lg border ${
                  executionState.result.success 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Status:</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        executionState.result.success 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {executionState.result.success ? 'Success' : 'Failed'}
                      </span>
                    </div>
                    
                    <div>
                      <span className="font-medium">Message:</span>
                      <p className="mt-1 text-sm">{executionState.result.message}</p>
                    </div>

                    {executionState.result.success && executionState.result.data && (
                      <div>
                        <span className="font-medium">Output:</span>
                        <Textarea
                          value={typeof executionState.result.data === 'string' 
                            ? executionState.result.data 
                            : JSON.stringify(executionState.result.data, null, 2)
                          }
                          readOnly
                          rows={8}
                          className="mt-1 font-mono text-xs"
                        />
                      </div>
                    )}

                    {executionState.result.error && (
                      <div>
                        <span className="font-medium text-red-600">Error:</span>
                        <p className="mt-1 text-sm text-red-600">{executionState.result.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
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
              <h1 className="text-2xl font-bold text-foreground">My Teams & Workflows</h1>
              <div className="flex items-center gap-3">
                <Button 
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={() => navigate('/store')}
                >
                  <Plus size={16} className="mr-2" />
                  Add for Free
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 px-6 py-8">
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-2">Your AI Teams & Workflows</h2>
            <p className="text-muted-foreground">
              Manage and execute your AI teams and workflows. Click on any item to view details and run executions.
            </p>
          </div>

          <div className="space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center p-8">
                <div className="text-muted-foreground flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading your teams...
                </div>
              </div>
            ) : teams.length === 0 ? (
              <div className="text-center p-8">
                <div className="mb-4">
                  <Users2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground mb-2">You don't have any teams or workflows yet.</p>
                  <p className="text-sm text-muted-foreground">
                    Get started by adding your first AI team or workflow from the store.
                  </p>
                </div>
                <Button variant="outline" onClick={() => navigate('/store')}>
                  <Plus size={16} className="mr-2" />
                  Add for Free
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {teams.map((team, index) => {
                  const teamId = team.id.toString();
                  const executionState = executionStates[teamId];
                  
                  return (
                    <Dialog key={team.id}>
                      <DialogTrigger asChild>
                        <Card className="hover:shadow-lg transition-all cursor-pointer hover:scale-105 transform">
                          <CardHeader>
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`h-10 w-10 rounded-full ${getTeamColor(index)} flex items-center justify-center text-white font-medium`}>
                                {getTeamInitials(team.name || (team.type === 'crew' ? team.crew?.name : team.workflow?.name) || 'Unknown')}
                              </div>
                              <div className="flex-1">
                                <CardTitle className="text-lg">
                                  {team.name || (team.type === 'crew' ? team.crew?.name : team.workflow?.name) || 'Unknown'}
                                </CardTitle>
                                <div className="flex items-center gap-2 mt-1">
                                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                    {team.type === 'crew' ? 'AI Team' : 'Workflow'}
                                  </span>
                                  <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-full">
                                    {team.type === 'crew' ? team.crew?.category : team.workflow?.category}
                                  </span>
                                  {team.type === 'workflow' && team.workflow?.category === 'Cloned' && (
                                    <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                                      My Copy
                                    </span>
                                  )}
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    team.is_active 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {team.is_active ? 'Active' : 'Inactive'}
                                  </span>
                                  {executionState?.isRunning && (
                                    <span className="text-xs border border-border px-2 py-1 rounded-full">
                                      <Loader2 className="h-3 w-3 animate-spin mr-1 inline" />
                                      Running
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <CardDescription className="mb-4">
                              <div className="space-y-1">
                                <div>Created {new Date(team.created_at).toLocaleDateString()}</div>
                                {team.last_executed && (
                                  <div className="flex items-center gap-1 text-xs text-green-600">
                                    <Clock className="h-3 w-3" />
                                    Last run: {new Date(team.last_executed).toLocaleDateString()}
                                  </div>
                                )}
                              </div>
                            </CardDescription>
                            <div className="flex gap-2">
                              <Button variant="outline" size="sm" className="flex-1">
                                <Settings className="mr-1 h-3 w-3" />
                                View Details
                              </Button>
                              <Button 
                                variant="default" 
                                size="sm" 
                                className="flex-1"
                                disabled={executionState?.isRunning}
                              >
                                {executionState?.isRunning ? (
                                  <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                                ) : (
                                  <Play className="mr-1 h-3 w-3" />
                                )}
                                Run
                              </Button>
                              {team.type === 'workflow' && (
                                <Button 
                                  variant={team.is_active ? "secondary" : "outline"}
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleWorkflowActive(team.id, team.is_active);
                                  }}
                                  className="px-2"
                                  title={team.is_active ? "Deactivate workflow" : "Activate workflow"}
                                >
                                  {team.is_active ? '⏸️' : '▶️'}
                                </Button>
                              )}
                              {team.type === 'workflow' && team.workflow?.category === 'Cloned' && (
                                <Button 
                                  variant="destructive"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    deleteClonedWorkflow(team.id, team.name || team.workflow?.name || 'Unknown');
                                  }}
                                  className="px-2"
                                  title="Delete cloned workflow permanently"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      </DialogTrigger>
                      <TeamDetailModal team={team} />
                    </Dialog>
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

export default MyTeams;