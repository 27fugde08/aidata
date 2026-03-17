const API_BASE = "http://localhost:8000/api/v1";

/**
 * AIOS Professional API Client
 * Centralizes all communication logic with error handling and logging.
 */
class AIOSApiClient {
    async request(endpoint, method = 'GET', body = null) {
        const url = `${API_BASE}${endpoint}`;
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) options.body = JSON.stringify(body);

        try {
            const response = await fetch(url, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "API Error");
            return data;
        } catch (error) {
            store.showToast(error.message, "error");
            throw error;
        }
    }

    // Projects CRUD
    getProjects() { return this.request('/projects/'); }
    createProject(data) { return this.request('/projects/', 'POST', data); }
    deleteProject(id) { return this.request(`/projects/${id}`, 'DELETE'); }

    // System Stats
    getHealth() { return this.request('/system/health'); }
    
    // Commands
    executeCommand(command) { return this.request('/command/execute', 'POST', { command }); }
}

const api = new AIOSApiClient();

/**
 * AIOS Global Store (2025 Reactive Pattern)
 */
class AIOSStore {
    constructor() {
        const lastView = localStorage.getItem('aios_last_view') || 'dashboard';

        this.state = new Proxy({
            currentView: lastView,
            resources: { cpu: 0, ram: { used: 0, total: 0, percent: 0 } },
            projects: [],
            logs: [],
            thoughtTraces: []
        }, {
            set: (target, prop, value) => {
                target[prop] = value;
                if (prop === 'currentView') localStorage.setItem('aios_last_view', value);
                this.render(); 
                return true;
            }
        });
        
        this.eventSource = null;
    }

    render() {
        updateHeaderUI(this.state.resources);
        if (this.state.currentView === 'dashboard') {
            renderDashboard(this.state.projects);
        }
    }

    async init() {
        try {
            const [pData, hData] = await Promise.all([api.getProjects(), api.getHealth()]);
            this.state.projects = pData.data;
            this.state.resources = hData.data;
            this.connectStream();
        } catch (e) {
            this.showToast("Connection to Kernel failed", "error");
        }
    }

    connectStream() {
        if (this.eventSource) this.eventSource.close();
        this.eventSource = new EventSource(`${API_BASE}/system/stream`);
        this.eventSource.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            this.handleEvent(type, data);
        };
    }

    handleEvent(type, data) {
        switch(type) {
            case 'project_created':
                this.state.projects = [...this.state.projects, data];
                this.showToast(`New Project: ${data.name}`, "success");
                break;
            case 'project_deleted':
                this.state.projects = this.state.projects.filter(p => p.id !== data.id);
                this.showToast(`Project Deleted`, "info");
                break;
            case 'log':
                this.addLog(data.message, data.level);
                break;
            case 'trace':
                this.addTrace(data.agent, data.message);
                break;
        }
    }

    showToast(msg, type = "info") {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        const colors = {
            success: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400',
            error: 'border-red-500/50 bg-red-500/10 text-red-400',
            info: 'border-blue-500/50 bg-blue-500/10 text-blue-400'
        };
        toast.className = `px-4 py-3 rounded-xl border backdrop-blur-md text-[10px] font-bold animate-in slide-in-from-right duration-300 ${colors[type]}`;
        toast.innerText = msg.toUpperCase();
        container.appendChild(toast);
        setTimeout(() => { toast.classList.add('fade-out'); setTimeout(() => toast.remove(), 500); }, 3000);
    }

    addLog(msg, level) {
        const logs = document.getElementById('kernel-logs');
        if (!logs) return;
        const line = document.createElement('div');
        const color = level === 'ERROR' ? 'text-red-400' : (level === 'WARNING' ? 'text-yellow-400' : 'text-emerald-500/70');
        line.innerHTML = `<span class="opacity-30 mr-2">[${new Date().toLocaleTimeString()}]</span> <span class="font-bold mr-2 ${color}">[${level}]</span> ${msg}`;
        logs.appendChild(line);
        logs.scrollTop = logs.scrollHeight;
    }

    addTrace(agent, message) {
        const stream = document.getElementById('thought-stream');
        if (!stream) return;
        const trace = document.createElement('div');
        trace.className = "p-2 bg-white/5 rounded-lg border-l-2 border-purple-500/50 mb-2 animate-in fade-in";
        trace.innerHTML = `<span class="text-purple-400 font-bold opacity-80">[${agent}]</span> ${message}`;
        stream.prepend(trace);
    }
}

const store = new AIOSStore();

// --- View Rendering ---
const views = {
    dashboard: `
        <div class="grid grid-cols-12 gap-6 h-full overflow-hidden">
            <div class="col-span-8 flex flex-col gap-6 overflow-hidden">
                <!-- Chat UI -->
                <div class="flex-1 bg-[#0a0a0f]/60 backdrop-blur-md rounded-2xl border border-white/5 flex flex-col overflow-hidden shadow-2xl">
                    <div class="p-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                        <div class="flex items-center gap-2">
                            <i data-lucide="terminal" class="w-4 h-4 text-emerald-400"></i>
                            <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">AIOS Command Terminal</span>
                        </div>
                        <div id="thinking-indicator" class="hidden flex items-center gap-2">
                            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></div>
                            <span class="text-[10px] text-emerald-500 font-bold uppercase">Executing...</span>
                        </div>
                    </div>
                    <div id="chat-history" class="flex-1 p-6 overflow-y-auto space-y-6 scrollbar-hide"></div>
                    <div class="p-4 bg-black/40 border-t border-white/5">
                        <div class="flex items-center gap-3 bg-black/60 rounded-xl border border-white/10 p-2">
                            <input id="chat-input" placeholder="Type /aios command here..." 
                                   class="flex-1 bg-transparent border-none text-white text-sm outline-none p-2 fira"
                                   onkeypress="if(event.key==='Enter') sendChat()">
                            <button onclick="sendChat()" class="bg-emerald-500 hover:bg-emerald-600 text-black w-10 h-10 flex items-center justify-center rounded-lg transition-all">
                                <i data-lucide="arrow-right" class="w-5 h-5"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-span-4 flex flex-col gap-6 overflow-hidden">
                <!-- Projects -->
                <div class="flex-1 bg-[#0a0a0f]/60 backdrop-blur-md rounded-2xl border border-white/5 p-4 flex flex-col overflow-hidden">
                    <div class="flex items-center justify-between mb-4 px-2">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Project Fleet</span>
                        <button onclick="createProject()" class="p-1.5 bg-emerald-500/10 text-emerald-400 rounded-lg hover:bg-emerald-500/20 transition-all">
                            <i data-lucide="plus" class="w-4 h-4"></i>
                        </button>
                    </div>
                    <div id="project-list" class="flex-1 overflow-y-auto space-y-2 px-2 scrollbar-hide"></div>
                </div>

                <!-- Live Thought Traces -->
                <div class="h-64 bg-[#0a0a0f]/60 backdrop-blur-md rounded-2xl border border-white/5 p-4 flex flex-col overflow-hidden">
                    <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-4 block">AI Core Reasoning</span>
                    <div id="thought-stream" class="flex-1 overflow-y-auto space-y-2 text-[10px] fira text-slate-500 scrollbar-hide"></div>
                </div>
            </div>

            <!-- Global Logs -->
            <div class="col-span-12 h-32 bg-black/80 rounded-2xl border border-white/5 p-4 overflow-hidden shadow-inner">
                <div id="kernel-logs" class="h-full overflow-y-auto fira text-[10px] text-emerald-500/60 space-y-1 scrollbar-hide"></div>
            </div>
        </div>
    `
};

function switchView(viewId) {
    store.state.currentView = viewId;
    document.getElementById('view-content').innerHTML = views[viewId] || views.dashboard;
    document.getElementById('view-title').innerText = viewId.toUpperCase();
    
    // Sidebar active state
    document.querySelectorAll('.nav-item').forEach(el => {
        const isActive = el.id === `nav-${viewId}`;
        el.classList.toggle('bg-emerald-500/10', isActive);
        el.classList.toggle('text-emerald-400', isActive);
    });

    if (window.lucide) lucide.createIcons();
}

function updateHeaderUI(res) {
    const cpuEl = document.getElementById('header-cpu');
    const ramEl = document.getElementById('header-ram');
    if (cpuEl) cpuEl.innerText = `${res.cpu}%`;
    if (ramEl) ramEl.innerText = `${res.ram.used}GB`;
}

function renderDashboard(projects) {
    const pList = document.getElementById('project-list');
    if (!pList) return;
    pList.innerHTML = projects.map(p => `
        <div class="p-4 bg-white/[0.03] border border-white/5 rounded-xl hover:border-emerald-500/30 transition-all group flex items-center justify-between">
            <div class="flex flex-col gap-1">
                <span class="text-xs font-bold text-slate-200 group-hover:text-emerald-400 transition-colors">${p.name}</span>
                <span class="text-[9px] text-slate-500 fira">${p.id}</span>
            </div>
            <button onclick="api.deleteProject('${p.id}')" class="p-2 opacity-0 group-hover:opacity-100 text-slate-600 hover:text-red-400 transition-all">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');
    if (window.lucide) lucide.createIcons();
}

// --- Interactions ---
async function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    
    addChatMessage('user', text);
    input.value = '';
    document.getElementById('thinking-indicator')?.classList.remove('hidden');

    try {
        const res = await api.executeCommand(text);
        addChatMessage('ai', res.message);
    } catch (e) {
        addChatMessage('ai', "Kernel interaction failed.");
    } finally {
        document.getElementById('thinking-indicator')?.classList.add('hidden');
    }
}

async function createProject() {
    const name = prompt("Project Name:");
    if (!name) return;
    const description = prompt("Description:");
    await api.createProject({ name, description: description || "" });
}

function addChatMessage(role, text) {
    const history = document.getElementById('chat-history');
    if (!history) return;
    const msg = document.createElement('div');
    msg.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`;
    msg.innerHTML = `
        <div class="max-w-[90%] p-4 rounded-2xl text-xs ${role === 'user' ? 'bg-emerald-500 text-black font-bold' : 'bg-white/5 border border-white/10 text-slate-200'}">
            ${role === 'ai' ? marked.parse(text) : text}
        </div>
    `;
    history.appendChild(msg);
    history.scrollTop = history.scrollHeight;
}

// --- Boot ---
document.addEventListener('DOMContentLoaded', () => {
    switchView(store.state.currentView);
    store.init();
    setInterval(() => api.getHealth().then(d => store.state.resources = d.data), 5000);
});
