"use client";

import Link from "next/link";
import { ArrowRight, Orbit, ShieldCheck, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { api, setToken } from "../../lib/api";

export default function Login() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setLoading(true);
    const form = new FormData(event.currentTarget);
    try {
      const login = await api.post("/auth/login", { email: form.get("email"), password: form.get("password") });
      const token = login.data.data.access_token;
      setToken(token); sessionStorage.setItem("campusos_access", token);
      const role = login.data.data.role;
      window.location.href = role === "admin" ? "/admin/dashboard" : role === "staff" ? "/staff/dashboard" : "/dashboard";
    } catch (request: any) { setError(request?.response?.data?.error?.message || request?.response?.data?.detail || "We could not sign you in. Please try again."); }
    finally { setLoading(false); }
  }
  return <main className="auth-page"><div className="auth-frame"><aside className="auth-aside"><span className="brand-lockup"><i className="logo"><Orbit /></i>campus<span style={{ color: "#7dd3fc" }}>os</span></span><p className="eyebrow" style={{ color: "#8ab6f8", marginTop: 50 }}>CONNECTED CAMPUS SUPPORT</p><h1>One place to report, resolve, and stay informed.</h1><p>CampusOS gives students, service teams, and operations staff a simple shared workspace.</p><div className="auth-stat-grid"><div className="auth-stat"><Sparkles size={17} color="#7dd3fc" /><b>Smart triage</b><span>Priority-aware routing</span></div><div className="auth-stat"><ShieldCheck size={17} color="#7dd3fc" /><b>Role secure</b><span>Access that fits your work</span></div></div></aside><section className="auth-main"><form className="auth-card" onSubmit={submit}><span className="brand-lockup"><i className="logo"><Orbit /></i>campus<span>os</span></span><h1>Welcome back</h1><p className="subtle">Sign in to continue to your campus workspace.</p><label className="input-label">COLLEGE EMAIL</label><input name="email" type="email" placeholder="name@campus.edu" autoComplete="email" required /><label className="input-label">PASSWORD</label><input name="password" type="password" placeholder="Enter your password" autoComplete="current-password" required />{error && <p role="alert" style={{ color: "var(--danger)", marginBottom: 12 }}>{error}</p>}<button className="button" disabled={loading} style={{ width: "100%" }}>{loading ? "Signing in…" : <>Continue <ArrowRight size={16} /></>}</button><p className="auth-footer">New student? <Link href="/signup">Create your account</Link></p></form></section></div></main>;
}
