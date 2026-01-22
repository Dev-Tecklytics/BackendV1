/**
 * IAAP Backend API Client
 * TypeScript/JavaScript API Reference
 *
 * Base URL: http://127.0.0.1:8000
 */

export const API_BASE_URL = "http://127.0.0.1:8000";

// ============================================
// TYPES & INTERFACES
// ============================================

export interface UserRegistration {
  email: string;
  password: string;
  full_name?: string;
  company_name?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    email: string;
    full_name: string;
    user_id: string;
  };
}

export interface UserProfile {
  user_id: string;
  email: string;
  full_name?: string;
}

export interface ProjectCreate {
  name: string;
  platform: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

export interface Project {
  project_id: string;
  name: string;
  platform: string;
  description?: string;
  created_at: string;
}

export interface WorkflowAnalysis {
  complexity_score: number;
  complexity_level: string;
  nesting_depth: number;
  activity_count: number;
  variable_count: number;
}

export interface ApiKeyResponse {
  api_key: string;
  name?: string;
}

export interface ApiKeyInfo {
  api_key_id: string;
  name?: string;
  key_prefix: string;
  created_at: string;
  is_active: boolean;
}

export interface SubscriptionPlan {
  plan_id: string;
  name: string;
  description: string;
  price: number;
  billing_cycle: string;
  max_analyses_per_month: number;
}

export interface Subscription {
  subscription_id: string;
  plan_id: string;
  status: string;
  start_date: string;
  end_date: string;
}

// ============================================
// API CLIENT CLASS
// ============================================

export class IaapApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Set authentication token
   */
  setToken(token: string) {
    this.token = token;
  }

  /**
   * Get authentication headers
   */
  private getHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (includeAuth && this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // ============================================
  // AUTHENTICATION
  // ============================================

  /**
   * Register a new user
   */
  async register(data: UserRegistration): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
      method: "POST",
      headers: this.getHeaders(false),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Registration failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: this.getHeaders(false),
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.statusText}`);
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh-token`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Token refresh failed: ${response.statusText}`);
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    await fetch(`${this.baseUrl}/api/v1/auth/logout`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    this.token = null;
  }

  // ============================================
  // USER MANAGEMENT
  // ============================================

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/v1/user/me`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update user profile
   */
  async updateProfile(
    fullName?: string,
    companyName?: string,
  ): Promise<{ message: string }> {
    const params = new URLSearchParams();
    if (fullName) params.append("full_name", fullName);
    if (companyName) params.append("company_name", companyName);

    const response = await fetch(
      `${this.baseUrl}/api/v1/user/profile?${params}`,
      {
        method: "PUT",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to update profile: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // PROJECTS
  // ============================================

  /**
   * Create a new project
   */
  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create project: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all projects
   */
  async getProjects(): Promise<Project[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get projects: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get project by ID
   */
  async getProject(projectId: string): Promise<Project> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/projects/${projectId}`,
      {
        method: "GET",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to get project: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update project
   */
  async updateProject(
    projectId: string,
    data: ProjectUpdate,
  ): Promise<Project> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/projects/${projectId}`,
      {
        method: "PATCH",
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to update project: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete project
   */
  async deleteProject(projectId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/projects/${projectId}`,
      {
        method: "DELETE",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to delete project: ${response.statusText}`);
    }
  }

  // ============================================
  // FILES
  // ============================================

  /**
   * Upload a file to a project
   */
  async uploadFile(
    projectId: string,
    file: File,
  ): Promise<{ file_id: string; file_name: string }> {
    const formData = new FormData();
    formData.append("upload", file);

    const headers: HeadersInit = {};
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(
      `${this.baseUrl}/api/v1/files/upload?project_id=${projectId}`,
      {
        method: "POST",
        headers,
        body: formData,
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to upload file: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // WORKFLOWS
  // ============================================

  /**
   * Analyze a workflow
   */
  async analyzeWorkflow(
    fileId: string,
    platform: string,
  ): Promise<WorkflowAnalysis> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/workflows/analyze?file_id=${fileId}&platform=${platform}`,
      {
        method: "POST",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to analyze workflow: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // CODE REVIEW
  // ============================================

  /**
   * Perform code review on a workflow
   */
  async reviewWorkflow(workflowId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/code-review?workflow_id=${workflowId}`,
      {
        method: "POST",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to review workflow: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // SUBSCRIPTIONS
  // ============================================

  /**
   * Get all subscription plans
   */
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/subscription/plans`, {
      method: "GET",
      headers: this.getHeaders(false),
    });

    if (!response.ok) {
      throw new Error(`Failed to get plans: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Subscribe to a plan
   */
  async subscribe(planId: string): Promise<{ message: string }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/subscription/subscribe?plan_id=${planId}`,
      {
        method: "POST",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to subscribe: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get current subscription
   */
  async getCurrentSubscription(): Promise<Subscription> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/subscription/current`,
      {
        method: "GET",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to get subscription: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // API KEYS
  // ============================================

  /**
   * Create a new API key
   */
  async createApiKey(name?: string): Promise<ApiKeyResponse> {
    const url = name
      ? `${this.baseUrl}/api/v1/api_key?name=${encodeURIComponent(name)}`
      : `${this.baseUrl}/api/v1/api_key`;

    const response = await fetch(url, {
      method: "POST",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to create API key: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all API keys
   */
  async getApiKeys(): Promise<ApiKeyInfo[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/api_key`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get API keys: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete an API key
   */
  async deleteApiKey(apiKeyId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/api_key/${apiKeyId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete API key: ${response.statusText}`);
    }
  }

  /**
   * Rotate an API key
   */
  async rotateApiKey(apiKeyId: string): Promise<{ new_api_key: string }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/api_key/${apiKeyId}/rotate`,
      {
        method: "PUT",
        headers: this.getHeaders(),
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to rotate API key: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // EXPORT
  // ============================================

  /**
   * Export workflow data to CSV
   */
  async exportToCsv(): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/export/csv`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to export CSV: ${response.statusText}`);
    }

    return response.blob();
  }

  // ============================================
  // HEALTH CHECK
  // ============================================

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// ============================================
// USAGE EXAMPLE
// ============================================

/*
// Initialize the client
const api = new IaapApiClient();

// Register and login
const user = await api.register({
  email: 'user@example.com',
  password: 'securePassword123',
  full_name: 'John Doe'
});

const auth = await api.login({
  email: 'user@example.com',
  password: 'securePassword123'
});

// Create a project
const project = await api.createProject({
  name: 'My RPA Project',
  platform: 'UiPath',
  description: 'Project description'
});

// Upload a file
const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
const file = fileInput.files[0];
const uploadResult = await api.uploadFile(project.project_id, file);

// Analyze the workflow
const analysis = await api.analyzeWorkflow(uploadResult.file_id, 'UiPath');
console.log('Complexity Score:', analysis.complexity_score);

// Get all projects
const projects = await api.getProjects();

// Export to CSV
const csvBlob = await api.exportToCsv();
const url = URL.createObjectURL(csvBlob);
const a = document.createElement('a');
a.href = url;
a.download = 'workflows.csv';
a.click();
*/
