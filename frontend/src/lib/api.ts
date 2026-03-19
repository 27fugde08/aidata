import axios from "axios";

// Environment-aware API URL
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const API_URL = `${BACKEND_URL}/api/v1`;

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export { BACKEND_URL };

export const runAgent = async (prompt: string) => {
  const { data } = await api.post("/agent/run", { prompt });
  return data;
};

export const fetchAgents = async () => {
  // Assuming there's an endpoint to list available agents
  // If not, we can mock it or use a default list
  const { data } = await api.get("/agent/list"); 
  return data;
};

export const fetchTasks = async () => {
  const { data } = await api.get("/tasks/");
  return data;
};

export const fetchTaskStatus = async (taskId: string) => {
  const { data } = await api.get(`/tasks/${taskId}`);
  return data;
};
