/* =========================================================================
   NOVA Dashboard — client live
   ========================================================================= */

const { supabaseUrl, supabaseAnonKey, agentName } = window.__NOVA__;

const supa = window.supabase.createClient(supabaseUrl, supabaseAnonKey, {
    realtime: { params: { eventsPerSecond: 10 } }
});

/* ---- Refs DOM ---- */
const $ = (id) => document.getElementById(id);
const els = {
    orb: $("orb"),
    dot: $("status-dot"),
    label: $("status-label"),
    mood: $("status-mood"),
    activity: $("status-activity"),
    target: $("status-target"),
    stream: $("stream"),
    streamSub: $("stream-sub"),
    pipeline: $("pipeline"),
    pipelineSub: $("pipeline-sub"),
    convos: $("convos"),
    convosSub: $("convos-sub"),
    cProspects: $("counter-prospects"),
    cEmails: $("counter-emails"),
    cReplies: $("counter-replies"),
    cAlerts: $("counter-alerts"),
    sProspects: $("stat-prospects"),
    sEvents: $("stat-events"),
    sConvos: $("stat-convos"),
    sAlerts: $("stat-alerts"),
    heartbeat: $("heartbeat"),
    console: $("console"),
    consoleSub: $("console-sub"),
    tasks: $("tasks"),
    tasksSub: $("tasks-sub"),
};

/* ---- Utilities ---- */
const MOOD_EMOJI = {
    serene: "🌌", focused: "🎯", excited: "✨",
    concerned: "⚠️", triumphant: "👑",
};
const STATUS_LABEL = {
    idle: "En écoute",
    thinking: "Réflexion",
    sourcing: "Sourcing actif",
    enriching: "Enrichissement",
    writing: "Rédaction",
    sending: "Envoi",
    listening: "Écoute des réponses",
    learning: "Apprentissage",
    sleeping: "Repos",
    error: "Erreur",
};
const STATUS_ORDER = [
    "new", "enriched", "scored", "contacted",
    "replied", "engaged", "ready_to_pay", "won", "lost", "blacklisted"
];
const STATUS_LABEL_FR = {
    new: "Nouveaux", enriched: "Enrichis", scored: "Scorés",
    contacted: "Contactés", replied: "Répondu", engaged: "Engagés",
    ready_to_pay: "👑 Prêts à payer", won: "Gagnés", lost: "Perdus",
    blacklisted: "Blacklist",
};

const fmtTime = (iso) => {
    const d = new Date(iso);
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60)    return "à l'instant";
    if (diff < 3600)  return `${Math.floor(diff/60)}m`;
    if (diff < 86400) return `${Math.floor(diff/3600)}h`;
    return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
};

/* ---- Rendering ---- */
function renderState(s) {
    if (!s) return;
    const status = s.status || "idle";
    const mood = s.mood || "serene";

    els.orb.dataset.mood = mood;
    els.dot.dataset.status = status;
    els.label.textContent = STATUS_LABEL[status] || status;
    els.mood.textContent = MOOD_EMOJI[mood] || "🌌";
    els.activity.textContent = s.current_activity || `${agentName} attend le prochain cycle.`;
    els.target.textContent = s.current_target || "";

    els.cProspects.textContent = s.prospects_found_today ?? 0;
    els.cEmails.textContent    = s.emails_sent_today ?? 0;
    els.cReplies.textContent   = s.replies_today ?? 0;
    els.cAlerts.textContent    = s.alerts_sent_today ?? 0;

    if (s.last_heartbeat) {
        els.heartbeat.textContent = `heartbeat: ${fmtTime(s.last_heartbeat)}`;
    }
}

function eventEl(e) {
    const div = document.createElement("div");
    div.className = `event event-${e.severity || "info"}`;
    div.innerHTML = `
        <span class="event-emoji">${e.emoji || "✨"}</span>
        <div class="event-body">
            <div class="event-title">${escapeHtml(e.title)}</div>
            ${e.description ? `<div class="event-desc">${escapeHtml(e.description)}</div>` : ""}
        </div>
        <div class="event-time">${fmtTime(e.created_at)}</div>
    `;
    return div;
}

function prependEvent(e) {
    // empty state
    const empty = els.stream.querySelector(".empty");
    if (empty) empty.remove();

    els.stream.appendChild(eventEl(e));   // flex-direction: column-reverse → bas = haut visuel
    // limite à 80 events affichés
    while (els.stream.children.length > 80) {
        els.stream.removeChild(els.stream.firstChild);
    }
    els.streamSub.textContent = `${els.stream.children.length} events`;
}

function renderEvents(events) {
    els.stream.innerHTML = "";
    if (!events || events.length === 0) {
        els.stream.innerHTML = `<div class="empty">NOVA s'éveille...</div>`;
        return;
    }
    // events arrivent en ordre desc → on les itère à l'envers
    for (const e of [...events].reverse()) {
        els.stream.appendChild(eventEl(e));
    }
    els.streamSub.textContent = `${events.length} events`;
}

function renderPipeline(grouped) {
    els.pipeline.innerHTML = "";
    let totalShown = 0;
    for (const status of STATUS_ORDER) {
        const items = grouped[status] || [];
        if (items.length === 0 && !["new", "contacted", "ready_to_pay"].includes(status)) continue;
        totalShown += items.length;

        const col = document.createElement("div");
        col.className = "kanban-col";
        col.dataset.status = status;
        col.innerHTML = `
            <div class="kanban-col-header">
                <span class="kanban-col-title">${STATUS_LABEL_FR[status] || status}</span>
                <span class="kanban-col-count">${items.length}</span>
            </div>
        `;
        for (const p of items.slice(0, 12)) {
            const card = document.createElement("div");
            card.className = "kanban-card";
            const badges = [];
            if (p.score != null) badges.push(`<span class="badge badge-score">${p.score}</span>`);
            if (!p.has_website)  badges.push(`<span class="badge badge-nosite">pas de site</span>`);
            if (p.email)         badges.push(`<span class="badge badge-email">email</span>`);
            card.innerHTML = `
                <div class="kanban-card-name">${escapeHtml(p.name)}</div>
                <div class="kanban-card-meta">
                    ${[p.city, p.sector_normalized].filter(Boolean).map(escapeHtml).join(" · ")}
                </div>
                <div class="kanban-card-meta">${badges.join("")}</div>
            `;
            col.appendChild(card);
        }
        if (items.length > 12) {
            const more = document.createElement("div");
            more.className = "kanban-card";
            more.style.opacity = "0.6";
            more.style.textAlign = "center";
            more.innerHTML = `<div class="kanban-card-name">+ ${items.length - 12} de plus</div>`;
            col.appendChild(more);
        }
        els.pipeline.appendChild(col);
    }
    els.pipelineSub.textContent = `${totalShown} prospects`;
}

function renderConversations(convos) {
    els.convos.innerHTML = "";
    if (!convos || convos.length === 0) {
        els.convos.innerHTML = `<div class="empty">Aucune conversation pour l'instant.</div>`;
        return;
    }
    for (const c of convos) {
        const div = document.createElement("div");
        div.className = `convo-item ${c.direction}`;
        div.innerHTML = `
            <div class="convo-meta">
                <span class="convo-direction">${c.direction === "outbound" ? "→ envoyé" : "← reçu"}</span>
                <span class="convo-time">${fmtTime(c.sent_at)}</span>
            </div>
            <div class="convo-subject">${escapeHtml(c.subject || "(sans objet)")}</div>
            <div class="convo-snippet">${escapeHtml((c.body || "").slice(0, 160))}</div>
        `;
        els.convos.appendChild(div);
    }
    els.convosSub.textContent = `${convos.length} récentes`;
}

function renderStats(d) {
    if (!d) return;
    els.sProspects.textContent = d.totals?.prospects ?? "—";
    els.sEvents.textContent    = d.totals?.events ?? "—";
    els.sConvos.textContent    = d.totals?.conversations ?? "—";
    els.sAlerts.textContent    = d.totals?.alerts ?? "—";
}

/* ---- CONSOLE (Tool Calls en direct) ---- */
function fmtTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function toolCallEl(tc) {
    const div = document.createElement("div");
    div.className = `tool-call status-${tc.status || 'ok'}`;
    const duration = tc.duration_ms ? `${tc.duration_ms}ms` : "";
    div.innerHTML = `
        <div class="tool-call-time">${escapeHtml(fmtTime(tc.created_at))}</div>
        <div class="tool-call-body">
            <div class="tool-call-name">${escapeHtml(tc.tool_name)}</div>
            ${tc.input_summary ? `<div class="tool-call-input">→ ${escapeHtml(tc.input_summary)}</div>` : ""}
            ${tc.output_summary ? `<div class="tool-call-output">← ${escapeHtml(tc.output_summary)}</div>` : ""}
        </div>
        <div class="tool-call-duration">${duration}</div>
    `;
    return div;
}

function renderToolCalls(list) {
    if (!list || list.length === 0) {
        els.console.innerHTML = `<div class="empty">NOVA n'a pas encore utilisé d'outil.</div>`;
        els.consoleSub.textContent = "0 appel";
        return;
    }
    els.console.innerHTML = "";
    list.forEach(tc => els.console.appendChild(toolCallEl(tc)));
    els.consoleSub.textContent = `${list.length} derniers appels`;
}

function prependToolCall(tc) {
    const empty = els.console.querySelector(".empty");
    if (empty) empty.remove();
    els.console.prepend(toolCallEl(tc));
    // Cap à 50 entries
    while (els.console.children.length > 50) {
        els.console.removeChild(els.console.lastChild);
    }
}

/* ---- TASKS QUEUE ---- */
function taskCardEl(t) {
    const div = document.createElement("div");
    div.className = `task-card status-${t.status}`;
    const time = t.finished_at ? `Fini : ${fmtTime(t.finished_at)}` :
                 t.started_at  ? `Démarré : ${fmtTime(t.started_at)}` :
                 `Créé : ${fmtTime(t.created_at)}`;
    div.innerHTML = `
        <div class="task-row">
            <span class="task-type">${escapeHtml(t.type)}</span>
            <span class="task-status">${escapeHtml(t.status)}</span>
        </div>
        ${t.reason ? `<div class="task-reason">${escapeHtml(t.reason)}</div>` : ""}
        <div class="task-time">${escapeHtml(time)}${t.attempts > 1 ? ` · tentative ${t.attempts}/${t.max_attempts}` : ""}</div>
    `;
    return div;
}

function renderTasks(list) {
    if (!list || list.length === 0) {
        els.tasks.innerHTML = `<div class="empty">Aucune tâche en queue.</div>`;
        els.tasksSub.textContent = "0";
        return;
    }
    els.tasks.innerHTML = "";
    list.forEach(t => els.tasks.appendChild(taskCardEl(t)));
    const running = list.filter(t => t.status === "running").length;
    const pending = list.filter(t => t.status === "pending").length;
    els.tasksSub.textContent = `${pending} pending · ${running} running`;
}

/* ---- Bootstrap ---- */
async function loadAll() {
    try {
        const [stateR, eventsR, pipelineR, convosR, statsR, toolsR, tasksR] = await Promise.all([
            fetch("/api/state").then(r => r.json()),
            fetch("/api/recent-events?limit=80").then(r => r.json()),
            fetch("/api/pipeline").then(r => r.json()),
            fetch("/api/recent-conversations?limit=10").then(r => r.json()),
            fetch("/api/stats").then(r => r.json()),
            fetch("/api/recent-tool-calls?limit=30").then(r => r.json()).catch(() => []),
            fetch("/api/recent-tasks?limit=15").then(r => r.json()).catch(() => []),
        ]);
        renderState(stateR);
        renderEvents(eventsR);
        renderPipeline(pipelineR);
        renderConversations(convosR);
        renderStats(statsR);
        renderToolCalls(toolsR);
        renderTasks(tasksR);
    } catch (e) {
        console.error("loadAll failed:", e);
    }
}

/* ---- Realtime subscriptions ---- */
function subscribe() {
    supa.channel("nova-events")
        .on("postgres_changes",
            { event: "INSERT", schema: "public", table: "agent_events" },
            (payload) => {
                prependEvent(payload.new);
                if (payload.new.severity === "celebration") loadAll();
            })
        .subscribe();

    supa.channel("nova-state")
        .on("postgres_changes",
            { event: "*", schema: "public", table: "agent_state" },
            (payload) => renderState(payload.new))
        .subscribe();

    supa.channel("nova-tools")
        .on("postgres_changes",
            { event: "INSERT", schema: "public", table: "tool_calls" },
            (payload) => prependToolCall(payload.new))
        .subscribe();

    supa.channel("nova-tasks")
        .on("postgres_changes",
            { event: "*", schema: "public", table: "tasks" },
            () => fetch("/api/recent-tasks?limit=15").then(r => r.json()).then(renderTasks).catch(() => {}))
        .subscribe();
}

/* ---- Refresh périodique pour pipeline/conversations/stats (Realtime ne couvre que events+state) */
function startPolling() {
    setInterval(async () => {
        try {
            const [pipelineR, convosR, statsR] = await Promise.all([
                fetch("/api/pipeline").then(r => r.json()),
                fetch("/api/recent-conversations?limit=10").then(r => r.json()),
                fetch("/api/stats").then(r => r.json()),
            ]);
            renderPipeline(pipelineR);
            renderConversations(convosR);
            renderStats(statsR);
        } catch {}
    }, 20000);
}

/* ---- Helpers ---- */
function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/* ---- Boot ---- */
(async function boot() {
    await loadAll();
    subscribe();
    startPolling();
})();
