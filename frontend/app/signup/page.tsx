"use client";

import Link from "next/link";
import { ArrowRight, Orbit, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { api } from "../../lib/api";

export default function Signup() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    const form = new FormData(event.currentTarget);
    if (form.get("password") !== form.get("confirm_password")) { setError("Passwords do not match."); return; }
    try {
      await api.post("/auth/register", { full_name: form.get("full_name"), email: form.get("email"), phone: form.get("phone") || null, student_id: form.get("student_id"), department: form.get("department"), year: Number(form.get("year")), section: form.get("section"), government_id: form.get("government_id"), permanent_address: form.get("permanent_address"), password: form.get("password") });
      setMessage("Registration submitted. An administrator must approve your account before you sign in."); event.currentTarget.reset();
    } catch (request: any) { setError(request?.response?.data?.error?.message || request?.response?.data?.detail || "Unable to create account. Please try again."); }
  }
  return <main className="auth-page"><div className="auth-frame"><aside className="auth-aside"><span className="brand-lockup"><i className="logo"><Orbit /></i>campus<span style={{ color: "#7dd3fc" }}>os</span></span><p className="eyebrow" style={{ color: "#8ab6f8", marginTop: 50 }}>VERIFIED STUDENT ACCESS</p><h1>One secure profile for every campus request.</h1><p>Your government identity and address stay private. An administrator verifies every new registration.</p><div className="auth-stat-grid"><div className="auth-stat"><ShieldCheck size={17} color="#7dd3fc" /><b>Verified</b><span>Account approval flow</span></div><div className="auth-stat"><b>Private</b><span>Protected identity details</span></div></div></aside><section className="auth-main"><form className="auth-card" onSubmit={submit}><span className="brand-lockup"><i className="logo"><Orbit /></i>campus<span>os</span></span><h1>Create your account</h1><p className="subtle">All marked details are required for verification.</p><label className="input-label">FULL NAME</label><input name="full_name" required minLength={2}/><label className="input-label">COLLEGE EMAIL</label><input name="email" type="email" required/><label className="input-label">STUDENT ID</label><input name="student_id" required/><label className="input-label">DEPARTMENT</label><input name="department" placeholder="Computer Science" required/><label className="input-label">YEAR</label><select name="year" defaultValue="1"><option value="1">Year 1</option><option value="2">Year 2</option><option value="3">Year 3</option><option value="4">Year 4</option></select><label className="input-label">SECTION</label><input name="section" placeholder="A" required/><label className="input-label">PHONE NUMBER</label><input name="phone" inputMode="tel" required/><label className="input-label">GOVERNMENT ID NUMBER</label><input name="government_id" placeholder="Aadhaar / Passport / DL" required/><label className="input-label">PERMANENT ADDRESS</label><textarea name="permanent_address" rows={3} required/><label className="input-label">PASSWORD</label><input name="password" type="password" minLength={8} placeholder="Uppercase, lowercase, number" required/><label className="input-label">CONFIRM PASSWORD</label><input name="confirm_password" type="password" minLength={8} required/>{error && <p role="alert" style={{ color: "var(--danger)" }}>{error}</p>}{message && <p role="status" style={{ color: "var(--success)" }}>{message}</p>}<button className="button" style={{ width: "100%" }}>Submit for approval <ArrowRight size={16}/></button><p className="auth-footer">Already approved? <Link href="/login">Sign in</Link></p></form></section></div></main>;
}
