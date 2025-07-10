const API_BASE_URL = 'http://localhost:8000';

export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Crew {
  id: number;
  name: string;
  description: string;
  category: string;
  folder_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TeamInstance {
  id: string; // UUID as string
  user_id: number;
  crew_id: number;
  custom_name: string | null;
  is_active: boolean;
  last_executed: string | null;
  created_at: string;
  updated_at?: string;
  user: User;
  crew: Crew;
}

export interface CrewInput {
  topic: string;
}

export interface ExecutionResult {
  success: boolean;
  message: string;
  data?: any;
  team_name?: string;
  error?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description: string;
  folder_name: string;
  category: string;
  type: string;
  node_count: number;
  integrations: string[];
  required_credentials: string[];
  n8n_workflow_id?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Integration {
  service_name: string;
  display_name: string;
  service_type: string;
  fields: Array<{
    name: string;
    type: string;
    required: boolean;
    label: string;
    placeholder?: string;
  }>;
  instructions: string;
  status: string;
  is_configured: boolean;
  configured_at?: string;
  icon?: string;
}

export interface WorkflowExecution {
  execution_id: string;
  status: string;
  result: any;
}

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    console.log('🔑 Token récupéré:', token ? 'Token présent' : 'Aucun token'); // Debug
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async register(data: RegisterRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async getStoreCrews(category?: string): Promise<Crew[]> {
    const params = category ? `?category=${encodeURIComponent(category)}` : '';
    const response = await fetch(`${API_BASE_URL}/store/crews${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch crews');
    }

    return response.json();
  }

  async getCrewById(crewId: number): Promise<Crew> {
    const response = await fetch(`${API_BASE_URL}/store/crews/${crewId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch crew');
    }

    return response.json();
  }

  async getMyTeams(): Promise<TeamInstance[]> {
    console.log('📋 Récupération des équipes...'); // Debug
    const headers = this.getAuthHeaders();
    console.log('📤 Headers envoyés:', headers); // Debug

    const response = await fetch(`${API_BASE_URL}/my-teams/`, {
      headers: headers,
    });

    if (!response.ok) {
      console.error('❌ Erreur response:', response.status, response.statusText); // Debug
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch teams');
    }

    return response.json();
  }

  async addTeam(crewId: number, customName?: string): Promise<TeamInstance> {
    console.log('➕ Ajout équipe:', { crewId, customName }); // Debug
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
    };
    console.log('📤 Headers pour ajout:', headers); // Debug

    const response = await fetch(`${API_BASE_URL}/my-teams/add-crew`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        crew_id: crewId,
        custom_name: customName,
      }),
    });

    if (!response.ok) {
      console.error('❌ Erreur ajout équipe:', response.status, response.statusText); // Debug
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add team');
    }

    return response.json();
  }

  /**
   * 🚀 NEW: Execute a team instance
   */
  async runTeamInstance(instanceId: string, input: CrewInput): Promise<ExecutionResult> {
    console.log('🚀 Exécution équipe:', { instanceId, input }); // Debug
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
    };

    const response = await fetch(`${API_BASE_URL}/my-teams/${instanceId}/run`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      console.error('❌ Erreur exécution équipe:', response.status, response.statusText); // Debug
      const error = await response.json();
      throw new Error(error.detail || 'Failed to execute team');
    }

    return response.json();
  }

  /**
   * 🔄 NEW: Update team instance (e.g., custom name)
   */
  async updateTeamInstance(instanceId: string, updates: { custom_name?: string }): Promise<TeamInstance> {
    console.log('🔄 Mise à jour équipe:', { instanceId, updates }); // Debug
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
    };

    const response = await fetch(`${API_BASE_URL}/my-teams/${instanceId}`, {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      console.error('❌ Erreur mise à jour équipe:', response.status, response.statusText); // Debug
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update team');
    }

    return response.json();
  }

  /**
   * 🗑️ NEW: Remove/deactivate team instance
   */
  async removeTeamInstance(instanceId: string): Promise<{ message: string }> {
    console.log('🗑️ Suppression équipe:', { instanceId }); // Debug
    const headers = this.getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/my-teams/${instanceId}`, {
      method: 'DELETE',
      headers: headers,
    });

    if (!response.ok) {
      console.error('❌ Erreur suppression équipe:', response.status, response.statusText); // Debug
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove team');
    }

    return response.json();
  }
  // === WORKFLOWS ===
  async getWorkflows(category?: string): Promise<Workflow[]> {
    const params = category ? `?category=${category}` : '';
    const response = await this.request(`/workflows${params}`);
    return response;
  }

  async getWorkflowDetails(workflowId: number): Promise<Workflow & { 
    credential_status: Record<string, boolean>;
    missing_credentials: string[];
  }> {
    return this.request(`/workflows/${workflowId}`);
  }

  async executeWorkflow(workflowId: number, inputs: Record<string, any>): Promise<WorkflowExecution> {
    return this.request(`/workflows/${workflowId}/execute`, {
      method: 'POST',
      body: JSON.stringify(inputs)
    });
  }

  async syncWorkflows(): Promise<{
    message: string;
    added: number;
    updated: number;
    total: number;
  }> {
    return this.request('/workflows/sync-workflows', {
      method: 'POST'
    });
  }

  // === INTEGRATIONS ===
  async getAvailableIntegrations(): Promise<Integration[]> {
    return this.request('/integrations/integrations');
  }

  // === UNIFIED STORE ===
  async getAllStoreResources(options?: {
    resourceType?: 'crews' | 'workflows';
    category?: string;
    skip?: number;
    limit?: number;
  }): Promise<{
    crews: any[];
    workflows: Workflow[];
    total_crews: number;
    total_workflows: number;
  }> {
    const params = new URLSearchParams();
    if (options?.resourceType) params.append('resource_type', options.resourceType);
    if (options?.category) params.append('category', options.category);
    if (options?.skip) params.append('skip', options.skip.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    
    const queryString = params.toString();
    return this.request(`/store/all-resources${queryString ? `?${queryString}` : ''}`);
  }

  async getStoreCategories(): Promise<{
    crew_categories: string[];
    workflow_categories: string[];
    all_categories: string[];
  }> {
    return this.request('/store/categories');
  }

  async syncAllStoreResources(): Promise<{
    message: string;
    results: {
      crews: { added: number; updated: number; total: number };
      workflows: { added: number; updated: number; total: number };
    };
  }> {
    return this.request('/store/sync-all-resources', {
      method: 'POST'
    });
  }

  async configureIntegration(serviceName: string, credentials: Record<string, string>): Promise<{
    message: string;
    status: string;
    service_name: string;
  }> {
    return this.request('/integrations/configure', {
      method: 'POST',
      body: JSON.stringify({
        service_name: serviceName,
        credentials
      })
    });
  }

  async removeIntegration(serviceName: string): Promise<{ message: string }> {
    return this.request(`/integrations/${serviceName}`, {
      method: 'DELETE'
    });
  }

  async testIntegration(serviceName: string): Promise<{
    status: string;
    message: string;
  }> {
    return this.request(`/integrations/${serviceName}/test`, {
      method: 'POST'
    });
  }

  private async request(endpoint: string, options?: RequestInit) {
    const token = localStorage.getItem('access_token');
    const baseURL = 'http://localhost:8000';
    
    const response = await fetch(`${baseURL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}



export const apiService = new ApiService();