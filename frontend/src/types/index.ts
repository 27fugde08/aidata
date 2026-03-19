export interface Message {
  role: 'agent' | 'user';
  content: string;
}

export interface AgentResponse {
  response: string;
  task_id?: string;
}

export interface Task {
  id: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  result?: any;
  created_at: string;
  updated_at: string;
  agent_name?: string;
}

export interface Agent {
  name: string;
  description: string;
  status: 'active' | 'inactive';
}
