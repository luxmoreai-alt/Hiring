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
  Download,
  Eye,
  EyeOff,
  FileText,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Play,
  Printer,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
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
  ["mern-stack-developer", "MERN Stack Developer", "MongoDB, Express, React & Node.js"],
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
    title: "Technical aptitude",
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
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.detail || `Request failed (HTTP ${response.status}). Please try again.`);
    error.status = response.status;
    throw error;
  }
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
    if (!/^\d{10}$/.test(form.phone)) {
      setError("Phone number must contain exactly 10 digits.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const body = new FormData();
      Object.entries(form).forEach(([key, value]) => body.append(key, value));
      body.append("address_confirmed", "true");
      const data = await request("/candidates/register/", {
        method: "POST",
        body,
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
                  onChange={(event) => setForm({ ...form, phone: event.target.value.replace(/\D/g, "").slice(0, 10) })}
                  pattern="[0-9]{10}"
                  inputMode="numeric"
                  minLength="10"
                  maxLength="10"
                  placeholder="9876543210"
                />
              </label>
            </div>
            <div className="field-row">
              <label>
                College / University
                <input
                  required
                  value={form.college}
                  onChange={(event) => setForm({ ...form, college: event.target.value.toUpperCase() })}
                  placeholder="E.G. ANNA UNIVERSITY"
                />
                <small className="field-help">Enter your college&apos;s full name in CAPITAL LETTERS. Do not use abbreviations.</small>
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
              Permanent address (as per Aadhaar)
              <textarea
                required
                rows="2"
                value={form.address}
                onChange={set("address")}
                placeholder="Enter your full permanent address as shown on Aadhaar"
                minLength="20"
                pattern=".*[1-9][0-9]{5}.*"
              />
              <small className="field-help">
                Please enter your full permanent address exactly as on your
                Aadhaar. It will be used for office-letter processing.
              </small>
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
              Developer, MERN Stack Developer, and Cloud Engineer profiles are
              supported.
            </p>
          </article>
          <article>
            <h3>Are candidate results public?</h3>
            <p>
              No. Candidate submissions and recruitment decisions are
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
        {candidate.hiring_status === "rejected" ? (
          <Rejection candidate={candidate} />
        ) : candidate.status === "completed" ? (
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
                  Ensure a stable internet connection and submit each answer
                  before its timer expires.
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

function Rejection({ candidate }) {
  return (
    <section className="completion rejection-card">
      <div className="trophy rejection-icon"><X /></div>
      <span className="eyebrow"><span /> Application update</span>
      <h2>Thank you for your time, {candidate.name.split(" ")[0]}.</h2>
      <p>
        The recruitment team has updated your application status.
      </p>
      <div className="result-private-note rejection-note">
        <X size={18} />
        <span>
          <b>Reason for rejection</b>
          {candidate.ai_rejection_reason || "Your application was not selected for the next step."}
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
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  if (!meta) return <Navigate to="/portal" />;
  const begin = async () => {
    if (!consent) {
      setError("Read and accept the assessment instructions before starting.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await request(`/rounds/${type}/start/`, { method: "POST" });
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
            <ShieldCheck />
            <span>
              <b>Complete each stage independently</b>
              <small>
                Use your own knowledge and submit every answer before its timer expires.
              </small>
            </span>
          </div>
          <div>
            <Clock3 />
            <span>
              <b>Automatic submission</b>
              <small>
                At zero, the current answer is submitted automatically. Questions cannot be revisited, so save each answer before moving on.
              </small>
            </span>
          </div>
        </div>
        
        <label className="rule-consent">
          <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
          <span>I have read the assessment instructions and I am ready to begin.</span>
        </label>
        {error && <div className="error-box">{error}</div>}
        <button className="primary wide" onClick={begin} disabled={loading || !consent}>
          {loading ? (
            "Preparing stage…"
          ) : (
            <>
              <Play size={18} /> Begin stage
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
  const [busy, setBusy] = useState(false);
  const [runResults, setRunResults] = useState(null);
  const [error, setError] = useState("");
  const submitting = useRef(false);
  const load = useCallback(async () => {
    try {
      const data = await request(`/rounds/${type}/state/`);
      setError("");
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
      if ([409, 423].includes(e.status)) {
        navigate("/portal", { replace: true });
      } else {
        setError(e.message);
      }
    }
  }, [type, language, navigate]);
  useEffect(() => {
    load();
  }, [load]);
  useEffect(() => {
    const timer = setTimeout(() => setPreviewCode(code), 500);
    return () => clearTimeout(timer);
  }, [code]);
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
        navigate("/portal");
      }
    } catch (e) {
      if (e.message.includes("advanced")) {
        await load();
      } else if ([409, 423].includes(e.status)) {
        navigate("/portal", { replace: true });
      } else {
        setError(e.message);
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
      if ([409, 423].includes(e.status)) {
        navigate("/portal", { replace: true });
      } else {
        setError(e.message);
      }
    } finally {
      setBusy(false);
    }
  };
  if (!state && error) return <Navigate to="/portal" replace />;
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
                    "Submitting…"
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
  const [collegeFilter, setCollegeFilter] = useState("");
  const [reportColleges, setReportColleges] = useState([]);
  const [reportStatuses, setReportStatuses] = useState(["selected", "rejected"]);
  const [collegeMenuOpen, setCollegeMenuOpen] = useState(false);
  const [locationFilter, setLocationFilter] = useState("");
  const [hiringFilter, setHiringFilter] = useState("");
  const [assessmentFilter, setAssessmentFilter] = useState("");
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [tab, setTab] = useState("overview");
  const [deletingRejected, setDeletingRejected] = useState(false);
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
      merged = { ...previous, ...payload.candidate };
      return {
        ...current,
        candidates: current.candidates.map((item) =>
          item.id === candidateId ? merged : item,
        ),
      };
    });
    setSelected((current) =>
      current?.id === candidateId
        ? { ...current, ...payload.candidate }
        : current,
    );
    setDetail(payload.candidate);
    return payload.candidate;
  };
  const deleteCandidate = async (candidate) => {
    if (!window.confirm(`Delete ${candidate.name} and all of their assessment data? This cannot be undone.`)) return;
    try {
      await request(`/staff/candidates/${candidate.id}/delete/`, { method: "DELETE" }, true);
      setData((current) => ({
        ...current,
        candidates: current.candidates.filter((item) => item.id !== candidate.id),
      }));
      if (selected?.id === candidate.id) {
        setSelected(null);
        setDetail(null);
      }
    } catch (error) {
      window.alert(error.message);
    }
  };
  const resetCandidate = async (candidate) => {
    if (!window.confirm(`Reset assessment access for ${candidate.name}? Their current results will be kept in previous assessment history, and they can start again with the same email and phone number.`)) return;
    try {
      const payload = await request(
        `/staff/candidates/${candidate.id}/reset/`,
        { method: "POST" },
        true,
      );
      const reset = { ...candidate, ...payload.candidate };
      setData((current) => ({
        ...current,
        candidates: current.candidates.map((item) =>
          item.id === candidate.id ? reset : item,
        ),
      }));
      setSelected((current) => current?.id === candidate.id ? reset : current);
      setDetail(payload.candidate);
    } catch (error) {
      window.alert(error.message);
    }
  };
  const deleteAllSelected = async () => {
    const count = data.candidates.filter((candidate) => candidate.hiring_status === "selected").length;
    if (!count || !window.confirm(`Delete all ${count} selected candidates and their assessment data? This cannot be undone.`)) return;
    try {
      await request("/staff/selected/delete-all/", { method: "DELETE" }, true);
      setData((current) => ({ ...current, candidates: current.candidates.filter((candidate) => candidate.hiring_status !== "selected") }));
      setSelected(null);
      setDetail(null);
    } catch (error) {
      window.alert(error.message);
    }
  };
  const deleteAllRejected = async () => {
    const count = data.candidates.filter((candidate) => candidate.hiring_status === "rejected").length;
    if (deletingRejected || !count || !window.confirm(`Delete all ${count} rejected candidates and their assessment data? This cannot be undone.`)) return;
    setDeletingRejected(true);
    let deleted = 0;
    try {
      let remaining;
      do {
        const result = await request("/staff/rejected/delete-all/?limit=10", { method: "DELETE" }, true);
        deleted += result.deleted;
        remaining = result.remaining;
        if (result.deleted < 1 && remaining > 0) {
          throw new Error("Rejected candidates could not be deleted. Refresh the dashboard and try again.");
        }
      } while (remaining > 0);
      if (deleted < 1) throw new Error("No rejected candidates were deleted. Refresh the dashboard and try again.");

      setData((current) => ({ ...current, candidates: current.candidates.filter((candidate) => candidate.hiring_status !== "rejected") }));
      setSelected(null);
      setDetail(null);
      // Refresh every dashboard total after the API confirms the database deletion.
      try {
        setData(await request("/staff/dashboard/", {}, true));
      } catch {
        window.alert(`${deleted} rejected candidate${deleted === 1 ? " was" : "s were"} deleted, but the dashboard totals could not be refreshed.`);
      }
    } catch (error) {
      if (deleted > 0) {
        request("/staff/dashboard/", {}, true).then(setData).catch(() => {});
      }
      window.alert(deleted > 0 ? `${deleted} rejected candidates were deleted before the request stopped. ${error.message}` : error.message);
    } finally {
      setDeletingRejected(false);
    }
  };
  if (!data) return <Loader />;
  const collegeKey = (value) => value.trim().replace(/\s+/g, " ").toLocaleLowerCase();
  const collegeMap = new Map();
  data.candidates.forEach((candidate) => {
    const key = collegeKey(candidate.college);
    if (key && !collegeMap.has(key)) collegeMap.set(key, candidate.college.trim().replace(/\s+/g, " "));
  });
  const colleges = [...collegeMap.entries()].sort((left, right) => left[1].localeCompare(right[1]));
  const reportCandidates = data.candidates.filter(
    (candidate) =>
      (!reportColleges.length || reportColleges.includes(collegeKey(candidate.college))) &&
      reportStatuses.includes(candidate.hiring_status),
  );
  const collegeReport = colleges
    .filter(([key]) => !reportColleges.length || reportColleges.includes(key))
    .map(([key, college]) => {
      const candidates = data.candidates.filter((candidate) => collegeKey(candidate.college) === key);
      return {
        key,
        college,
        total: candidates.length,
        selected: candidates.filter((candidate) => candidate.hiring_status === "selected").length,
        rejected: candidates.filter((candidate) => candidate.hiring_status === "rejected").length,
        reported: candidates.filter((candidate) => reportStatuses.includes(candidate.hiring_status)).length,
      };
    })
    .filter((item) => item.reported > 0);
  const toggleReportCollege = (key) => {
    setReportColleges((current) =>
      current.includes(key) ? current.filter((item) => item !== key) : [...current, key],
    );
  };
  const toggleReportStatus = (status) => {
    setReportStatuses((current) =>
      current.includes(status) ? current.filter((item) => item !== status) : [...current, status],
    );
  };
  const downloadReport = () => {
    const columns = [
      "Student name", "Email", "Phone", "College", "Degree / designation", "Role",
      "Preferred location", "Hiring status", "Assessment status", "Registered at",
    ];
    const csvCell = (value) => {
      const text = String(value ?? "");
      const spreadsheetSafe = /^[=+\-@]/.test(text) ? `'${text}` : text;
      return `"${spreadsheetSafe.replaceAll('"', '""')}"`;
    };
    const lines = reportCandidates.map((candidate) => {
      return [
        candidate.name, candidate.email, candidate.phone, candidate.college,
        candidate.designation, candidate.role_label, candidate.preferred_location_label,
        candidate.hiring_status_label, candidate.status,
        candidate.registered_at ? new Date(candidate.registered_at).toLocaleString() : "",
      ].map(csvCell).join(",");
    });
    const blob = new Blob(["\ufeff", columns.map(csvCell).join(","), "\r\n", lines.join("\r\n")], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `student-report-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };
  const tableCandidates = tab === "selected"
    ? data.candidates.filter((candidate) => candidate.hiring_status === "selected")
    : tab === "rejected"
      ? data.candidates.filter((candidate) => candidate.hiring_status === "rejected")
      : data.candidates;
  const rows = tableCandidates.filter((c) => {
    return (
      (!role || c.role === role) &&
      (!collegeFilter || collegeKey(c.college) === collegeFilter) &&
      (!locationFilter || c.preferred_location === locationFilter) &&
      (!hiringFilter || c.hiring_status === hiringFilter) &&
      (!assessmentFilter || c.status === assessmentFilter) &&
      `${c.name} ${c.email} ${c.college}`
        .toLowerCase()
        .includes(query.toLowerCase())
    );
  });
  const chart = roles.map(([value, name]) => ({
    name: name.split(" ")[0],
    candidates: data.candidates.filter((c) => c.role === value).length,
  }));
  const titles = {
    overview: "Hiring overview",
    candidates: "Candidate directory",
    selected: "Selected candidates",
    rejected: "Rejected candidates",
    reports: "College reports",
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
            className={tab === "selected" ? "active" : ""}
            onClick={() => setTab("selected")}
          >
            <Check />
            Selected candidates
          </button>
          <button
            className={tab === "rejected" ? "active" : ""}
            onClick={() => setTab("rejected")}
          >
            <X />
            Rejected candidates
          </button>
          <button
            className={tab === "reports" ? "active" : ""}
            onClick={() => setTab("reports")}
          >
            <FileText />
            Reports
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
        {tab !== "candidates" && tab !== "selected" && tab !== "rejected" && tab !== "reports" && (
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
              icon={UserRound}
              label="Selected"
              value={data.candidates.filter((candidate) => candidate.hiring_status === "selected").length}
            />
            <Stat
              icon={X}
              label="Rejected"
              value={data.candidates.filter((candidate) => candidate.hiring_status === "rejected").length}
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
                  <h3>Recent candidates</h3>
                  <p>Latest registrations</p>
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
                  <strong>{c.status}</strong>
                </div>
              ))}
            </section>
          </div>
        )}
        {tab === "reports" && (
          <section className="panel reports-panel">
            <div className="panel-head reports-head">
              <div>
                <h3>Student selection report</h3>
                <p>Select one or more colleges and the result types you want to include.</p>
              </div>
              <div className="report-actions">
                <button className="secondary" onClick={() => window.print()} disabled={!reportCandidates.length}>
                  <Printer /> Print / PDF
                </button>
                <button className="primary" onClick={downloadReport} disabled={!reportCandidates.length}>
                  <Download /> Download detailed CSV
                </button>
              </div>
            </div>
            <div className="report-controls">
              <div className="report-control">
                <span className="report-label">Colleges</span>
                <div className="multi-select">
                  <button type="button" onClick={() => setCollegeMenuOpen((open) => !open)}>
                    <span>
                      {!reportColleges.length
                        ? "All colleges"
                        : reportColleges.length === 1
                          ? collegeMap.get(reportColleges[0])
                          : `${reportColleges.length} colleges selected`}
                    </span>
                    <ChevronLeft className={collegeMenuOpen ? "multi-arrow open" : "multi-arrow"} />
                  </button>
                  {collegeMenuOpen && (
                    <div className="multi-menu">
                      <label>
                        <input type="checkbox" checked={!reportColleges.length} onChange={() => setReportColleges([])} />
                        <b>All colleges</b>
                      </label>
                      {colleges.map(([key, college]) => (
                        <label key={key}>
                          <input type="checkbox" checked={reportColleges.includes(key)} onChange={() => toggleReportCollege(key)} />
                          <span>{college}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="report-control">
                <span className="report-label">Report type</span>
                <div className="report-status-options">
                  <label className="selected-option">
                    <input type="checkbox" checked={reportStatuses.includes("selected")} onChange={() => toggleReportStatus("selected")} />
                    <Check /> Selected
                  </label>
                  <label className="rejected-option">
                    <input type="checkbox" checked={reportStatuses.includes("rejected")} onChange={() => toggleReportStatus("rejected")} />
                    <X /> Rejected
                  </label>
                </div>
              </div>
            </div>
            {!reportStatuses.length ? (
              <div className="empty">Choose Selected, Rejected, or both to create a report.</div>
            ) : (
              <>
                <div className="report-summary">
                  <Stat icon={UsersRound} label="Students in report" value={reportCandidates.length} />
                  <Stat icon={Check} label="Selected" value={reportCandidates.filter((candidate) => candidate.hiring_status === "selected").length} />
                  <Stat icon={X} label="Rejected" value={reportCandidates.filter((candidate) => candidate.hiring_status === "rejected").length} />
                  <Stat icon={FileText} label="Colleges" value={collegeReport.length} />
                </div>
                <div className="college-report-grid">
                  {collegeReport.map((item) => (
                    <article key={item.key}>
                      <h4>{item.college}</h4>
                      <span>{item.total} total students</span>
                      <div><b className="report-selected">{item.selected}</b><small>Selected</small></div>
                      <div><b className="report-rejected">{item.rejected}</b><small>Rejected</small></div>
                    </article>
                  ))}
                </div>
                <div className="table-scroll report-table">
                  <table>
                    <thead>
                      <tr><th>Student</th><th>College</th><th>Role</th><th>Result</th><th>Assessment</th><th>Details</th></tr>
                    </thead>
                    <tbody>
                      {reportCandidates.map((candidate) => (
                        <tr key={candidate.id}>
                          <td><div className="person"><span>{candidate.name[0]}</span><div><b>{candidate.name}</b><small>{candidate.email} · {candidate.phone}</small></div></div></td>
                          <td>{candidate.college}<br /><small>{candidate.designation}</small></td>
                          <td>{candidate.role_label}<br /><small>{candidate.preferred_location_label}</small></td>
                          <td><span className={`report-result ${candidate.hiring_status}`}>{candidate.hiring_status_label}</span></td>
                          <td>{candidate.status}</td>
                          <td><button className="view-btn" aria-label={`View ${candidate.name}'s detailed report`} onClick={() => open(candidate)}><Eye /></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {!reportCandidates.length && <div className="empty">No students match the selected report options.</div>}
                </div>
              </>
            )}
          </section>
        )}
        {tab !== "reports" && (
          <section className="panel candidate-table">
            <div className="panel-head">
              <div>
                  <h3>{tab === "selected" ? "Selected candidates" : tab === "rejected" ? "Rejected candidates" : "All candidates"}</h3>
                  <p>{tab === "selected" ? `${tableCandidates.length} candidates selected for the next step` : tab === "rejected" ? `${tableCandidates.length} candidates rejected` : "Ranked by overall performance"}</p>
                </div>
              <div className="filters">
                {tab === "selected" && tableCandidates.length > 0 && (
                  <button className="danger-action" onClick={deleteAllSelected}><Trash2 /> Delete all selected</button>
                )}
                {tab === "rejected" && tableCandidates.length > 0 && (
                  <button
                    type="button"
                    className="danger-action"
                    onClick={deleteAllRejected}
                    disabled={deletingRejected}
                  >
                    <Trash2 /> {deletingRejected ? "Deleting rejected candidates…" : "Delete all rejected"}
                  </button>
                )}
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
                  value={collegeFilter}
                  onChange={(e) => setCollegeFilter(e.target.value)}
                >
                  <option value="">All colleges</option>
                  {colleges.map(([key, college]) => (
                    <option key={key} value={key}>
                      {college}
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
                {(role ||
                  collegeFilter ||
                  locationFilter ||
                  hiringFilter ||
                  assessmentFilter ||
                  query) && (
                  <button
                    className="clear-filters"
                    onClick={() => {
                      setQuery("");
                      setRole("");
                      setCollegeFilter("");
                      setLocationFilter("");
                      setHiringFilter("");
                      setAssessmentFilter("");
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
                    <th>Candidate</th>
                    <th>Role</th>
                    <th>Location</th>
                    <th>Hiring status</th>
                    <th>Assessment</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((c) => (
                    <tr key={c.id}>
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
                        <button className="view-btn" onClick={() => open(c)}>
                          <Eye />
                        </button>
                        <button
                          className="reset-btn"
                          aria-label={`Reset assessment for ${c.name}`}
                          title="Reset assessment access"
                          onClick={() => resetCandidate(c)}
                        >
                          <RotateCcw />
                        </button>
                        <button
                          className="delete-btn"
                          aria-label={`Delete ${c.name}`}
                          title="Delete candidate"
                          onClick={() => deleteCandidate(c)}
                        >
                          <Trash2 />
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
          <div className="detail-wide address-detail">
            <small>Registered address</small>
            <b>{candidate.address || "Not provided"}</b>
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
        <h3>Stage progress</h3>
        {!candidate.rounds.length && (
          <div className="drawer-loading">No rounds started in the current assessment.</div>
        )}
        {candidate.rounds.map((r) => (
          <div className="round-result" key={r.round_type}>
            <span>
              {roundMeta[r.round_type]?.title}
              <small>{r.status}</small>
            </span>
            <b>{r.status === "in_progress" ? "In progress" : "Submitted"}</b>
          </div>
        ))}
        {detail?.previous_assessments?.length > 0 && (
          <>
            <h3>Previous assessments</h3>
            {detail.previous_assessments.map((assessment) => (
              <div className="previous-assessment" key={assessment.assessment_cycle}>
                <div>
                  <b>Attempt {assessment.assessment_cycle}</b>
                  <small>
                    Status: {assessment.status} · reset {new Date(assessment.reset_at).toLocaleString()} by {assessment.reset_by}
                  </small>
                </div>
                {assessment.rounds.map((round) => (
                  <div className="round-result" key={round.round_type}>
                    <span>
                      {roundMeta[round.round_type]?.title}
                      <small>{round.status}</small>
                    </span>
                    <b>{round.status === "in_progress" ? "In progress" : "Submitted"}</b>
                  </div>
                ))}
              </div>
            ))}
          </>
        )}
        <h3>Response audit</h3>
        {!detail ? (
          <div className="drawer-loading">Loading response details…</div>
        ) : (
          <div className="response-list">
            {detail.responses.map((r, i) => (
              <div key={i}>
                <span className="dot-good" />
                <p>
                  <b>{r.question.split("\n")[0]}</b>
                  <small>
                    {r.round} · {r.timed_out ? "Timed out" : "Submitted"}
                  </small>
                </p>
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
