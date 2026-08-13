import { useCallback, useEffect, useRef, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Check,
  ChevronLeft,
  Clock3,
  Code2,
  Eye,
  EyeOff,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Maximize2,
  Play,
  Search,
  ShieldCheck,
  Trophy,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import hero from "./assets/hero.png";
import luxmorLogo from "./assets/WhatsA mail.jpeg";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "/api";
const roles = [
  ["data-analyst", "Data Analyst", "SQL, statistics & insights"],
  ["frontend-developer", "Frontend Developer", "React, JavaScript, HTML & CSS"],
  [
    "backend-developer",
    "Backend Developer",
    "APIs, databases & server-side systems",
  ],
  [
    "full-stack-developer",
    "Full Stack Developer",
    "Frontend, backend & integration",
  ],
  ["software-developer", "Software Developer", "DSA, systems & engineering"],
  ["cloud-engineer", "Cloud Engineer", "Infrastructure, reliability & cloud"],
];
const locations = [
  ["chennai", "Chennai"],
  ["bengaluru", "Bengaluru"],
  ["hyderabad", "Hyderabad"],
];
const hiringStatuses = [
  ["assessment_pending", "Assessment pending"],
  ["assessment_completed", "Assessment completed"],
  ["technical_scheduled", "Technical scheduled"],
  ["technical_completed", "Technical completed"],
  ["hr_scheduled", "HR scheduled"],
  ["hr_completed", "HR completed"],
  ["on_hold", "On hold"],
  ["selected", "Selected"],
  ["rejected", "Rejected"],
];
const roundMeta = {
  aptitude: {
    title: "Cognitive aptitude",
    caption: "60 questions · 60 minutes",
    icon: BarChart3,
  },
  technical: {
    title: "Role knowledge",
    caption: "20 questions · 20 minutes",
    icon: UserRound,
  },
  coding: {
    title: "Coding challenge",
    caption: "2 problems · 40 minutes",
    icon: Code2,
  },
};
const languageLabels = {
  react: "React (JSX)",
  python: "Python 3",
  javascript: "JavaScript (Node.js)",
  typescript: "TypeScript",
  java: "Java 17",
};

function reactPreviewDocument(code) {
  const candidateSource = `${code}\nwindow.__CandidateApp = typeof App !== 'undefined' ? App : null;`;
  const serialized = JSON.stringify(candidateSource).replace(/</g, "\\u003c");
  return `<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>html,body,#root{margin:0;min-height:100%;font-family:Inter,Arial,sans-serif}.preview-loading,.preview-error{padding:24px;color:#5d5870}.preview-error{color:#b42335;white-space:pre-wrap}</style></head>
<body><div id="root"><div class="preview-loading">Loading React preview...</div></div>
<script>window.addEventListener('error',function(e){document.getElementById('root').innerHTML='<div class="preview-error">'+String(e.message).replace(/</g,'&lt;')+'</div>';});</script>
<script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script>
try {
  const source = ${serialized};
  const compiled = Babel.transform(source, { presets: ['react'] }).code;
  (0, eval)(compiled);
  if (!window.__CandidateApp) throw new Error('Keep your component named App.');
  ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(window.__CandidateApp));
} catch (error) {
  document.getElementById('root').innerHTML = '<div class="preview-error">'+String(error.message).replace(/</g,'&lt;')+'</div>';
}
</script></body></html>`;
}

async function request(path, options = {}, admin = false) {
  const token = localStorage.getItem(admin ? "adminToken" : "candidateToken");
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(data.detail || "Something went wrong. Please try again.");
  return data;
}

function Brand({ light = false }) {
  return (
    <div className={`brand ${light ? "brand-light" : ""}`}>
      <img className="brand-logo" src={luxmorLogo} alt="Luxmor AI" />
      <span>
        Luxmor <span>TalentForge</span>
      </span>
    </div>
  );
}

function Landing() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    college: "",
    designation: "",
    address: "",
    role: "",
    preferred_location: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [roleText, setRoleText] = useState("");
  const set = (key) => (event) =>
    setForm({ ...form, [key]: event.target.value });
  const submit = async (event) => {
    event.preventDefault();
    if (!form.role) {
      setError(
        "Choose a job profile from the suggestions so we can assign the correct technical questions.",
      );
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await request("/candidates/register/", {
        method: "POST",
        body: JSON.stringify(form),
      });
      localStorage.setItem("candidateToken", data.token);
      navigate("/portal");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <main className="landing-page">
      <div className="landing">
        <section className="intro-panel">
        <Brand light />
        <div className="intro-copy">
          <span className="eyebrow light">
            <span /> Campus recruitment 2026
          </span>
          <h1>
            Luxmor TalentForge
            <br />
            campus hiring <em>starts here.</em>
          </h1>
          <p>
            Luxmor AI Technologies&apos; secure online assessment portal helps
            campus candidates show how they think, what they know, and what
            they can build.
          </p>
          <div className="journey-line">
            <div>
              <b>01</b>
              <span>Aptitude</span>
            </div>
            <i />
            <div>
              <b>02</b>
              <span>Role skills</span>
            </div>
            <i />
            <div>
              <b>03</b>
              <span>Code</span>
            </div>
          </div>
        </div>
        <img src={hero} className="hero-shape" alt="" />
        <div className="secure-note">
          <ShieldCheck size={17} />
          <span>
            <b>Secure assessment</b>
            <small>Proctored & time-bound</small>
          </span>
        </div>
        </section>
        <section className="form-panel">
        <div className="form-wrap">
          <div className="mobile-brand">
            <Brand />
          </div>
          <span className="step-label">Candidate registration</span>
          <h2>Tell us about yourself</h2>
          <p className="subtext">
            Enter your details exactly as they appear on your college records.
          </p>
          <form onSubmit={submit}>
            <label>
              Full name
              <input
                required
                value={form.name}
                onChange={set("name")}
                placeholder="e.g. Arjun Sharma"
              />
            </label>
            <div className="field-row">
              <label>
                Email address
                <input
                  required
                  type="email"
                  value={form.email}
                  onChange={set("email")}
                  placeholder="you@college.edu"
                />
              </label>
              <label>
                Phone number
                <input
                  required
                  value={form.phone}
                  onChange={set("phone")}
                  pattern="[0-9+ -]{8,20}"
                  placeholder="+91 98765 43210"
                />
              </label>
            </div>
            <div className="field-row">
              <label>
                College / University
                <input
                  required
                  value={form.college}
                  onChange={set("college")}
                  placeholder="Institution name"
                />
              </label>
              <label>
                Degree / designation
                <input
                  required
                  value={form.designation}
                  onChange={set("designation")}
                  placeholder="e.g. B.Tech CSE"
                />
              </label>
            </div>
            <label>
              Address
              <textarea
                required
                rows="2"
                value={form.address}
                onChange={set("address")}
                placeholder="Current address"
              />
            </label>
            <div className="field-row">
              <label>
                Job profile you are interested in
                <input
                  required
                  list="job-profile-options"
                  value={roleText}
                  onChange={(event) => {
                    const text = event.target.value;
                    const normalized = text.toLowerCase().replace(/[\s-]/g, "");
                    const match = roles.find(
                      ([, name]) =>
                        name.toLowerCase().replace(/[\s-]/g, "") === normalized,
                    );
                    setRoleText(text);
                    setForm((current) => ({
                      ...current,
                      role: match?.[0] || "",
                    }));
                  }}
                  placeholder="Type Frontend, Backend, Data Analyst…"
                />
                <datalist id="job-profile-options">
                  {roles.map(([value, name]) => (
                    <option value={name} key={value} />
                  ))}
                </datalist>
                <small className="field-help">
                  Start typing and choose the closest profile. Your technical
                  and coding questions will follow this selection.
                </small>
              </label>
              <label>
                Preferred work location
                <select
                  required
                  value={form.preferred_location}
                  onChange={set("preferred_location")}
                >
                  <option value="">Select a location</option>
                  {locations.map(([value, name]) => (
                    <option value={value} key={value}>
                      {name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <p className="location-note">
              Preferred work location is collected for planning and may vary
              based on business requirements.
            </p>
            {error && <div className="error-box">{error}</div>}
            <button className="primary wide" disabled={loading}>
              {loading ? (
                "Creating your profile…"
              ) : (
                <>
                  Continue to assessment <ArrowRight size={18} />
                </>
              )}
            </button>
            <p className="consent">
              <LockKeyhole size={13} /> Your information is encrypted and used
              only for this recruitment drive.
            </p>
          </form>
        </div>
        <button className="admin-link" onClick={() => navigate("/admin")}>
          <LayoutDashboard size={15} /> Recruiter access
        </button>
        </section>
      </div>
      <section className="seo-content" aria-labelledby="about-talentforge">
        <div className="seo-heading">
          <span className="eyebrow">
            <span /> Official Luxmor recruitment portal
          </span>
          <h2 id="about-talentforge">What is Luxmor TalentForge?</h2>
          <p>
            Luxmor TalentForge is Luxmor AI Technologies&apos; secure campus
            recruitment and online assessment portal. It brings candidate
            registration, timed evaluations, practical coding, and recruiter
            review into one focused hiring experience.
          </p>
        </div>
        <div className="seo-answers">
          <article>
            <h3>What assessments are included in Luxmor TalentForge?</h3>
            <p>
              Candidates complete a 60-question aptitude assessment, 20
              role-specific technical questions, and two practical coding
              challenges aligned with their chosen profile.
            </p>
          </article>
          <article>
            <h3>Which job profiles does Luxmor TalentForge support?</h3>
            <p>
              Data Analyst, Frontend Developer, Backend Developer, Full Stack
              Developer, Software Developer, and Cloud Engineer profiles are
              supported.
            </p>
          </article>
          <article>
            <h3>Are candidate results public?</h3>
            <p>
              No. Assessment scores, integrity records, and coding results are
              confidential and available only to authorized Luxmor recruitment
              staff.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}

function Portal() {
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    request("/candidates/me/")
      .then(setCandidate)
      .catch((e) => {
        setError(e.message);
        localStorage.removeItem("candidateToken");
      });
  }, []);
  if (error) return <Navigate to="/" replace />;
  if (!candidate) return <Loader />;
  const completed = Object.fromEntries(
    candidate.rounds.map((r) => [r.round_type, r]),
  );
  const current =
    candidate.status === "registered" ? "aptitude" : candidate.status;
  const start = (type) => navigate(`/instructions/${type}`);
  return (
    <div className="portal-page">
      <header className="topbar">
        <Brand />
        <div className="top-actions">
          <span className="candidate-chip">
            <span>{candidate.name[0]}</span>
            {candidate.name}
          </span>
          <button
            className="icon-button"
            title="Sign out"
            onClick={() => {
              localStorage.removeItem("candidateToken");
              navigate("/");
            }}
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>
      <main className="portal-shell">
        <section className="welcome">
          <div>
            <span className="eyebrow">
              <span /> Assessment centre
            </span>
            <h1>Good luck, {candidate.name.split(" ")[0]}.</h1>
            <p>
              You’re applying for <b>{candidate.role_label}</b>. Complete all
              three stages in one focused sitting.
            </p>
          </div>
          <div className="application-id">
            <span>Application ID</span>
            <b>{candidate.id.slice(0, 8).toUpperCase()}</b>
          </div>
        </section>
        {candidate.status === "completed" ? (
          <Completion candidate={candidate} />
        ) : (
          <>
            <div className="progress-head">
              <h3>Your assessment journey</h3>
              <span>
                {
                  candidate.rounds.filter((r) => r.status !== "in_progress")
                    .length
                }{" "}
                of 3 stages complete
              </span>
            </div>
            <div className="round-grid">
              {Object.entries(roundMeta).map(([type, meta], index) => {
                const record = completed[type];
                const done = record && record.status !== "in_progress";
                const active = current === type;
                const Icon = meta.icon;
                return (
                  <article
                    className={`round-card ${active ? "active" : ""} ${done ? "done" : ""}`}
                    key={type}
                  >
                    <div className="round-top">
                      <span className="round-number">
                        {done ? <Check size={18} /> : `0${index + 1}`}
                      </span>
                      <span
                        className={`status-pill ${done ? "success" : active ? "ready" : ""}`}
                      >
                        {done ? "Completed" : active ? "Ready" : "Locked"}
                      </span>
                    </div>
                    <Icon className="round-icon" size={30} />
                    <h3>{meta.title}</h3>
                    <p>{meta.caption}</p>
                    {done ? (
                      <div className="score-line private-result">
                        <Check size={17} />
                        <b>Response submitted</b>
                      </div>
                    ) : (
                      <button disabled={!active} onClick={() => start(type)}>
                        {record
                          ? "Resume stage"
                          : active
                            ? "View instructions"
                            : "Complete previous stage"}
                        {active && <ArrowRight size={16} />}
                      </button>
                    )}
                  </article>
                );
              })}
            </div>
            <div className="rules-strip">
              <ShieldCheck />
              <div>
                <b>Before you begin</b>
                <span>
                  The test enters fullscreen. Keep this tab active, allow
                  pop-ups, and ensure a stable internet connection.
                </span>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function Completion({ candidate }) {
  return (
    <section className="completion">
      <div className="trophy">
        <Trophy />
      </div>
      <span className="eyebrow">
        <span /> Assessment submitted
      </span>
      <h2>You did it, {candidate.name.split(" ")[0]}!</h2>
      <p>
        Your responses and code have been securely submitted. The recruitment
        team will contact shortlisted candidates.
      </p>
      <div className="result-private-note">
        <LockKeyhole size={18} />
        <span>
          <b>Results are confidential</b>Your assessment results are available
          only to the Luxmor recruitment team.
        </span>
      </div>
    </section>
  );
}

function Instructions() {
  const { type } = useParams();
  const navigate = useNavigate();
  const meta = roundMeta[type];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  if (!meta) return <Navigate to="/portal" />;
  const begin = async () => {
    setLoading(true);
    setError("");
    try {
      await request(`/rounds/${type}/start/`, { method: "POST" });
      await document.documentElement.requestFullscreen();
      navigate(`/assessment/${type}`);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };
  return (
    <div className="instruction-page">
      <div className="instruction-card">
        <Brand />
        <div className="instruction-icon">
          <meta.icon size={34} />
        </div>
        <span className="eyebrow">
          <span /> Stage instructions
        </span>
        <h1>{meta.title}</h1>
        <p className="lead">
          {meta.caption}. Read each question carefully—the timer begins as soon
          as you start.
        </p>
        <div className="instruction-list">
          <div>
            <Clock3 />
            <span>
              <b>One question at a time</b>
              <small>
                {type === "coding"
                  ? "20 minutes per coding problem"
                  : "60 seconds per question"}
                . Questions cannot be revisited.
              </small>
            </span>
          </div>
          <div>
            <Maximize2 />
            <span>
              <b>Fullscreen is mandatory</b>
              <small>
                Leaving fullscreen or changing tabs is recorded as a proctoring
                violation.
              </small>
            </span>
          </div>
          <div>
            <ShieldCheck />
            <span>
              <b>Responses auto-save</b>
              <small>
                At zero, the current unanswered question is submitted
                automatically.
              </small>
            </span>
          </div>
        </div>
        {error && <div className="error-box">{error}</div>}
        <button className="primary wide" onClick={begin} disabled={loading}>
          {loading ? (
            "Preparing stage…"
          ) : (
            <>
              <Play size={18} /> Enter fullscreen & begin
            </>
          )}
        </button>
        <button className="text-button" onClick={() => navigate("/portal")}>
          Return to assessment centre
        </button>
      </div>
    </div>
  );
}

function Assessment() {
  const { type } = useParams();
  const navigate = useNavigate();
  const [state, setState] = useState(null);
  const [selected, setSelected] = useState(null);
  const [code, setCode] = useState("");
  const [previewCode, setPreviewCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [remaining, setRemaining] = useState(0);
  const [blocked, setBlocked] = useState(!document.fullscreenElement);
  const [busy, setBusy] = useState(false);
  const [runResults, setRunResults] = useState(null);
  const [error, setError] = useState("");
  const submitting = useRef(false);
  const load = useCallback(async () => {
    try {
      const data = await request(`/rounds/${type}/state/`);
      setState(data);
      setRemaining(data.remaining_seconds || 0);
      if (data.question?.starter_code) {
        const values = (data.question.languages || []).map((item) =>
          typeof item === "string" ? item : item.value,
        );
        const nextLanguage = values.includes(language) ? language : values[0];
        if (nextLanguage && nextLanguage !== language)
          setLanguage(nextLanguage);
        const starter = data.question.starter_code[nextLanguage] || "";
        setCode(starter);
        setPreviewCode(starter);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [type, language]);
  useEffect(() => {
    load();
  }, [load]);
  useEffect(() => {
    const timer = setTimeout(() => setPreviewCode(code), 500);
    return () => clearTimeout(timer);
  }, [code]);
  const logEvent = useCallback(
    (event_type) =>
      request("/proctor/events/", {
        method: "POST",
        body: JSON.stringify({
          event_type,
          details: { path: location.pathname },
        }),
      })
        .then((data) =>
          setState((s) => (s ? { ...s, violations: data.violations } : s)),
        )
        .catch(() => {}),
    [],
  );
  useEffect(() => {
    const fs = () => {
      const exited = !document.fullscreenElement;
      setBlocked(exited);
      if (exited) logEvent("fullscreen_exit");
    };
    const visibility = () => {
      if (document.hidden) logEvent("tab_hidden");
    };
    document.addEventListener("fullscreenchange", fs);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      document.removeEventListener("fullscreenchange", fs);
      document.removeEventListener("visibilitychange", visibility);
    };
  }, [logEvent]);
  const submit = useCallback(async () => {
    if (!state?.question || submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    const submittedState = state;
    const advancedOptimistically = Boolean(state.next_question);
    try {
      const body =
        type === "coding"
          ? { question_id: state.question.id, code, language }
          : { question_id: state.question.id, selected_option: selected };
      if (state.next_question) {
        setState({
          ...state,
          current: state.current + 1,
          question: state.next_question,
          next_question: null,
          remaining_seconds: state.question_seconds,
        });
        setRemaining(state.question_seconds);
        setSelected(null);
        setRunResults(null);
        if (state.next_question.starter_code) {
          const nextValues = (state.next_question.languages || []).map((item) =>
            typeof item === "string" ? item : item.value,
          );
          const nextLanguage = nextValues.includes(language)
            ? language
            : nextValues[0];
          if (nextLanguage && nextLanguage !== language)
            setLanguage(nextLanguage);
          setCode(state.next_question.starter_code[nextLanguage] || "");
        }
      }
      const data = await request(`/rounds/${type}/answer/`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (!advancedOptimistically) setSelected(null);
      setRunResults(null);
      setState(data.state);
      setRemaining(data.state.remaining_seconds || 0);
      if (data.state.question?.starter_code) {
        const values = (data.state.question.languages || []).map((item) =>
          typeof item === "string" ? item : item.value,
        );
        const nextLanguage = values.includes(language) ? language : values[0];
        if (nextLanguage && nextLanguage !== language)
          setLanguage(nextLanguage);
        setCode(data.state.question.starter_code[nextLanguage] || "");
      }
      if (data.state.status !== "in_progress") {
        if (document.fullscreenElement)
          await document.exitFullscreen().catch(() => {});
        navigate("/portal");
      }
    } catch (e) {
      setError(e.message);
      if (e.message.includes("advanced")) load();
      else {
        setState(submittedState);
        setRemaining(submittedState.remaining_seconds || 0);
        setSelected(selected);
      }
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  }, [state, type, code, language, selected, navigate, load]);
  const submitRef = useRef(submit);
  submitRef.current = submit;
  const activeQuestionId = state?.question?.id;
  const assessmentActive = state?.status === "in_progress";
  useEffect(() => {
    if (!assessmentActive) return;
    const tick = setInterval(
      () =>
        setRemaining((value) => {
          if (value <= 1) {
            clearInterval(tick);
            setTimeout(() => submitRef.current(), 0);
            return 0;
          }
          return value - 1;
        }),
      1000,
    );
    return () => clearInterval(tick);
  }, [activeQuestionId, assessmentActive]);
  const changeLanguage = (value) => {
    setLanguage(value);
    setCode(state.question.starter_code[value] || "");
  };
  const run = async () => {
    setBusy(true);
    setError("");
    try {
      const data = await request(`/rounds/${type}/run/`, {
        method: "POST",
        body: JSON.stringify({ code, language }),
      });
      setRunResults(data.results);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  if (!state) return <Loader />;
  if (state.status !== "in_progress") return <Navigate to="/portal" />;
  const q = state.question;
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const urgent = remaining <= (type === "coding" ? 120 : 10);
  return (
    <div className={`test-page ${type === "coding" ? "coding-page" : ""}`}>
      <header className="test-header">
        <Brand />
        <div className="test-title">
          <b>{roundMeta[type].title}</b>
          <span>
            Question {state.current + 1} of {state.total}
          </span>
        </div>
        <div className={`timer ${urgent ? "urgent" : ""}`}>
          <Clock3 size={18} />
          <b>
            {String(minutes).padStart(2, "0")}:
            {String(seconds).padStart(2, "0")}
          </b>
        </div>
        <div className="violation">
          <ShieldCheck size={16} />
          {state.violations} violations
        </div>
      </header>
      <div className="test-progress">
        <i style={{ width: `${((state.current + 1) / state.total) * 100}%` }} />
      </div>
      {type === "coding" ? (
        <main className="coding-workspace">
          <section className="problem-pane">
            <span className="question-count">Problem {state.current + 1}</span>
            <h2>{q.prompt.split("\n")[0]}</h2>
            <p className="problem-copy">
              {q.prompt.split("\n").slice(2).join("\n")}
            </p>
            <h4>
              {q.workspace === "react"
                ? "Evaluation checklist"
                : "Sample test cases"}
            </h4>
            {q.workspace === "react" ? (
              <div className="ui-checklist">
                {q.visible_tests.map((item, index) => (
                  <div key={item.label}>
                    <Check size={15} />
                    <span>{index + 1}. {item.label}</span>
                  </div>
                ))}
              </div>
            ) : (
              q.visible_tests.map((t, i) => (
                <div className="sample" key={i}>
                  <span>Input</span>
                  <pre>{t.input}</pre>
                  <span>Expected output</span>
                  <pre>{t.output}</pre>
                </div>
              ))
            )}
          </section>
          <section className={`editor-pane ${q.workspace === "react" ? "react-editor-pane" : ""}`}>
            <div className="editor-bar">
              <select
                value={language}
                onChange={(e) => changeLanguage(e.target.value)}
              >
                {q.languages.map((item) => {
                  const value = typeof item === "string" ? item : item.value;
                  const label =
                    typeof item === "string"
                      ? languageLabels[item] || item
                      : item.label;
                  return (
                    <option value={value} key={value}>
                      {label}
                    </option>
                  );
                })}
              </select>
              <span>
                {q.workspace === "react" ? "React component / live preview" : "stdin / stdout"}
              </span>
            </div>
            <textarea
              spellCheck="false"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="code-editor"
            />
            {q.workspace === "react" && (
              <div className="live-preview">
                <div><b>Live preview</b><span>Updates automatically</span></div>
                <iframe
                  title="Candidate React preview"
                  sandbox="allow-scripts"
                  referrerPolicy="no-referrer"
                  srcDoc={reactPreviewDocument(previewCode)}
                />
              </div>
            )}
            {runResults && (
              <div className="test-results">
                {runResults.map((r, i) => (
                  <div className={r.passed ? "pass" : "fail"} key={i}>
                    {r.passed ? <Check /> : <X />}
                    <span>
                      <b>{q.workspace === "react" ? r.label || `Requirement ${i + 1}` : `Sample ${i + 1}`}</b>
                      <small>
                        {r.passed
                          ? "Passed"
                          : r.error ||
                            `Expected ${r.expected}, got ${r.actual}`}
                      </small>
                    </span>
                  </div>
                ))}
              </div>
            )}
            <div className="editor-actions">
              <button className="secondary" onClick={run} disabled={busy}>
                <Play size={16} /> {q.workspace === "react" ? "Check requirements" : "Run samples"}
              </button>
              <button
                className="primary"
                onClick={submit}
                disabled={busy || !code.trim()}
              >
                {busy ? (
                  "Evaluating…"
                ) : (
                  <>
                    Submit solution <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </section>
        </main>
      ) : (
        <main className="question-shell">
          <div className="question-card">
            <div className="question-meta">
              <span>{q.category.replace("-", " ")}</span>
              <span>+1 point</span>
            </div>
            <h1>{q.prompt}</h1>
            <div className="options">
              {q.options.map((option, index) => (
                <button
                  key={option}
                  className={selected === index ? "selected" : ""}
                  onClick={() => setSelected(index)}
                >
                  <i>{String.fromCharCode(65 + index)}</i>
                  <span>{option}</span>
                  {selected === index && <Check />}
                </button>
              ))}
            </div>
            {error && <div className="error-box">{error}</div>}
            <div className="answer-footer">
              <span>
                Choose one answer. You cannot return to this question.
              </span>
              <button
                className="primary"
                disabled={selected === null || busy}
                onClick={submit}
              >
                {busy ? (
                  <>
                    <i className="button-spinner" /> Saving answer…
                  </>
                ) : (
                  <>
                    Save & next <ArrowRight size={17} />
                  </>
                )}
              </button>
            </div>
          </div>
        </main>
      )}
      {blocked && (
        <div className="fullscreen-block">
          <div>
            <Maximize2 />
            <h2>Return to fullscreen</h2>
            <p>
              Your assessment is paused visually, but the question timer
              continues. This exit has been recorded.
            </p>
            <button
              className="primary"
              onClick={() =>
                document.documentElement.requestFullscreen().catch(() => {})
              }
            >
              <Maximize2 size={17} /> Resume in fullscreen
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function AdminLogin() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const d = await request("/staff/login/", {
        method: "POST",
        body: JSON.stringify(form),
      });
      localStorage.setItem("adminToken", d.token);
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="admin-login">
      <div className="login-brand">
        <Brand light />
        <div>
          <span className="eyebrow light">
            <span /> Recruiter console
          </span>
          <h1>
            Find the people
            <br />
            who <em>stand out.</em>
          </h1>
          <p>
            Monitor progress, review code performance, and rank candidates with
            clarity.
          </p>
        </div>
      </div>
      <div className="login-form">
        <form onSubmit={submit}>
          <div className="login-icon">
            <LockKeyhole />
          </div>
          <h2>Welcome back</h2>
          <p>Sign in with your staff credentials.</p>
          <label>
            Username
            <input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoComplete="username"
              placeholder="name@company.com"
              required
            />
          </label>
          <label>
            Password
            <div className="password-wrap">
              <input
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </label>
          {error && <div className="error-box">{error}</div>}
          <button className="primary wide" disabled={busy}>
            {busy ? "Signing in…" : "Sign in to dashboard"}
          </button>
          <button
            type="button"
            className="text-button"
            onClick={() => navigate("/")}
          >
            <ChevronLeft size={15} /> Candidate portal
          </button>
        </form>
      </div>
    </div>
  );
}

function AdminDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [hiringFilter, setHiringFilter] = useState("");
  const [assessmentFilter, setAssessmentFilter] = useState("");
  const [integrityFilter, setIntegrityFilter] = useState("");
  const [scoreFilter, setScoreFilter] = useState("");
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [tab, setTab] = useState("overview");
  useEffect(() => {
    request("/staff/dashboard/", {}, true)
      .then(setData)
      .catch(() => {
        localStorage.removeItem("adminToken");
        navigate("/admin");
      });
  }, [navigate]);
  const open = async (candidate) => {
    setSelected(candidate);
    setDetail(null);
    try {
      setDetail(await request(`/staff/candidates/${candidate.id}/`, {}, true));
    } catch {}
  };
  const updateHiringStatus = async (candidateId, hiringStatus, note = "") => {
    const payload = await request(
      `/staff/candidates/${candidateId}/status/`,
      {
        method: "PATCH",
        body: JSON.stringify({ hiring_status: hiringStatus, note }),
      },
      true,
    );
    let merged;
    setData((current) => {
      const previous = current.candidates.find(
        (item) => item.id === candidateId,
      );
      merged = {
        ...previous,
        ...payload.candidate,
        percentage: previous.percentage,
      };
      return {
        ...current,
        candidates: current.candidates.map((item) =>
          item.id === candidateId ? merged : item,
        ),
      };
    });
    setSelected((current) =>
      current?.id === candidateId
        ? { ...current, ...payload.candidate, percentage: current.percentage }
        : current,
    );
    setDetail(payload.candidate);
    return payload.candidate;
  };
  if (!data) return <Loader />;
  const rows = data.candidates.filter((c) => {
    const violations = c.rounds.reduce(
      (sum, round) => sum + round.violations,
      0,
    );
    const scoreMatch =
      !scoreFilter ||
      (scoreFilter === "80" && c.percentage >= 80) ||
      (scoreFilter === "60" && c.percentage >= 60 && c.percentage < 80) ||
      (scoreFilter === "40" && c.percentage >= 40 && c.percentage < 60) ||
      (scoreFilter === "below40" && c.percentage < 40);
    const integrityMatch =
      !integrityFilter ||
      (integrityFilter === "zero" && violations === 0) ||
      (integrityFilter === "flagged" && violations > 0) ||
      (integrityFilter === "high" && violations >= 3);
    return (
      (!role || c.role === role) &&
      (!locationFilter || c.preferred_location === locationFilter) &&
      (!hiringFilter || c.hiring_status === hiringFilter) &&
      (!assessmentFilter || c.status === assessmentFilter) &&
      scoreMatch &&
      integrityMatch &&
      `${c.name} ${c.email} ${c.college}`
        .toLowerCase()
        .includes(query.toLowerCase())
    );
  });
  const chart = roles.map(([value, name]) => ({
    name: name.split(" ")[0],
    candidates: data.candidates.filter((c) => c.role === value).length,
  }));
  const roundPerformance = Object.keys(roundMeta).map((roundType) => {
    const attempts = data.candidates.flatMap((candidate) =>
      candidate.rounds.filter((round) => round.round_type === roundType),
    );
    const average = attempts.length
      ? attempts.reduce(
          (sum, attempt) =>
            sum +
            (attempt.max_score ? (attempt.score / attempt.max_score) * 100 : 0),
          0,
        ) / attempts.length
      : 0;
    return {
      name: roundMeta[roundType].title.split(" ")[0],
      average: Math.round(average * 10) / 10,
      attempts: attempts.length,
    };
  });
  const rolePerformance = roles.map(([value, name]) => {
    const candidates = data.candidates.filter(
      (candidate) => candidate.role === value,
    );
    return {
      name: name.split(" ")[0],
      average: candidates.length
        ? Math.round(
            (candidates.reduce(
              (sum, candidate) => sum + candidate.percentage,
              0,
            ) /
              candidates.length) *
              10,
          ) / 10
        : 0,
    };
  });
  const titles = {
    overview: "Hiring overview",
    candidates: "Candidate directory",
    analytics: "Assessment analytics",
  };
  return (
    <div className="admin-page">
      <aside>
        <Brand light />
        <nav>
          <button
            className={tab === "overview" ? "active" : ""}
            onClick={() => setTab("overview")}
          >
            <LayoutDashboard />
            Overview
          </button>
          <button
            className={tab === "candidates" ? "active" : ""}
            onClick={() => setTab("candidates")}
          >
            <UsersRound />
            Candidates
          </button>
          <button
            className={tab === "analytics" ? "active" : ""}
            onClick={() => setTab("analytics")}
          >
            <BarChart3 />
            Assessment analytics
          </button>
        </nav>
        <div className="aside-foot">
          <span>Recruitment drive</span>
          <b>Campus 2026</b>
          <button
            onClick={() => {
              localStorage.removeItem("adminToken");
              navigate("/admin");
            }}
          >
            <LogOut /> Sign out
          </button>
        </div>
      </aside>
      <main className="admin-main">
        <header>
          <div>
            <span className="eyebrow">
              <span /> Live recruitment
            </span>
            <h1>{titles[tab]}</h1>
          </div>
          <div className="live">
            <i /> Assessment live
          </div>
        </header>
        {tab !== "candidates" && (
          <div className="stat-grid">
            <Stat
              icon={UsersRound}
              label="Registered"
              value={data.summary.registered}
            />
            <Stat
              icon={Check}
              label="Completed"
              value={data.summary.completed}
            />
            <Stat
              icon={BarChart3}
              label="Average score"
              value={`${data.summary.average}%`}
            />
            <Stat
              icon={Trophy}
              label="Highest score"
              value={`${data.summary.top_score}%`}
            />
          </div>
        )}
        {tab === "overview" && (
          <div className="admin-mid">
            <section className="panel">
              <div className="panel-head">
                <div>
                  <h3>Applications by role</h3>
                  <p>Candidate distribution</p>
                </div>
              </div>
              <div className="chart">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chart}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                    <YAxis
                      allowDecimals={false}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="candidates"
                      fill="#6c4df6"
                      radius={[7, 7, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
            <section className="panel leaderboard">
              <div className="panel-head">
                <div>
                  <h3>Top performers</h3>
                  <p>Overall assessment score</p>
                </div>
                <Trophy />
              </div>
              {data.candidates.slice(0, 4).map((c, i) => (
                <div className="leader" key={c.id}>
                  <b className={`rank r${i + 1}`}>{i + 1}</b>
                  <span className="avatar">{c.name[0]}</span>
                  <div>
                    <b>{c.name}</b>
                    <small>{c.role_label}</small>
                  </div>
                  <strong>{c.percentage}%</strong>
                </div>
              ))}
            </section>
          </div>
        )}
        {tab === "analytics" && (
          <div className="analytics-grid">
            <section className="panel">
              <div className="panel-head">
                <div>
                  <h3>Average score by round</h3>
                  <p>Percentage performance across submitted attempts</p>
                </div>
              </div>
              <div className="chart analytics-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={roundPerformance}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                    <YAxis
                      domain={[0, 100]}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar
                      dataKey="average"
                      name="Average score"
                      fill="#6c4df6"
                      radius={[7, 7, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
            <section className="panel">
              <div className="panel-head">
                <div>
                  <h3>Average score by role</h3>
                  <p>Overall candidate performance by preferred role</p>
                </div>
              </div>
              <div className="chart analytics-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={rolePerformance}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                    <YAxis
                      domain={[0, 100]}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar
                      dataKey="average"
                      name="Average score"
                      fill="#22a06b"
                      radius={[7, 7, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        )}
        {tab !== "analytics" && (
          <section className="panel candidate-table">
            <div className="panel-head">
              <div>
                <h3>All candidates</h3>
                <p>Ranked by overall performance</p>
              </div>
              <div className="filters">
                <label>
                  <Search />
                  <input
                    placeholder="Search candidates"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </label>
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="">All roles</option>
                  {roles.map((r) => (
                    <option key={r[0]} value={r[0]}>
                      {r[1]}
                    </option>
                  ))}
                </select>
                <select
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                >
                  <option value="">All locations</option>
                  <option value="not_provided">Not provided (legacy)</option>
                  {locations.map(([value, name]) => (
                    <option key={value} value={value}>
                      {name}
                    </option>
                  ))}
                </select>
                <select
                  value={hiringFilter}
                  onChange={(e) => setHiringFilter(e.target.value)}
                >
                  <option value="">All hiring statuses</option>
                  {hiringStatuses.map(([value, name]) => (
                    <option key={value} value={value}>
                      {name}
                    </option>
                  ))}
                </select>
                <select
                  value={assessmentFilter}
                  onChange={(e) => setAssessmentFilter(e.target.value)}
                >
                  <option value="">All assessment stages</option>
                  <option value="registered">Registered</option>
                  <option value="aptitude">Aptitude</option>
                  <option value="technical">Technical test</option>
                  <option value="coding">Coding</option>
                  <option value="completed">Completed</option>
                </select>
                <select
                  value={integrityFilter}
                  onChange={(e) => setIntegrityFilter(e.target.value)}
                >
                  <option value="">All integrity records</option>
                  <option value="zero">Zero violations</option>
                  <option value="flagged">Any violation</option>
                  <option value="high">3+ violations</option>
                </select>
                <select
                  value={scoreFilter}
                  onChange={(e) => setScoreFilter(e.target.value)}
                >
                  <option value="">All scores</option>
                  <option value="80">80% and above</option>
                  <option value="60">60–79%</option>
                  <option value="40">40–59%</option>
                  <option value="below40">Below 40%</option>
                </select>
                {(role ||
                  locationFilter ||
                  hiringFilter ||
                  assessmentFilter ||
                  integrityFilter ||
                  scoreFilter ||
                  query) && (
                  <button
                    className="clear-filters"
                    onClick={() => {
                      setQuery("");
                      setRole("");
                      setLocationFilter("");
                      setHiringFilter("");
                      setAssessmentFilter("");
                      setIntegrityFilter("");
                      setScoreFilter("");
                    }}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Candidate</th>
                    <th>Role</th>
                    <th>Location</th>
                    <th>Hiring status</th>
                    <th>Assessment</th>
                    <th>Test cases</th>
                    <th>Violations</th>
                    <th>Score</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((c, i) => (
                    <tr key={c.id}>
                      <td>
                        <b>#{i + 1}</b>
                      </td>
                      <td>
                        <div className="person">
                          <span>{c.name[0]}</span>
                          <div>
                            <b>{c.name}</b>
                            <small>{c.email}</small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="role-tag">{c.role_label}</span>
                      </td>
                      <td>{c.preferred_location_label}</td>
                      <td>
                        <select
                          className={`hiring-status-select status-${c.hiring_status}`}
                          value={c.hiring_status}
                          onChange={(event) =>
                            updateHiringStatus(c.id, event.target.value)
                          }
                        >
                          {hiringStatuses.map(([value, name]) => (
                            <option key={value} value={value}>
                              {name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span
                          className={`status-tag ${c.status === "completed" ? "complete" : ""}`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td>
                        {c.rounds.reduce((s, r) => s + r.passed_tests, 0)} /{" "}
                        {c.rounds.reduce((s, r) => s + r.total_tests, 0)}
                      </td>
                      <td>{c.rounds.reduce((s, r) => s + r.violations, 0)}</td>
                      <td>
                        <b className="score">{c.percentage}%</b>
                      </td>
                      <td>
                        <button className="view-btn" onClick={() => open(c)}>
                          <Eye />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!rows.length && (
                <div className="empty">No candidates match these filters.</div>
              )}
            </div>
          </section>
        )}
      </main>
      {selected && (
        <CandidateDrawer
          candidate={selected}
          detail={detail}
          updateStatus={updateHiringStatus}
          close={() => setSelected(null)}
        />
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="stat-card">
      <span>
        <Icon />
      </span>
      <div>
        <small>{label}</small>
        <b>{value}</b>
      </div>
    </div>
  );
}
function CandidateDrawer({ candidate, detail, close, updateStatus }) {
  const [statusDraft, setStatusDraft] = useState(candidate.hiring_status);
  const [statusNote, setStatusNote] = useState("");
  const [savingStatus, setSavingStatus] = useState(false);
  const saveStatus = async () => {
    setSavingStatus(true);
    try {
      await updateStatus(candidate.id, statusDraft, statusNote);
      setStatusNote("");
    } finally {
      setSavingStatus(false);
    }
  };
  return (
    <div className="drawer-backdrop" onClick={close}>
      <aside className="drawer" onClick={(e) => e.stopPropagation()}>
        <button className="drawer-close" onClick={close}>
          <X />
        </button>
        <div className="drawer-person">
          <span>{candidate.name[0]}</span>
          <h2>{candidate.name}</h2>
          <p>
            {candidate.email} · {candidate.phone}
          </p>
          <i>{candidate.role_label}</i>
        </div>
        <div className="detail-grid">
          <div>
            <small>College</small>
            <b>{candidate.college}</b>
          </div>
          <div>
            <small>Degree / designation</small>
            <b>{candidate.designation}</b>
          </div>
          <div>
            <small>Overall score</small>
            <b>{candidate.percentage}%</b>
          </div>
          <div>
            <small>Assessment status</small>
            <b>{candidate.status}</b>
          </div>
          <div>
            <small>Preferred location</small>
            <b>{candidate.preferred_location_label}</b>
          </div>
          <div>
            <small>Hiring status</small>
            <b>{candidate.hiring_status_label}</b>
          </div>
        </div>
        <div className="workflow-editor">
          <h3>Update recruitment status</h3>
          <select
            value={statusDraft}
            onChange={(event) => setStatusDraft(event.target.value)}
          >
            {hiringStatuses.map(([value, name]) => (
              <option key={value} value={value}>
                {name}
              </option>
            ))}
          </select>
          <textarea
            rows="2"
            value={statusNote}
            onChange={(event) => setStatusNote(event.target.value)}
            placeholder="Optional note, interviewer feedback, or next action"
          />
          <button
            className="primary"
            onClick={saveStatus}
            disabled={savingStatus}
          >
            {savingStatus ? "Saving…" : "Save status"}
          </button>
        </div>
        <h3>Round performance</h3>
        {candidate.rounds.map((r) => (
          <div className="round-result" key={r.round_type}>
            <span>
              {roundMeta[r.round_type]?.title}
              <small>
                {r.passed_tests}/{r.total_tests} coding tests · {r.violations}{" "}
                violations
              </small>
            </span>
            <b>
              {r.score}/{r.max_score}
            </b>
          </div>
        ))}
        <h3>Response audit</h3>
        {!detail ? (
          <div className="drawer-loading">Loading response details…</div>
        ) : (
          <div className="response-list">
            {detail.responses.map((r, i) => (
              <div key={i}>
                <span className={r.correct ? "dot-good" : "dot-bad"} />
                <p>
                  <b>{r.question.split("\n")[0]}</b>
                  <small>
                    {r.round} ·{" "}
                    {r.timed_out
                      ? "Timed out"
                      : r.total_tests
                        ? `${r.passed_tests}/${r.total_tests} tests passed`
                        : r.correct
                          ? "Correct"
                          : "Incorrect"}
                  </small>
                </p>
                <strong>{r.score}</strong>
              </div>
            ))}
          </div>
        )}
        {detail?.status_history?.length > 0 && (
          <>
            <h3>Recruitment timeline</h3>
            <div className="status-timeline">
              {detail.status_history.map((event, index) => (
                <div key={`${event.created_at}-${index}`}>
                  <i />
                  <span>
                    <b>{event.to_status_label}</b>
                    <small>
                      {new Date(event.created_at).toLocaleString()} ·{" "}
                      {event.changed_by}
                    </small>
                    {event.note && <p>{event.note}</p>}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
function Loader() {
  return (
    <div className="loader">
      <div className="logo-loader">
        <i />
        <img src={luxmorLogo} alt="Luxmor AI Technologies" />
      </div>
      <b>Luxmor TalentForge</b>
      <p>Preparing your recruitment workspace…</p>
    </div>
  );
}

function CandidateOnly({ children }) {
  return localStorage.getItem("candidateToken") ? (
    children
  ) : (
    <Navigate to="/" replace />
  );
}
function AdminOnly({ children }) {
  return localStorage.getItem("adminToken") ? (
    children
  ) : (
    <Navigate to="/admin" replace />
  );
}
function AdminEntry() {
  return localStorage.getItem("adminToken") ? (
    <Navigate to="/admin/dashboard" replace />
  ) : (
    <AdminLogin />
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/portal"
          element={
            <CandidateOnly>
              <Portal />
            </CandidateOnly>
          }
        />
        <Route
          path="/instructions/:type"
          element={
            <CandidateOnly>
              <Instructions />
            </CandidateOnly>
          }
        />
        <Route
          path="/assessment/:type"
          element={
            <CandidateOnly>
              <Assessment />
            </CandidateOnly>
          }
        />
        <Route path="/admin" element={<AdminEntry />} />
        <Route path="/admin/" element={<AdminEntry />} />
        <Route
          path="/admin/dashboard"
          element={
            <AdminOnly>
              <AdminDashboard />
            </AdminOnly>
          }
        />
        <Route
          path="/admin/dashboard/"
          element={
            <AdminOnly>
              <AdminDashboard />
            </AdminOnly>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
