// Session Management
let sessionId = localStorage.getItem("twin_session_id");
if (!sessionId) {
    sessionId = "session_" + Math.random().toString(36).substring(2, 11);
    localStorage.setItem("twin_session_id", sessionId);
}

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initModals();
    loadDashboard();
    initChat();
    initActionButtons();
});

// --- Tab Navigation ---
function initTabs() {
    const tabLinks = document.querySelectorAll(".tab-link");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabLinks.forEach(link => {
        link.addEventListener("click", () => {
            const targetTab = link.getAttribute("data-tab");

            tabLinks.forEach(l => l.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            link.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
        });
    });
}

// --- Modal Controls ---
function initModals() {
    const modalTriggers = [
        { btn: "add-goal-trigger", modal: "modal-goal" },
        { btn: "add-task-trigger", modal: "modal-task" },
        { btn: "log-wellness-trigger", modal: "modal-wellness" },
        { btn: "log-finance-trigger", modal: "modal-finance" }
    ];

    modalTriggers.forEach(trigger => {
        const btnElement = document.getElementById(trigger.btn);
        const modalElement = document.getElementById(trigger.modal);
        if (btnElement && modalElement) {
            btnElement.addEventListener("click", () => {
                modalElement.classList.add("active");
            });
        }
    });

    // Close buttons logic
    const closeBtns = document.querySelectorAll(".modal-close");
    closeBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            const modal = e.target.closest(".modal");
            if (modal) modal.classList.remove("active");
        });
    });

    // Close on click outside content
    window.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal")) {
            e.target.classList.remove("active");
        }
    });

    // Form Submissions
    initFormHandlers();
}

function initFormHandlers() {
    // 1. Goal Form
    const goalForm = document.getElementById("goal-form");
    if (goalForm) {
        goalForm.submit = false; // Bypass default
        goalForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById("goal-title").value,
                description: document.getElementById("goal-desc").value,
                category: document.getElementById("goal-cat").value,
                target_date: document.getElementById("goal-date").value
            };
            
            const res = await apiPost("/api/goals", payload);
            if (res.status === "success") {
                document.getElementById("modal-goal").classList.remove("active");
                goalForm.reset();
                loadDashboard();
            }
        });
    }

    // 2. Task Form
    const taskForm = document.getElementById("task-form");
    if (taskForm) {
        taskForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const goalIdVal = document.getElementById("task-goal").value;
            const payload = {
                title: document.getElementById("task-title").value,
                description: document.getElementById("task-desc").value,
                goal_id: goalIdVal ? parseInt(goalIdVal) : null,
                due_date: document.getElementById("task-date").value,
                priority: document.getElementById("task-priority").value
            };
            
            const res = await apiPost("/api/tasks", payload);
            if (res.status === "success") {
                document.getElementById("modal-task").classList.remove("active");
                taskForm.reset();
                loadDashboard();
            }
        });
    }

    // 3. Wellness Form
    const wellnessForm = document.getElementById("wellness-form");
    if (wellnessForm) {
        wellnessForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const checkedHabits = [];
            document.querySelectorAll("input[name='habit']:checked").forEach(checkbox => {
                checkedHabits.push(checkbox.value);
            });
            const payload = {
                sleep_hours: parseFloat(document.getElementById("well-sleep").value),
                exercise_minutes: parseInt(document.getElementById("well-exercise").value),
                calories_burned: parseInt(document.getElementById("well-calories").value || 0),
                mood: document.getElementById("well-mood").value,
                habits: checkedHabits
            };
            
            const res = await apiPost("/api/wellness", payload);
            if (res.status === "success") {
                document.getElementById("modal-wellness").classList.remove("active");
                wellnessForm.reset();
                loadDashboard();
            }
        });
    }

    // 4. Finance Form
    const financeForm = document.getElementById("finance-form");
    if (financeForm) {
        financeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                amount: parseFloat(document.getElementById("fin-amount").value),
                type: document.getElementById("fin-type").value,
                category: document.getElementById("fin-cat").value,
                description: document.getElementById("fin-desc").value
            };
            
            const res = await apiPost("/api/finances", payload);
            if (res.status === "success") {
                document.getElementById("modal-finance").classList.remove("active");
                financeForm.reset();
                loadDashboard();
            }
        });
    }
}

// --- Action Buttons (Briefing / Reflection) ---
function initActionButtons() {
    const briefingBtn = document.getElementById("btn-briefing");
    const reflectBtn = document.getElementById("btn-reflect");
    const closeBriefingBtn = document.getElementById("btn-close-briefing");
    const briefingPanel = document.getElementById("briefing-panel");
    const briefingContent = document.getElementById("briefing-content");

    if (briefingBtn) {
        briefingBtn.addEventListener("click", async () => {
            briefingPanel.classList.remove("hidden");
            briefingContent.innerHTML = "<em>Compiling daily briefing with Executive Assistant Agent...</em>";
            try {
                const res = await apiGet("/api/briefing");
                briefingContent.innerHTML = formatMarkdown(res.briefing);
            } catch (err) {
                briefingContent.innerHTML = "Failed to compile briefing. Check server logs.";
            }
        });
    }

    if (reflectBtn) {
        reflectBtn.addEventListener("click", async () => {
            briefingPanel.classList.remove("hidden");
            briefingContent.innerHTML = "<em>Analyzing logs & compiling reflection metrics...</em>";
            try {
                const res = await apiPost("/api/reflect", {});
                briefingContent.innerHTML = formatMarkdown(res.reflection);
                loadDashboard(); // Reload to capture any changes
            } catch (err) {
                briefingContent.innerHTML = "Failed to trigger reflection. Check server logs.";
            }
        });
    }

    if (closeBriefingBtn) {
        closeBriefingBtn.addEventListener("click", () => {
            briefingPanel.classList.add("hidden");
        });
    }
}

// --- Chat Interface ---
function initChat() {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const messagesContainer = document.getElementById("chat-messages");

    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = chatInput.value.trim();
            if (!text) return;

            // Render User message
            appendMessage("User", text, "user-msg");
            chatInput.value = "";

            // Render loading indicator
            const loadingMsg = appendMessage("Twin Assistant", "...", "agent-msg loading");

            try {
                const res = await apiPost("/api/chat", {
                    message: text,
                    session_id: sessionId
                });
                
                // Remove loading and render reply
                loadingMsg.remove();
                appendMessage("Twin Assistant", res.response, "agent-msg");
                loadDashboard(); // Refresh metrics since tools might have modified goal/task states
            } catch (err) {
                loadingMsg.remove();
                appendMessage("System Error", "Failed to retrieve agent response. Verify your API key.", "system-msg");
            }
        });
    }
}

function appendMessage(sender, text, className) {
    const container = document.getElementById("chat-messages");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;
    
    // Simple markdown formatting for agent answers
    const formattedText = className.includes("user-msg") ? text : formatMarkdown(text);
    msgDiv.innerHTML = `<p><strong>${sender}:</strong> ${formattedText}</p>`;
    
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    return msgDiv;
}

// --- Fetch Dashboard Content ---
async function loadDashboard() {
    try {
        const data = await apiGet("/api/dashboard");
        renderGoals(data.goals);
        renderTasks(data.tasks);
        renderLearningPlans(data.learning);
        renderWellness(data.wellness);
        renderFinances(data.finances);
        renderSkills(data.skills);
        populateGoalDropdown(data.goals);
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

// Populate task goal dropdown
function populateGoalDropdown(goals) {
    const dropdown = document.getElementById("task-goal");
    if (!dropdown) return;
    
    dropdown.innerHTML = '<option value="">No goal linkage</option>';
    goals.forEach(g => {
        const option = document.createElement("option");
        option.value = g.id;
        option.textContent = g.title;
        dropdown.appendChild(option);
    });
}

function renderGoals(goals) {
    const container = document.getElementById("goals-list");
    if (!container) return;

    if (goals.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No goals tracked. Click '+ Add Goal' to create one.</p>";
        return;
    }

    container.innerHTML = goals.map(g => `
        <div class="goal-card">
            <div class="goal-header">
                <h5>${g.title}</h5>
                <span class="goal-badge ${g.category}">${g.category}</span>
            </div>
            <p class="subtitle">${g.description || ""}</p>
            <div class="goal-progress">
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${g.progress}%"></div>
                </div>
                <span>${g.progress}%</span>
            </div>
        </div>
    `).join("");
}

function renderTasks(tasks) {
    const container = document.getElementById("tasks-list");
    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No tasks pending. Click '+ Add Task' to add items.</p>";
        return;
    }

    // Sort tasks: pending first, then high priority
    const sorted = tasks.sort((a,b) => {
        if (a.status === 'done' && b.status !== 'done') return 1;
        if (a.status !== 'done' && b.status === 'done') return -1;
        const priorities = { high: 3, medium: 2, low: 1 };
        return priorities[b.priority] - priorities[a.priority];
    });

    container.innerHTML = sorted.map(t => `
        <div class="task-item ${t.status === 'done' ? 'done' : ''}">
            <div class="task-left">
                <div class="task-check" onclick="toggleTaskStatus(${t.id}, '${t.status}')">✓</div>
                <div>
                    <span class="task-title">${t.title}</span>
                    <div class="task-meta">
                        <span class="priority-tag ${t.priority}">${t.priority} priority</span>
                        ${t.due_date ? `<span>Due: ${t.due_date}</span>` : ""}
                    </div>
                </div>
            </div>
            <div class="task-right">
                ${t.status === 'done' ? 'Done' : 'Pending'}
            </div>
        </div>
    `).join("");
}

async function toggleTaskStatus(taskId, currentStatus) {
    const newStatus = currentStatus === 'done' ? 'todo' : 'done';
    
    // Simulate updating via chat or direct API to show multi-agent sync
    appendMessage("System", `Updating task status of Task #${taskId} to ${newStatus}...`, "system-msg");
    
    try {
        await apiPost("/api/chat", {
            message: `Update task status of task ID ${taskId} to ${newStatus}`,
            session_id: sessionId
        });
        loadDashboard();
    } catch (err) {
        console.error(err);
    }
}

function renderLearningPlans(plans) {
    const container = document.getElementById("learning-plans");
    if (!container) return;

    if (plans.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No active study plans found.</p>";
        return;
    }

    container.innerHTML = plans.map(p => `
        <div class="plan-card">
            <h5 class="plan-title">${p.title}</h5>
            <div class="plan-topic">${p.topic}</div>
            <div class="goal-progress mb-2">
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${p.progress}%"></div>
                </div>
                <span>${p.progress}%</span>
            </div>
            <p class="plan-resources">Resources: ${p.resources}</p>
        </div>
    `).join("");
}

function renderSkills(skills) {
    const container = document.getElementById("career-skills");
    if (!container) return;

    if (skills.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No career portfolio items found. Ask the twin agent to track your professional growth!</p>";
        return;
    }

    container.innerHTML = skills.map(s => `
        <div class="skill-row">
            <div class="skill-header">
                <h5>Skill: ${s.skill_name}</h5>
                <span class="skill-level">${s.proficiency}</span>
            </div>
            <p class="subtitle">Certifications: ${s.certifications || 'None linked'}</p>
            ${s.roadmap && s.roadmap.length > 0 ? `
                <ul class="skill-roadmap">
                    ${s.roadmap.map(step => `<li>${step}</li>`).join("")}
                </ul>
            ` : ""}
        </div>
    `).join("");
}

function renderWellness(logs) {
    const container = document.getElementById("wellness-metrics");
    if (!container) return;

    if (logs.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No wellness logs submitted today.</p>";
        return;
    }

    // Latest log
    const latest = logs[0];

    container.innerHTML = `
        <div class="metric-card">
            <div class="metric-lbl">Sleep Duration</div>
            <div class="metric-val">${latest.sleep_hours}h</div>
            <div class="metric-lbl">Target: 8h</div>
        </div>
        <div class="metric-card">
            <div class="metric-lbl">Exercise Time</div>
            <div class="metric-val">${latest.exercise_minutes}m</div>
            <div class="metric-lbl">Target: 30m</div>
        </div>
        <div class="metric-card">
            <div class="metric-lbl">Active Calories</div>
            <div class="metric-val">${latest.calories_burned}</div>
            <div class="metric-lbl">Kcal today</div>
        </div>
        <div class="metric-card">
            <div class="metric-lbl">Mood / Energy</div>
            <div class="metric-val" style="font-size: 1.3rem; text-transform:capitalize; padding: 12px 0;">${latest.mood}</div>
            <div class="metric-lbl">Condition</div>
        </div>
    `;
}

function renderFinances(finances) {
    const container = document.getElementById("finance-list");
    if (!container) return;

    if (finances.length === 0) {
        container.innerHTML = "<p class='text-secondary'>No transaction history recorded.</p>";
        return;
    }

    container.innerHTML = finances.map(f => `
        <div class="transaction-item">
            <div>
                <strong>${f.description}</strong>
                <div class="txn-meta">${f.date} | Category: ${f.category}</div>
            </div>
            <span class="txn-amount ${f.type}">
                ${f.type === 'expense' ? '-' : '+'}$${f.amount.toFixed(2)}
            </span>
        </div>
    `).join("");
}

// --- API Helpers ---
async function apiGet(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`GET ${url} failed`);
    return await response.json();
}

async function apiPost(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`POST ${url} failed`);
    return await response.json();
}

// Simple markdown formatting helper
function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^- (.*)/gm, '<li>$1</li>')
        .replace(/\n\n/g, '<br/>');
}
