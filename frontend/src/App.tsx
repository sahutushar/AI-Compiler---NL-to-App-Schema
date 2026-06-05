import React, { useState, useCallback } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";
import {
  Zap, Code2, Database, Globe, Shield, LayoutDashboard,
  FileCode2, BarChart3, Wrench, ChevronRight, Cpu,
  CheckCircle2, Loader2, AlertTriangle, ExternalLink,
  Sparkles, Terminal, Layers
} from "lucide-react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";

// ── Constants ────────────────────────────────────────────────────────────────

const STAGES = [
  { key: "intent",   label: "Intent Extraction",  icon: <Sparkles size={11} /> },
  { key: "design",   label: "System Design",       icon: <Layers size={11} /> },
  { key: "schemas",  label: "Schema Generation",   icon: <Database size={11} /> },
  { key: "validate", label: "Validation & Repair", icon: <Shield size={11} /> },
  { key: "codegen",  label: "Code Generation",     icon: <Code2 size={11} /> },
];

const EXAMPLES = [
  "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
  "Create an e-commerce store with product listings, shopping cart, checkout with Stripe, and order tracking.",
  "Build a project management tool like Trello with boards, cards, team members, deadlines, and notifications.",
  "Create a hospital appointment booking system with doctors, patients, time slots, prescriptions, and billing.",
  "Build a SaaS invoicing tool with clients, invoices, payment reminders, recurring billing, and financial reports.",
  "Create a social media platform with profiles, posts, follow system, feed, and direct messages.",
];

const TABS = [
  { id: "full",    label: "Full Schema",  icon: <Layers size={13} /> },
  { id: "intent",  label: "Intent",       icon: <Sparkles size={13} /> },
  { id: "db",      label: "Database",     icon: <Database size={13} /> },
  { id: "api",     label: "API",          icon: <Globe size={13} /> },
  { id: "ui",      label: "UI",           icon: <LayoutDashboard size={13} /> },
  { id: "auth",    label: "Auth",         icon: <Shield size={13} /> },
  { id: "code",    label: "Code",         icon: <FileCode2 size={13} /> },
  { id: "metrics", label: "Metrics",      icon: <BarChart3 size={13} /> },
];

const FEATURES = [
  { icon: <Layers size={12} />,   label: "5-Stage Pipeline" },
  { icon: <Shield size={12} />,   label: "Auto Repair" },
  { icon: <Database size={12} />, label: "DB Schema" },
  { icon: <Globe size={12} />,    label: "REST API" },
  { icon: <Code2 size={12} />,    label: "Code Skeleton" },
];

type Status = "idle" | "loading" | "success" | "error";


// ── Component ────────────────────────────────────────────────────────────────

export default function App() {
  const [prompt, setPrompt]           = useState("");
  const [status, setStatus]           = useState<Status>("idle");
  const [activeStage, setActiveStage] = useState(-1);
  const [result, setResult]           = useState<any>(null);
  const [activeTab, setActiveTab]     = useState("full");
  const [error, setError]             = useState("");
  const [jobId, setJobId]             = useState("");

  const generate = useCallback(async () => {
    if (!prompt.trim() || status === "loading") return;

    setStatus("loading");
    setResult(null);
    setError("");
    setJobId("");
    setActiveTab("full");

    // Animate stages while waiting for response
    const stageTimer = (async () => {
      for (let i = 0; i < STAGES.length; i++) {
        setActiveStage(i);
        await new Promise((r) => setTimeout(r, 900));
      }
    })();

    try {
      const res = await axios.post(`${API_URL}/generate`, { prompt });
      await stageTimer;
      setResult(res.data);
      setJobId(res.data.job_id);
      setStatus("success");
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Connection refused — is the backend running?");
      setStatus("error");
    } finally {
      setActiveStage(-1);
    }
  }, [prompt, status]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) generate();
  };

  const getTabData = () => {
    if (!result) return null;
    switch (activeTab) {
      case "full":    return result.app_schema;
      case "intent":  return result.app_schema?.intent;
      case "db":      return result.app_schema?.database;
      case "api":     return result.app_schema?.api;
      case "ui":      return result.app_schema?.ui;
      case "auth":    return result.app_schema?.auth;
      case "code":    return result.generated_code;
      case "metrics": return result.metrics;
      default:        return result;
    }
  };

  const tabData  = getTabData();
  const hasErrors  = result?.validation_errors?.length > 0;
  const hasRepairs = result?.repair_log?.length > 0;

  // Summary counts for tab badges
  const counts: Record<string, number> = result ? {
    db:  result.app_schema?.database?.tables?.length ?? 0,
    api: result.app_schema?.api?.endpoints?.length ?? 0,
    ui:  result.app_schema?.ui?.pages?.length ?? 0,
  } : {};

  return (
    <div className="app">

      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="navbar-logo">
          <div className="logo-icon">
            <Cpu size={16} color="white" />
          </div>
          <span className="logo-text">AI<span>Compiler</span></span>
        </div>
        <span className="navbar-tag">Beta</span>

        <div className="navbar-right">
          <span style={{ fontSize: 12, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--green)", display: "inline-block" }} />
            Powered by Groq · Free
          </span>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-eyebrow">
          <Zap size={11} />
          AI-Powered App Compiler
        </div>
        <h1>
          Natural Language<br />
          <span className="gradient">→ Production App Schema</span>
        </h1>
        <p className="hero-sub">
          Describe any app in plain English. Our 5-stage pipeline extracts intent,
          designs the architecture, generates validated DB + API + UI schemas, and
          produces a runnable code skeleton.
        </p>

        {/* Pipeline visual */}
        <div className="pipeline-visual">
          {STAGES.map((s, i) => (
            <React.Fragment key={s.key}>
              <div className={`pv-step ${activeStage === i ? "active-step" : ""} ${status === "success" ? "done-step" : ""}`}>
                {status === "success"
                  ? <CheckCircle2 size={12} />
                  : activeStage === i
                  ? <Loader2 size={12} className="pulse" />
                  : s.icon}
                {s.label}
              </div>
              {i < STAGES.length - 1 && <span className="pv-arrow"><ChevronRight size={14} /></span>}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* ── Workspace ── */}
      <div className="workspace">

        {/* ── Sidebar ── */}
        <aside className="sidebar">

          {/* Prompt input */}
          <div className="sidebar-section">
            <div className="section-label">
              <Terminal size={11} />
              Describe your app
            </div>
            <textarea
              className="prompt-textarea"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Build a CRM with login, contacts, dashboard, role-based access, and payments. Admins can see analytics..."
              disabled={status === "loading"}
            />
            <div className="char-count">{prompt.length} chars · Ctrl+Enter to generate</div>
          </div>

          {/* Generate button */}
          <div className="sidebar-section">
            <button
              className="generate-btn"
              onClick={generate}
              disabled={status === "loading" || !prompt.trim()}
            >
              {status === "loading" ? (
                <><div className="spinner" /> Processing pipeline…</>
              ) : (
                <><Zap size={15} /> Generate App Schema</>
              )}
            </button>

            {/* Status + job id */}
            {result && (
              <div style={{ marginTop: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span className={`status-pill ${result.status}`}>
                  {result.status === "success"
                    ? <CheckCircle2 size={11} />
                    : <AlertTriangle size={11} />}
                  {result.status}
                </span>
                <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}>
                  #{jobId}
                </span>
              </div>
            )}

            {error && (
              <div className="alert alert-error" style={{ marginTop: 10 }}>
                <AlertTriangle size={13} style={{ flexShrink: 0, marginTop: 1 }} />
                {error}
              </div>
            )}
          </div>

          {/* Examples */}
          <div className="sidebar-section">
            <div className="section-label">
              <Sparkles size={11} />
              Quick Examples
            </div>
            <div className="example-chips">
              {EXAMPLES.map((ex, i) => (
                <button key={i} className="example-chip" onClick={() => setPrompt(ex)}>
                  {ex.slice(0, 80)}…
                </button>
              ))}
            </div>
          </div>

          {/* Pipeline stages */}
          <div className="sidebar-section">
            <div className="section-label">
              <Layers size={11} />
              Pipeline Stages
            </div>
            <div className="stage-list">
              {STAGES.map((s, i) => (
                <div
                  key={s.key}
                  className={`stage-row ${activeStage === i ? "s-active" : ""} ${status === "success" ? "s-done" : ""}`}
                >
                  <div className="stage-dot">
                    {status === "success"
                      ? <CheckCircle2 size={10} />
                      : activeStage === i
                      ? <Loader2 size={10} className="pulse" />
                      : i + 1}
                  </div>
                  {s.label}
                </div>
              ))}
            </div>
          </div>

          {/* Metrics */}
          {result?.metrics && (
            <div className="sidebar-section">
              <div className="section-label">
                <BarChart3 size={11} />
                Run Metrics
              </div>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-label">Latency</div>
                  <div className="metric-val c-blue">{result.metrics.total_latency_seconds}s</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Tokens</div>
                  <div className="metric-val">{result.metrics.total_tokens?.toLocaleString()}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Est. Cost</div>
                  <div className="metric-val c-blue">${result.metrics.estimated_cost_usd}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Repairs</div>
                  <div className={`metric-val ${result.metrics.repair_attempts > 0 ? "c-yellow" : "c-green"}`}>
                    {result.metrics.repair_attempts}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Validation errors */}
          {hasErrors && (
            <div className="sidebar-section">
              <div className="section-label">
                <AlertTriangle size={11} />
                Validation Errors ({result.validation_errors.length})
              </div>
              <div className="alert-list">
                {result.validation_errors.slice(0, 6).map((e: string, i: number) => (
                  <div key={i} className="alert alert-warning">
                    <AlertTriangle size={12} style={{ flexShrink: 0, marginTop: 1 }} />
                    {e}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Assumptions */}
          {result?.assumptions?.length > 0 && (
            <div className="sidebar-section">
              <div className="section-label">
                <Sparkles size={11} />
                Assumptions Made ({result.assumptions.length})
              </div>
              <div className="alert-list">
                {result.assumptions.map((a: string, i: number) => (
                  <div key={i} className="alert alert-success">
                    <CheckCircle2 size={12} style={{ flexShrink: 0, marginTop: 1 }} />
                    {a}
                  </div>
                ))}
              </div>
            </div>
          )}

        </aside>

        {/* ── Output Panel ── */}
        <div className="output-panel">

          {!result && status !== "loading" ? (
            <div className="empty-state">
              <div className="empty-icon-wrap">
                <Cpu size={30} color="var(--brand)" />
              </div>
              <div className="empty-title">Ready to compile</div>
              <div className="empty-sub">
                Enter a description of your app on the left and click
                "Generate App Schema" to run the full 5-stage pipeline.
              </div>
              <div className="feature-pills">
                {FEATURES.map((f, i) => (
                  <span key={i} className="feature-pill">
                    {f.icon} {f.label}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <>
              {/* Tab bar */}
              <div className="tab-bar">
                {TABS.map((t) => (
                  <button
                    key={t.id}
                    className={`tab-item ${activeTab === t.id ? "t-active" : ""}`}
                    onClick={() => setActiveTab(t.id)}
                  >
                    {t.icon}
                    {t.label}
                    {counts[t.id] ? (
                      <span className="tab-badge">{counts[t.id]}</span>
                    ) : null}
                  </button>
                ))}
              </div>

              {/* Editor area */}
              <div className="editor-area">
                {activeTab === "code" && result?.generated_code ? (
                  <div className="code-files-view">
                    {Object.entries(result.generated_code).map(([filename, code]) => (
                      <div key={filename} className="code-file-block">
                        <div className="code-file-header">
                          <span className="file-dot" />
                          {filename}
                        </div>
                        <Editor
                          height="320px"
                          language={
                            filename.endsWith(".py") ? "python" :
                            filename.endsWith(".md") ? "markdown" :
                            filename.endsWith(".env.example") ? "ini" : "plaintext"
                          }
                          value={code as string}
                          theme="vs-dark"
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            fontSize: 13,
                            fontFamily: "'JetBrains Mono', monospace",
                            lineNumbers: "on",
                            scrollBeyondLastLine: false,
                            padding: { top: 12, bottom: 12 },
                          }}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <Editor
                    height="100%"
                    language="json"
                    value={
                      status === "loading"
                        ? `// Pipeline running — Stage ${activeStage + 1}: ${STAGES[activeStage]?.label ?? ""}...`
                        : tabData
                        ? JSON.stringify(tabData, null, 2)
                        : "// No data"
                    }
                    theme="vs-dark"
                    options={{
                      readOnly: true,
                      minimap: { enabled: false },
                      fontSize: 13,
                      fontFamily: "'JetBrains Mono', monospace",
                      wordWrap: "on",
                      scrollBeyondLastLine: false,
                      padding: { top: 12, bottom: 12 },
                      lineNumbers: "on",
                    }}
                  />
                )}
              </div>

              {/* Repair log strip */}
              {hasRepairs && (
                <div className="log-strip">
                  <div className="log-header">
                    <Wrench size={11} />
                    Repair Log ({result.repair_log.length} fix{result.repair_log.length > 1 ? "es" : ""} applied)
                  </div>
                  <div className="log-items">
                    {result.repair_log.map((r: string, i: number) => (
                      <div key={i} className="log-item repair">✓ {r}</div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* ── Footer ── */}
      <footer className="footer">
        <span>AI Compiler · Natural Language → App Schema</span>
        <div className="footer-links">
          <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">
            API Docs <ExternalLink size={10} style={{ display: "inline", verticalAlign: "middle" }} />
          </a>
          <a href={`${API_URL}/metrics`} target="_blank" rel="noreferrer">
            Metrics <ExternalLink size={10} style={{ display: "inline", verticalAlign: "middle" }} />
          </a>
          <a href={`${API_URL}/health`} target="_blank" rel="noreferrer">Health</a>
        </div>
      </footer>


    </div>
  );
}
