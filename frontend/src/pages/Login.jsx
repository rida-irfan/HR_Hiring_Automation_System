
import { useState } from "react";
import {
  UsersRound,
  Sparkles,
  Check,
  Mail,
  LockKeyhole,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  BriefcaseBusiness,
  FileUser,
  BarChart3,
  UserRound,
  CheckCircle2,
} from "lucide-react";

import "./Login.css";

const API_URL = "http://127.0.0.1:8000";

export default function Login() {
  const [mode, setMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [showSetupKey, setShowSetupKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    setup_key: "",
  });

  function updateField(e) {
    setForm((previous) => ({
      ...previous,
      [e.target.name]: e.target.value,
    }));
  }

  function changeMode(nextMode) {
    setMode(nextMode);
    setError("");
    setSuccess("");
    setShowPassword(false);
    setShowSetupKey(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    const isSignup = mode === "signup";

    try {
      const headers = {
        "Content-Type": "application/json",
      };

      if (isSignup) {
        headers["hr-setup-key"] = form.setup_key;
      }

      const payload = isSignup
        ? {
            full_name: form.full_name.trim(),
            email: form.email.trim().toLowerCase(),
            password: form.password,
          }
        : {
            email: form.email.trim().toLowerCase(),
            password: form.password,
          };

      const endpoint = isSignup
        ? "/auth/signup"
        : "/auth/login";

      const response = await fetch(
        `${API_URL}${endpoint}`,
        {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Request failed. Please check your details."
        );
      }

      if (isSignup) {
        setMode("login");
        setSuccess(
          "HR account created successfully! Please sign in."
        );

        setForm((previous) => ({
          ...previous,
          password: "",
          setup_key: "",
        }));
      } else {
        if (!data.access_token) {
          throw new Error(
            "Login response did not contain an access token."
          );
        }

        sessionStorage.setItem(
          "hr_token",
          data.access_token
        );

        setLoggedIn(true);
      }
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Unable to connect to FastAPI. Check backend and CORS."
          : err.message || "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    sessionStorage.removeItem("hr_token");
    setLoggedIn(false);
    setForm((previous) => ({
      ...previous,
      password: "",
    }));
  }

  if (loggedIn) {
    return (
      <div className="welcome-screen">
        <div className="welcome-card">
          <CheckCircle2 size={58} color="#16a34a" />
          <h1>Welcome to HireFlow AI!</h1>
          <p>
            You have successfully signed in to your
            HR recruitment workspace.
          </p>
          <button
            className="primary-btn"
            onClick={logout}
          >
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="auth-layout">
      {/* LEFT SIDE */}
      <section className="brand-panel">
        <div className="brand-glow glow-one" />
        <div className="brand-glow glow-two" />

        <div className="brand-header">
          <div className="brand-logo">
            <UsersRound size={30} />
          </div>
          <div>
            <h2>HireFlow AI</h2>
            <p>HR Hiring Automation System</p>
          </div>
        </div>

        <div className="brand-content">
          <div className="ai-badge">
            <Sparkles size={17} />
            AI-Powered Recruitment
          </div>

          <h1>
            Smarter Hiring
            <br />
            for <span>Modern Teams</span>
          </h1>

          <p className="brand-description">
            Streamline your hiring process with
            AI-powered resume screening, candidate
            evaluation, and intelligent interview insights.
          </p>

          <div className="feature-list">
            {[
              "Manage Job Requisitions",
              "AI Resume Evaluation",
              "Conduct Online Interviews",
              "Track Candidates & Results",
            ].map((feature) => (
              <div className="feature" key={feature}>
                <span className="feature-check">
                  <Check size={15} />
                </span>
                {feature}
              </div>
            ))}
          </div>
        </div>

        {/* FLOATING DASHBOARD ILLUSTRATION */}
        <div className="dashboard-illustration">
          <div className="floating-icon floating-resume">
            <FileUser size={27} />
          </div>

          <div className="floating-icon floating-chart">
            <BarChart3 size={27} />
          </div>

          <div className="dashboard-preview">
            <div className="preview-sidebar">
              <BriefcaseBusiness size={21} />
              <UsersRound size={19} />
              <BarChart3 size={19} />
            </div>

            <div className="preview-main">
              <div className="preview-heading">
                HR Dashboard
              </div>

              <div className="preview-stats">
                <div>
                  <strong>12</strong>
                  <small>Open Jobs</small>
                </div>
                <div>
                  <strong>248</strong>
                  <small>Applicants</small>
                </div>
                <div>
                  <strong>36</strong>
                  <small>Shortlisted</small>
                </div>
              </div>

              <div className="preview-bottom">
                <div className="preview-chart">
                  <span>Hiring Overview</span>
                  <div className="chart-bars">
                    {[35, 55, 42, 75, 58, 90, 68].map(
                      (height, index) => (
                        <div
                          key={index}
                          style={{ height: `${height}%` }}
                        />
                      )
                    )}
                  </div>
                </div>

                <div className="preview-score">
                  <span>AI Evaluation</span>
                  <div className="score-circle">
                    85%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="brand-footer">
          <ShieldCheck size={19} />
          Secure • Intelligent • Efficient Hiring
        </div>
      </section>

      {/* RIGHT SIDE */}
      <section className="form-panel">
        <div className="form-card">
          <div className="mobile-logo">
            <UsersRound size={25} />
            <strong>HireFlow AI</strong>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={
                mode === "login" ? "active" : ""
              }
              onClick={() => changeMode("login")}
            >
              Sign In
            </button>

            <button
              type="button"
              className={
                mode === "signup" ? "active" : ""
              }
              onClick={() => changeMode("signup")}
            >
              Sign Up
            </button>
          </div>

          <div className="form-heading">
            <h2>
              {mode === "login"
                ? "Welcome Back 👋"
                : "Create HR Account"}
            </h2>

            <p>
              {mode === "login"
                ? "Sign in to access your HR dashboard"
                : "Administrator authorization is required"}
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            {mode === "signup" && (
              <div className="field-group">
                <label htmlFor="full_name">
                  Full Name
                </label>
                <div className="input-wrapper">
                  <UserRound size={19} />
                  <input
                    id="full_name"
                    name="full_name"
                    value={form.full_name}
                    onChange={updateField}
                    placeholder="Enter your full name"
                    required
                  />
                </div>
              </div>
            )}

            <div className="field-group">
              <label htmlFor="email">
                Work Email
              </label>
              <div className="input-wrapper">
                <Mail size={19} />
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={updateField}
                  placeholder="hr@example.com"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="field-group">
              <label htmlFor="password">
                Password
              </label>

              <div className="input-wrapper">
                <LockKeyhole size={19} />

                <input
                  id="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  name="password"
                  value={form.password}
                  onChange={updateField}
                  placeholder="Enter your password"
                  autoComplete={
                    mode === "login"
                      ? "current-password"
                      : "new-password"
                  }
                  minLength={
                    mode === "signup" ? 12 : undefined
                  }
                  required
                />

                <button
                  type="button"
                  className="eye-btn"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword
                    ? <EyeOff size={20} />
                    : <Eye size={20} />}
                </button>
              </div>
            </div>

            {mode === "signup" && (
              <div className="field-group">
                <label htmlFor="setup_key">
                  Administrator Setup Key
                </label>

                <div className="input-wrapper">
                  <ShieldCheck size={19} />

                  <input
                    id="setup_key"
                    type={
                      showSetupKey
                        ? "text"
                        : "password"
                    }
                    name="setup_key"
                    value={form.setup_key}
                    onChange={updateField}
                    placeholder="Enter setup key"
                    autoComplete="off"
                    required
                  />

                  <button
                    type="button"
                    className="eye-btn"
                    onClick={() =>
                      setShowSetupKey(!showSetupKey)
                    }
                    aria-label={
                      showSetupKey
                        ? "Hide setup key"
                        : "Show setup key"
                    }
                  >
                    {showSetupKey
                      ? <EyeOff size={20} />
                      : <Eye size={20} />}
                  </button>
                </div>

                <p className="field-help">
                  Only authorized administrators can
                  create HR accounts.
                </p>
              </div>
            )}

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            {success && (
              <div className="success-message" role="status">
                {success}
              </div>
            )}

            <button
              type="submit"
              className="primary-btn"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : mode === "login"
                  ? "Sign In"
                  : "Create HR Account"}

              {!loading && <ArrowRight size={19} />}
            </button>
          </form>

          <div className="form-footer">
            <ShieldCheck size={16} />
            Secure HR Access • AI-Powered Recruitment
          </div>
        </div>

        <p className="copyright">
          © {new Date().getFullYear()} HireFlow AI.
          All rights reserved.
        </p>
      </section>
    </main>
  );
}
