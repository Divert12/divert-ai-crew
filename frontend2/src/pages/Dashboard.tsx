import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { apiService, TeamInstance } from '@/services/api';
import { CheckCircle, Clock, LayoutDashboard, LogOut, Plus, Settings, Store, TrendingUp, Users, Users2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';


const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [teams, setTeams] = useState<TeamInstance[]>([]);
  const [isLoadingTeams, setIsLoadingTeams] = useState(true);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: ' Store', href: '/store', icon: Store },
    { name: 'My Teams & agents', href: '/my-teams', icon: Users2 },
    { name: 'External Integrations', href: '/integrations', icon: Settings }
  ];

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const userTeams = await apiService.getMyTeams();
        setTeams(userTeams);
      } catch (error) {
        console.error('Error fetching teams:', error);
        toast.error('Failed to fetch your teams');
      } finally {
        setIsLoadingTeams(false);
      }
    };

    fetchTeams();
  }, []);

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
              <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
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

        <main className="flex-1 px-6 py-8">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Teams</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{teams.filter(team => team.is_active).length}</div>
                <p className="text-xs text-muted-foreground">Teams working</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Teams</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{teams.length}</div>
                <p className="text-xs text-muted-foreground">All teams</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0h</div>
                <p className="text-xs text-muted-foreground">+0% from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Efficiency</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0%</div>
                <p className="text-xs text-muted-foreground">+0% improvement</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* My Teams */}
            <Card>
              <CardHeader>
                <CardTitle>My Teams</CardTitle>
                <CardDescription>Your active AI agent teams</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingTeams ? (
                  <div className="flex items-center justify-center p-8">
                    <div className="text-muted-foreground">Loading your teams...</div>
                  </div>
                ) : teams.length === 0 ? (
                  <div className="text-center p-8">
                    <p className="text-muted-foreground mb-4">You don't have any teams yet.</p>
                    <Button variant="outline" onClick={() => navigate('/store')}>
                  <Plus size={16} className="mr-2" />
                  Add for Free
                </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {teams.map((team, index) => (
                      <div key={team.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`h-10 w-10 rounded-full ${getTeamColor(index)} flex items-center justify-center text-white font-medium`}>
                            {getTeamInitials(team.custom_name || (team.type === 'crew' ? team.crew?.name : team.workflow?.name) || 'Unknown')}
                          </div>
                          <div>
                            <h4 className="font-medium">{team.custom_name || (team.type === 'crew' ? team.crew?.name : team.workflow?.name) || 'Unknown'}</h4>
                            <p className="text-sm text-muted-foreground">
                              {team.type === 'crew' ? team.crew?.category : team.workflow?.category || 'Workflow'} • {team.is_active ? 'Active' : 'Inactive'}
                            </p>
                          </div>
                        </div>
                        <Button variant="outline" size="sm">Manage</Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest updates from your AI teams</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {teams.slice(0, 4).map((team, index) => (
                    <div key={team.id} className="flex items-start gap-3 pb-3 border-b border-border last:border-b-0">
                      <div className={`h-2 w-2 rounded-full ${getTeamColor(index)} mt-2`}></div>
                      <div className="flex-1">
                        <p className="text-sm">{team.custom_name || (team.type === 'crew' ? team.crew?.name : team.workflow?.name) || 'Unknown'} is ready for tasks</p>
                        <p className="text-xs text-muted-foreground">
                          Created {new Date(team.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {teams.length === 0 && (
                    <div className="text-center p-4 text-muted-foreground">
                      No recent activity to show
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
