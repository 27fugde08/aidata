const API_BASE_URL = 'http://localhost:8888';

// --- Navigation ---

function showTowerView(viewId) {
    // Update Sidebar
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.getAttribute('onclick').includes(`'${viewId}'`));
    });

    // Toggle Views
    document.querySelectorAll('.tower-view').forEach(view => {
        view.classList.toggle('active', view.id === `view-${viewId}`);
    });

    // Update Header Title
    const titles = {
        'command-center': 'Command Center',
        'agents-monitor': 'Agents Monitor',
        'workflow-builder': 'Workflow Builder',
        'automation-store': 'Automation Store',
        'system-monitor': 'System Monitor',
        'task-monitor': 'Task Monitor / Logs',
        'product-deployment': 'Product Deployment',
        'video-engine': 'AI Video Engine',
        'file-manager': 'Workspace File Explorer'
    };
    document.getElementById('view-title').textContent = titles[viewId] || 'AIOS Tower';

    // Specific Initializations
    if (viewId === 'system-monitor') pollSystemResources();
    if (viewId === 'agents-monitor') updateAgentFleetStatus();
    if (viewId === 'automation-store') loadAutomationStore();
    if (viewId === 'task-monitor') loadProcesses();
    if (viewId === 'product-deployment') loadDeployHistory();
    if (viewId === 'workflow-builder') loadWorkflows();
    if (viewId === 'video-engine') loadVideoLibrary();
    if (viewId === 'file-manager') loadFiles();
}

// --- File Manager ---

async function loadFiles(path = '') {
    const list = document.getElementById('file-list');
    list.innerHTML = '<div class="metric-sub">Scanning workspace...</div>';
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/files?path=${path}`);
        const data = await res.json();
        
        list.innerHTML = data.files.map(f => `
            <div class="agent-card" style="padding: 10px; cursor: pointer; text-align: center;" onclick="${f.type === 'file' ? `editFile('${f.path}')` : `loadFiles('${f.path}')`}">
                <i data-lucide="${f.type === 'file' ? 'file-text' : 'folder'}" style="margin-bottom: 5px; color: ${f.type === 'file' ? 'var(--text-dim)' : 'var(--accent)'}"></i>
                <div style="font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${f.name}</div>
            </div>
        `).join('');
        lucide.createIcons();
    } catch (e) { list.innerHTML = 'File system offline.'; }
}

async function editFile(path) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/files/content?path=${path}`);
        const data = await res.json();
        
        document.getElementById('editing-filename').textContent = path;
        document.getElementById('file-content-editor').value = data.content;
        document.getElementById('file-editor-panel').style.display = 'flex';
        
        // Scroll to editor
        document.getElementById('file-editor-panel').scrollIntoView({ behavior: 'smooth' });
    } catch (e) { alert('Could not read file.'); }
}

async function saveCurrentFile() {
    const path = document.getElementById('editing-filename').textContent;
    const content = document.getElementById('file-content-editor').value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/files/content`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path, content })
        });
        const data = await res.json();
        if (data.status === 'success') {
            addLogEntry(`File saved: ${path}`, 'success');
            alert('File saved successfully.');
        }
    } catch (e) { alert('Save failed.'); }
}

// --- Video Engine ---

async function downloadVideoEngine() {
    const input = document.getElementById('video-url-input');
    const url = input.value.trim();
    if (!url) return;

    const status = document.getElementById('video-engine-status');
    status.textContent = 'Downloading... (yt-dlp processing)';
    status.className = 'status-text warning';

    try {
        const res = await fetch(`${API_BASE_URL}/api/video/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        if (data.status === 'success') {
            status.textContent = 'Media secured in library.';
            status.className = 'status-text success';
            input.value = '';
            loadVideoLibrary();
        } else {
            throw new Error(data.error);
        }
    } catch (err) {
        status.textContent = `Error: ${err.message}`;
        status.className = 'status-text error';
    }
}

async function loadVideoLibrary() {
    const videoGrid = document.getElementById('video-library-grid');
    const shortsGrid = document.getElementById('shorts-library-grid');
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/video/list`);
        const data = await res.json();

        videoGrid.innerHTML = data.videos.map(v => `
            <div class="video-card glass-panel">
                <div class="video-name">${v.name}</div>
                <div class="video-meta">${(v.size/1024/1024).toFixed(1)} MB</div>
                <div class="video-actions">
                    <button class="btn btn-xs" onclick="clipShort('${v.name}')"><i data-lucide="scissors"></i> CLIP 9:16</button>
                    <a href="${API_BASE_URL}${v.url}" download class="btn btn-xs btn-secondary"><i data-lucide="download"></i></a>
                </div>
            </div>
        `).join('');

        shortsGrid.innerHTML = data.shorts.map(s => `
            <div class="video-card glass-panel short">
                <div class="video-name">${s.name}</div>
                <div class="video-actions">
                    <a href="${API_BASE_URL}${s.url}" target="_blank" class="btn btn-xs"><i data-lucide="play"></i> VIEW</a>
                    <a href="${API_BASE_URL}${s.url}" download class="btn btn-xs btn-secondary"><i data-lucide="download"></i></a>
                </div>
            </div>
        `).join('');
        lucide.createIcons();
    } catch (e) { console.error('Library load failed'); }
}

async function clipShort(filename) {
    const status = document.getElementById('video-engine-status');
    status.textContent = `Clipping ${filename}... (FFmpeg processing)`;
    status.className = 'status-text warning';

    try {
        const res = await fetch(`${API_BASE_URL}/api/video/clip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, start: 0, end: 30 }) // Default 30s
        });
        const data = await res.json();
        addLogEntry(`FFmpeg Job: ${data.message}`);
        
        // Polling library for completion
        setTimeout(loadVideoLibrary, 5000);
    } catch (err) {
        status.textContent = `Clip failed: ${err.message}`;
        status.className = 'status-text error';
    }
}

// --- Command Center (Chat) ---

async function handleChatInput(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChat();
    }
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    addChatMessage(text, 'user');
    input.value = '';

    if (text.startsWith('/team ')) {
        startOperationalTask(text.replace('/team ', ''), 'workflow');
    } else if (text.startsWith('/agent ')) {
        startOperationalTask(text.replace('/agent ', ''), 'single');
    } else {
        // Normal Chat with primary LLM
        const aiMsgDiv = addChatMessage('Thinking...', 'ai');
        const settings = getSettings();
        
        try {
            const res = await fetch(`${API_BASE_URL}/api/ai/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    messages: [{ role: 'user', content: text }],
                    api_key: settings.geminiKey
                })
            });
            const result = await res.text();
            aiMsgDiv.innerHTML = `<div class="msg-content">${marked.parse(result)}</div>`;
        } catch (err) { 
            aiMsgDiv.innerHTML = `<div class="msg-content error">Error: ${err.message}</div>`;
        }
    }
}

function addChatMessage(text, role) {
    const history = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `<div class="msg-content">${text}</div>`;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
    return div;
}

// --- Agents Monitor ---

async function updateAgentFleetStatus() {
    const agents = ['architect', 'developer', 'tester', 'reviewer'];
    const statusMap = ['idle', 'thinking', 'working', 'error'];
    
    agents.forEach(role => {
        const statusEl = document.getElementById(`status-${role}`);
        const taskEl = document.getElementById(`task-${role}`);
        
        // Simulating real-time updates for now, in real it would fetch from /api/agents/status
        // Or be pushed via WebSocket
        const randomStatus = statusMap[Math.floor(Math.random() * (statusMap.length - 1))]; // mostly non-error
        statusEl.className = `agent-status status-${randomStatus}`;
        statusEl.textContent = randomStatus.toUpperCase();
    });
}

// --- System Monitor ---

async function pollSystemResources() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/system/resources`);
        const data = await res.json();
        
        // Update Hardware
        document.getElementById('val-cpu').textContent = `${data.hardware.cpu_percent}%`;
        document.getElementById('fill-cpu').style.width = `${data.hardware.cpu_percent}%`;
        
        document.getElementById('val-ram').textContent = `${data.hardware.ram_used_gb} / ${data.hardware.ram_total_gb} GB`;
        document.getElementById('fill-ram').style.width = `${data.hardware.ram_percent}%`;
        
        // Update Tokens
        document.getElementById('val-tokens').textContent = data.tokens.total.toLocaleString();
        
        const modelList = document.getElementById('model-token-usage');
        modelList.innerHTML = '';
        Object.entries(data.tokens.by_model).forEach(([model, count]) => {
            const div = document.createElement('div');
            div.className = 'metric-sub';
            div.style.marginBottom = '5px';
            div.innerHTML = `<span>${model}:</span> <span style="color: var(--accent);">${count.toLocaleString()}</span>`;
            modelList.appendChild(div);
        });
    } catch (e) { console.error('Resource polling failed'); }
}

// --- Task Monitor & Logs ---

async function loadProcesses() {
    const container = document.getElementById('os-process-list');
    try {
        const res = await fetch(`${API_BASE_URL}/api/os/processes`);
        const data = await res.json();
        container.innerHTML = '';
        
        if (data.processes.length === 0) {
            container.innerHTML = '<div class="metric-sub">No active AI processes.</div>';
            return;
        }

        data.processes.reverse().forEach(proc => {
            const item = document.createElement('div');
            item.style.padding = '10px';
            item.style.background = 'rgba(255,255,255,0.02)';
            item.style.borderRadius = '6px';
            item.style.marginBottom = '8px';
            item.style.fontSize = '12px';
            item.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <strong>[PID ${proc.pid}] ${proc.name}</strong>
                    <span style="color:var(--accent)">${proc.status}</span>
                </div>
            `;
            container.appendChild(item);
        });
    } catch (e) {}
}

function clearLogs() {
    document.getElementById('logs-view').innerHTML = '<div class="log-entry">Log stream cleared.</div>';
}

function addLogEntry(msg, type = 'info') {
    const view = document.getElementById('logs-view');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString();
    entry.innerHTML = `<span style="color: #888;">[${time}]</span> ${msg}`;
    view.appendChild(entry);
    view.scrollTop = view.scrollHeight;
}

// --- Automation Store ---

async function loadAutomationStore() {
    const grid = document.getElementById('automation-store-grid');
    grid.innerHTML = '<div class="metric-sub">Loading operational templates...</div>';
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/automations/store`);
        const data = await res.json();
        
        grid.innerHTML = '';
        data.recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'agent-card'; // Reuse style
            card.innerHTML = `
                <div class="agent-header">
                    <div class="agent-icon"><i data-lucide="package"></i></div>
                    <div class="agent-name">${recipe.name}</div>
                </div>
                <div class="agent-task">${recipe.description}</div>
                <button class="btn btn-primary btn-block" style="margin-top:15px;" onclick="installOperationalTemplate('${recipe.id}')">INSTALL</button>
            `;
            grid.appendChild(card);
        });
        lucide.createIcons();
    } catch (err) { grid.innerHTML = 'Store offline.'; }
}

function installOperationalTemplate(id) {
    addLogEntry(`Installing operational blueprint: ${id}`, 'warning');
    alert(`Template ${id} synchronized with Workflow Builder.`);
    showTowerView('workflow-builder');
}

// --- Deployment Center ---

async function loadDeployHistory() {
    const container = document.getElementById('deploy-history-list');
    try {
        const res = await fetch(`${API_BASE_URL}/api/deploy/history`);
        const data = await res.json();
        container.innerHTML = '';
        
        data.history.reverse().forEach(dep => {
            const div = document.createElement('div');
            div.style.padding = '12px';
            div.style.background = 'rgba(255,255,255,0.02)';
            div.style.borderRadius = '8px';
            div.style.borderLeft = `3px solid ${dep.status === 'live' ? 'var(--accent)' : 'var(--danger)'}`;
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600;">
                    <span>${dep.project}</span>
                    <span style="color:var(--text-dim); font-size:11px;">${new Date(dep.timestamp).toLocaleDateString()}</span>
                </div>
                <div style="font-size:11px; margin-top:5px; color:${dep.status === 'live' ? 'var(--accent)' : 'var(--danger)'}">
                    ${dep.status.toUpperCase()} | URL: http://aios-cloud/${dep.project}
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {}
}

async function executeDeployment() {
    const path = document.getElementById('deploy-path').value;
    if (!path) return;
    
    addLogEntry(`Initiating production deployment for ${path}...`, 'warning');
    showTowerView('task-monitor');
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/deploy/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path, env: 'production' })
        });
        const data = await res.json();
        if (data.status === 'live') {
            addLogEntry(`DEPLOYMENT SUCCESS: ${path} is now LIVE.`, 'success');
        } else {
            addLogEntry(`DEPLOYMENT FAILED: ${data.logs}`, 'error');
        }
        loadDeployHistory();
    } catch (e) { addLogEntry(`Error: ${e.message}`, 'error'); }
}

// --- Operational Task Execution (Reuses backend /api/agent/work) ---

async function startOperationalTask(prompt, mode) {
    addLogEntry(`Task dispatched: ${prompt} [Mode: ${mode}]`, 'warning');
    showTowerView('task-monitor');
    
    const settings = getSettings();
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/agent/work`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, api_key: settings.geminiKey, mode })
        });
        
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const text = decoder.decode(value);
            text.split('\n').forEach(line => {
                if (line.trim()) addLogEntry(line);
            });
        }
    } catch (err) { addLogEntry(`Operational Error: ${err.message}`, 'error'); }
}

// --- Workflow Builder (Visual Placeholder) ---

let opWorkflows = [];

function loadWorkflows() {
    const canvas = document.getElementById('workflow-canvas');
    canvas.innerHTML = `
        <div style="text-align:center; padding-top:100px; color:var(--text-dim);">
            <i data-lucide="git-branch" size="48" style="margin-bottom:20px;"></i>
            <p>Drag blocks from the sidebar to design your AI pipeline.</p>
            <p style="font-size:12px; margin-top:10px;">(Visual Block Engine Initializing...)</p>
        </div>
    `;
    lucide.createIcons();
}

function addWorkflowStep() {
    addLogEntry('Operational Node added to canvas', 'info');
}

async function executeWorkflow() {
    const goal = prompt("Enter mission objective for this workflow:");
    if (goal) startOperationalTask(goal, 'workflow');
}

// --- Settings & Utils ---

function openSettings() { document.getElementById('settings-modal').style.display = 'flex'; }
function closeSettings() { document.getElementById('settings-modal').style.display = 'none'; }

function saveSettings() {
    const settings = {
        geminiKey: document.getElementById('gemini-key').value,
        openaiKey: document.getElementById('openai-key').value
    };
    localStorage.setItem('aios-tower-settings', JSON.stringify(settings));
    closeSettings();
    addLogEntry('Operational configuration updated.', 'info');
}

function getSettings() {
    const saved = localStorage.getItem('aios-tower-settings');
    return saved ? JSON.parse(saved) : {};
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    const settings = getSettings();
    document.getElementById('gemini-key').value = settings.geminiKey || '';
    document.getElementById('openai-key').value = settings.openaiKey || '';
    
    // Initial view
    showTowerView('command-center');
    
    // Auto-poll resources
    setInterval(pollSystemResources, 5000);
    setInterval(loadProcesses, 3000);
});
