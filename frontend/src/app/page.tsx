"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, Bot, User, Loader2, Sparkles, Database, CheckCircle, XCircle, Clock } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { runAgent, fetchTasks, fetchAgents } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Message, Task, Agent } from "@/types";

export default function Home() {
  const queryClient = useQueryClient();
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "agent", content: "👋 Hello! I am your AIOS Assistant. Select an agent or ask me to perform a task." },
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Poll tasks every 3 seconds
  const { data: tasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: fetchTasks,
    refetchInterval: 3000,
  });

  // Mock agents list - in real app, fetch from backend
  const agents: Agent[] = [
    { name: "Research Agent", description: "Searches the web and summarizes info", status: "active" },
    { name: "Code Agent", description: "Writes and debugs code", status: "active" },
    { name: "Media Agent", description: "Analyzes images and videos", status: "inactive" },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const mutation = useMutation({
    mutationFn: runAgent,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: data.response },
      ]);
      // Invalidate tasks to refresh the list immediately
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: "❌ Error: Something went wrong. Please check the backend connection." },
      ]);
      console.error(error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || mutation.isPending) return;

    const userMsg: Message = { role: "user", content: prompt };
    setMessages((prev) => [...prev, userMsg]);
    mutation.mutate(prompt);
    setPrompt("");
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar - Agents */}
      <aside className="w-64 border-r bg-muted/20 p-4 hidden md:flex flex-col gap-4">
        <div className="flex items-center gap-2 font-bold text-lg mb-4">
          <Database className="h-5 w-5" />
          <span>AIOS Agents</span>
        </div>
        <div className="space-y-2 overflow-y-auto flex-1">
          {agents.map((agent) => (
            <div key={agent.name} className="p-3 rounded-lg border bg-card hover:bg-accent cursor-pointer transition-colors">
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-sm">{agent.name}</span>
                <span className={cn("h-2 w-2 rounded-full", agent.status === 'active' ? "bg-green-500" : "bg-gray-300")} />
              </div>
              <p className="text-xs text-muted-foreground">{agent.description}</p>
            </div>
          ))}
        </div>
        
        {/* Task Monitor (Mini) */}
        <div className="border-t pt-4">
            <h3 className="text-sm font-semibold mb-2">Recent Tasks</h3>
             <div className="space-y-2 max-h-48 overflow-y-auto text-xs">
                {tasks?.slice(0, 5).map((task: Task) => (
                    <div key={task.id} className="flex justify-between items-center p-2 rounded bg-muted/50">
                        <span className="truncate w-24">Task #{task.id.slice(0,4)}</span>
                        {task.status === 'COMPLETED' && <CheckCircle className="h-3 w-3 text-green-500" />}
                        {task.status === 'IN_PROGRESS' && <Loader2 className="h-3 w-3 animate-spin text-blue-500" />}
                        {task.status === 'FAILED' && <XCircle className="h-3 w-3 text-red-500" />}
                        {task.status === 'PENDING' && <Clock className="h-3 w-3 text-yellow-500" />}
                    </div>
                ))}
             </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative">
        <header className="h-14 border-b flex items-center px-6 justify-between bg-background/95 backdrop-blur">
          <h1 className="font-semibold flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            AIOS Assistant
          </h1>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={cn(
                "flex w-full items-start gap-4",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === "agent" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20 mt-1">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
              )}
              
              <div
                className={cn(
                  "relative max-w-[80%] rounded-2xl px-5 py-3 text-sm md:text-base shadow-sm",
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground rounded-tr-none"
                    : "bg-muted text-foreground rounded-tl-none border border-border"
                )}
              >
                <ReactMarkdown className="prose dark:prose-invert prose-sm max-w-none break-words">
                  {msg.content}
                </ReactMarkdown>
              </div>

              {msg.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary border border-border mt-1">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}
          
          {mutation.isPending && (
            <div className="flex w-full items-start gap-4 justify-start">
               <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted px-5 py-3 rounded-2xl rounded-tl-none border border-border flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Processing task...</span>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t bg-background">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-3">
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask AIOS to perform a task..."
              className="flex-1"
              disabled={mutation.isPending}
            />
            <Button 
              type="submit" 
              size="icon" 
              disabled={!prompt.trim() || mutation.isPending}
            >
              {mutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </main>
      
      {/* Right Panel - Detailed Task / Output View (Optional - kept simple for now) */}
      <aside className="w-80 border-l bg-muted/10 p-4 hidden lg:block overflow-y-auto">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Task History
        </h3>
        <div className="space-y-3">
            {tasks?.map((task: Task) => (
                <Card key={task.id} className="text-sm">
                    <CardHeader className="p-3 pb-1">
                        <div className="flex justify-between items-start">
                            <span className="font-medium text-xs text-muted-foreground">Task ID: {task.id.slice(0,8)}</span>
                            <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full border", 
                                task.status === 'COMPLETED' ? "bg-green-100 text-green-700 border-green-200" :
                                task.status === 'IN_PROGRESS' ? "bg-blue-100 text-blue-700 border-blue-200" :
                                "bg-gray-100 text-gray-700 border-gray-200"
                            )}>
                                {task.status}
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent className="p-3 pt-2">
                        {task.result ? (
                             <div className="bg-muted p-2 rounded text-xs font-mono overflow-x-auto max-h-32">
                                {JSON.stringify(task.result, null, 2)}
                             </div>
                        ) : (
                            <p className="text-xs text-muted-foreground italic">No result yet...</p>
                        )}
                        <div className="mt-2 text-[10px] text-muted-foreground text-right">
                            {new Date(task.created_at).toLocaleString()}
                        </div>
                    </CardContent>
                </Card>
            ))}
            {!tasks?.length && (
                <div className="text-center text-muted-foreground text-sm py-8">
                    No tasks found.
                </div>
            )}
        </div>
      </aside>
    </div>
  );
}
