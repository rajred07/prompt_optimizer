import React, { useState, useEffect } from 'react';
import { Settings, BarChart2, Zap, Scale, FileText, CheckCircle, AlertTriangle, Sparkles, Navigation } from 'lucide-react';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Sparkles className="logo-icon" size={28} />
          <span>Optimizer</span>
        </div>
        
        <nav>
          <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <BarChart2 size={20} /> Dashboard
          </button>
          <button className={`nav-item ${activeTab === 'evaluate' ? 'active' : ''}`} onClick={() => setActiveTab('evaluate')}>
            <CheckCircle size={20} /> Evaluator
          </button>
          <button className={`nav-item ${activeTab === 'optimize' ? 'active' : ''}`} onClick={() => setActiveTab('optimize')}>
            <Zap size={20} /> Optimizer
          </button>
          <button className={`nav-item ${activeTab === 'compare' ? 'active' : ''}`} onClick={() => setActiveTab('compare')}>
            <Scale size={20} /> A/B Compare
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'evaluate' && <EvaluatorView />}
        {activeTab === 'optimize' && <OptimizerView />}
        {activeTab === 'compare' && <CompareView />}
      </main>
    </div>
  );
}

// ─── DASHBOARD VIEW ─────────────────────────────────────────────────────────

function DashboardView() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/stats`)
      .then(res => res.json())
      .then(data => setStats(data.data))
      .catch(err => console.error(err));
  }, []);

  if (!stats) return <Loading />;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Executive Dashboard</h1>
        <p className="page-subtitle">Track your prompt engineering performance.</p>
      </div>

      <div className="grid-4">
        <div className="glass-card">
          <div style={{color: 'var(--text-muted)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase'}}>Total Optimizations</div>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold'}}>{stats.total_optimizations}</div>
        </div>
        <div className="glass-card">
          <div style={{color: 'var(--text-muted)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase'}}>Avg Score Jump</div>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)'}}>+{stats.average_improvement}</div>
        </div>
        <div className="glass-card">
          <div style={{color: 'var(--text-muted)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase'}}>Tests Run</div>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold'}}>{stats.total_tests}</div>
        </div>
        <div className="glass-card">
          <div style={{color: 'var(--text-muted)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase'}}>Best Domain</div>
          <div style={{fontSize: '1.8rem', fontWeight: 'bold', color: 'var(--accent)', textTransform: 'capitalize'}}>{stats.best_domain}</div>
        </div>
      </div>
    </div>
  );
}

// ─── EVALUATOR VIEW ─────────────────────────────────────────────────────────

function EvaluatorView() {
  const [prompt, setPrompt] = useState('You are a customer support agent. Help the user.');
  const [domain, setDomain] = useState('customer_support');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, domain })
      });
      const data = await res.json();
      setResult(data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Prompt Evaluator</h1>
        <p className="page-subtitle">Score your prompt scientifically across 7 dimensions.</p>
      </div>

      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="input-group">
          <label className="input-label">Domain</label>
          <select className="select-field" value={domain} onChange={e => setDomain(e.target.value)}>
            <option value="customer_support">Customer Support</option>
            <option value="education">Education</option>
            <option value="healthcare">Healthcare</option>
            <option value="finance">Finance</option>
            <option value="general">General</option>
          </select>
        </div>
        <div className="input-group">
          <label className="input-label">System Prompt</label>
          <textarea 
            className="textarea-field" 
            rows={4} 
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
          />
        </div>
        <button className="btn btn-primary" onClick={handleEvaluate} disabled={loading}>
          {loading ? <span className="loader"></span> : <><CheckCircle size={18}/> Analyze Prompt</>}
        </button>
      </div>

      {result && (
        <div className="grid-2 animate-fade-in">
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1.2rem' }}>Quality Score</h3>
              <div className="score-circle" style={{ '--score': result.overall_score }}>
                <span className="score-number" style={{ color: result.overall_score < 50 ? 'var(--danger)' : 'white' }}>{result.overall_score}</span>
                <span className="score-grade">Grade: {result.grade}</span>
              </div>
            </div>

            {Object.entries(result.dimensions).map(([key, data]) => {
              const color = data.score > 7 ? 'var(--success)' : data.score > 4 ? 'var(--warning)' : 'var(--danger)';
              return (
                <div key={key} className="progress-container">
                  <div className="progress-header">
                    <span style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>
                    <span style={{ color }}>{data.score}/10</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${data.score * 10}%`, background: color }}></div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="glass-card">
            <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Feedback Analysis</h3>
            
            <div style={{ marginBottom: '24px' }}>
              <div style={{ color: 'var(--success)', fontWeight: '600', marginBottom: '8px' }}>Strengths</div>
              {result.strengths.map((str, i) => <div key={i} className="pill pill-strength">{str}</div>)}
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <div style={{ color: 'var(--danger)', fontWeight: '600', marginBottom: '8px' }}>Weaknesses</div>
              {result.weaknesses.map((w, i) => <div key={i} className="pill pill-weakness">{w}</div>)}
            </div>

            <div>
              <div style={{ color: 'var(--accent)', fontWeight: '600', marginBottom: '8px' }}>Actionable Suggestions</div>
              <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                {result.improvement_suggestions.map((s, i) => <li key={i} style={{marginBottom:'4px'}}>{s}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── OPTIMIZER VIEW ─────────────────────────────────────────────────────────

function OptimizerView() {
  const [prompt, setPrompt] = useState('You are a customer support agent. Help the user.');
  const [domain, setDomain] = useState('customer_support');
  const [goal, setGoal] = useState('Make it highly professional and empathetic');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleOptimize = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, domain, optimization_goal: goal })
      });
      const data = await res.json();
      setResult(data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">AI Optimizer</h1>
        <p className="page-subtitle">Let Gemini rewrite your prompt for maximum efficiency.</p>
      </div>

      <div className="grid-2">
        <div className="glass-card">
          <div className="input-group">
            <label className="input-label">Original Prompt</label>
            <textarea 
              className="textarea-field" 
              rows={4} 
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label className="input-label">Optimization Goal</label>
            <input 
              className="input-field" 
              type="text"
              value={goal}
              onChange={e => setGoal(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={handleOptimize} disabled={loading}>
            {loading ? <span className="loader"></span> : <><Zap size={18}/> Auto Improve</>}
          </button>
        </div>

        {result && (
          <div className="glass-card animate-fade-in" style={{ borderColor: 'var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ color: 'var(--primary)', fontWeight: 'bold' }}>🚀 +{result.improvement} Points Improvement</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{result.original_score} ➔ {result.optimized_score}</div>
            </div>
            
            <div className="code-block" style={{ marginBottom: '16px' }}>
              {result.optimized_prompt}
            </div>

            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>AI Reasoning:</strong> {result.explanation}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── COMPARE VIEW ───────────────────────────────────────────────────────────

function CompareView() {
  const [promptA, setPromptA] = useState('You are a helpful assistant.');
  const [promptB, setPromptB] = useState('You are an expert, highly professional assistant. Answer directly.');
  const [testInput, setTestInput] = useState('I need help with my account.');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCompare = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_a: promptA, prompt_b: promptB, test_input: testInput, domain: 'general' })
      });
      const data = await res.json();
      setResult(data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">A/B Comparator</h1>
        <p className="page-subtitle">Test two prompts simultaneously with a simulated user message.</p>
      </div>

      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="grid-2">
          <div className="input-group">
            <label className="input-label" style={{color: '#ff4b4b'}}>Prompt A</label>
            <textarea className="textarea-field" rows={3} value={promptA} onChange={e => setPromptA(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label" style={{color: '#0575e6'}}>Prompt B</label>
            <textarea className="textarea-field" rows={3} value={promptB} onChange={e => setPromptB(e.target.value)} />
          </div>
        </div>
        <div className="input-group">
          <label className="input-label">Simulated User Message</label>
          <input className="input-field" type="text" value={testInput} onChange={e => setTestInput(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={handleCompare} disabled={loading} style={{width: '100%'}}>
           {loading ? <span className="loader"></span> : <><Scale size={18}/> Run Simulation</>}
        </button>
      </div>

      {result && (
        <div className="glass-card animate-fade-in" style={{ border: `2px solid ${result.winner === 'A' ? 'var(--danger)' : 'var(--accent)'}` }}>
          <h2 style={{ textAlign: 'center', marginBottom: '24px' }}>
            Winner: Prompt {result.winner} 👑
          </h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '32px' }}>"{result.winner_reason}"</p>

          <div className="grid-2">
            <div style={{ padding: '16px', background: 'rgba(255,75,75,0.05)', borderRadius: '8px' }}>
              <div style={{ fontWeight: 'bold', color: 'var(--danger)', marginBottom: '8px' }}>Response A (Score: {result.score_a})</div>
              <div style={{ fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{result.response_a}</div>
            </div>
            <div style={{ padding: '16px', background: 'rgba(5,117,230,0.05)', borderRadius: '8px' }}>
              <div style={{ fontWeight: 'bold', color: 'var(--accent)', marginBottom: '8px' }}>Response B (Score: {result.score_b})</div>
              <div style={{ fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{result.response_b}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── UTILS ──────────────────────────────────────────────────────────────────

function Loading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
      <div className="loader" style={{ width: '48px', height: '48px', borderWidth: '4px' }}></div>
    </div>
  );
}
