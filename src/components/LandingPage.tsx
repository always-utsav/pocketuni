import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileText,
  Users,
  Search,
  CheckCircle2,
  AlertCircle,
  X,
  ExternalLink,
  Shield,
  GraduationCap,
  Lock,
  ChevronRight,
  LogIn,
  Loader2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { apiClient } from '../services/apiClient';

export const LandingPage: React.FC = () => {
  const { loginAs, sandboxLogin, authError, clearAuthError, setCurrentUser, setActiveView } = useApp();

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<'STUDENT' | 'FACULTY' | 'SUPER_ADMIN' | null>(null);
  const [isLoadingOAuthUrl, setIsLoadingOAuthUrl] = useState(false);
  const [isSandboxLoading, setIsSandboxLoading] = useState(false);
  const [oauthVerifying, setOauthVerifying] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showDevBypass, setShowDevBypass] = useState(false);
  const [customDevEmail, setCustomDevEmail] = useState('');
  const [demoStep, setDemoStep] = useState(0);

  const demoConversation = [
    {
      q: 'When do MST-1 exams commence for 3rd year AI students?',
      a: 'Per official MITS 2026-27 Academic Calendar, Mid-Semester Test-1 (MST-1) runs from September 8 to September 12, 2026 for 2nd and 3rd year students. [Source: web.mitsgwalior.in/academic-calendar]'
    },
    {
      q: 'Find students open for hackathons skilled in PyTorch and NLP',
      a: 'Found verified peer profiles skilled in PyTorch, Transformer Acceleration, and HuggingFace, open for hackathon collaborations.'
    },
    {
      q: 'Generate leave application for 3 days addressed to Dr. Mausam Chouksey',
      a: 'Drafted official Leave Application addressed to Centre for AI with medical relaxation clauses and attendance undertaking. Ready to Share to Professor.'
    }
  ];

  // Rotate demo prompt
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) return;

    const interval = setInterval(() => {
      setDemoStep((prev) => (prev + 1) % demoConversation.length);
    }, 5500);

    return () => clearInterval(interval);
  }, []);

  // Handle Google OAuth Callback in URL (e.g. ?code=...&state=...)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code && state) {
      setOauthVerifying(true);
      setErrorMessage(null);

      apiClient.googleOAuthCallback(code, state)
        .then((data) => {
          // Clean URL params without reloading
          window.history.replaceState({}, document.title, window.location.pathname);

          const roleNormalized = (data.role || 'STUDENT').toLowerCase() as any;
          const userObj = {
            id: data.user_id,
            googleSub: '',
            email: data.email,
            role: roleNormalized,
            activeContext: data.active_context ? (data.active_context.toLowerCase() as any) : roleNormalized,
            fullName: data.name || data.email.split('@')[0],
            pictureUrl: data.picture_url || '',
            isActive: true,
            lastLoginAt: new Date().toISOString()
          };

          localStorage.setItem('pocketuni_user', JSON.stringify(userObj));
          setCurrentUser(userObj);

          if (roleNormalized === 'super_admin') {
            setActiveView('super_admin_dashboard');
          } else if (roleNormalized === 'faculty') {
            setActiveView('applications_list');
          } else {
            setActiveView('chat');
          }
        })
        .catch((err) => {
          console.error(err);
          const detail = err?.message || 'Google OAuth identity verification failed. Please try again.';
          setErrorMessage(detail);
          setIsLoginModalOpen(true);
        })
        .finally(() => {
          setOauthVerifying(false);
        });
    }
  }, []);

  const handleInitiateGoogleLogin = async () => {
    if (!selectedRole) return;
    setIsLoadingOAuthUrl(true);
    setErrorMessage(null);

    try {
      const data = await apiClient.getGoogleOAuthUrl(selectedRole);
      if (data?.url) {
        window.location.href = data.url;
      } else {
        throw new Error('Google authorization URL was not returned by server.');
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Could not connect to Google OAuth service. Ensure credentials are configured in backend/.env.');
    } finally {
      setIsLoadingOAuthUrl(false);
    }
  };

  const handleDevBypassLogin = (email: string) => {
    const ok = loginAs(email);
    if (ok) {
      setIsLoginModalOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink-navy text-stone-warm flex flex-col justify-between selection:bg-terracotta selection:text-white relative overflow-hidden font-sans">
      {/* Ambient Glow */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-slate-blue/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 -left-40 w-96 h-96 bg-sage/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header */}
      <header className="px-6 lg:px-12 py-6 flex items-center justify-between relative z-10 border-b border-slate-blue/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-ink-dark border border-stone-warm/20 flex items-center justify-center font-heading font-extrabold text-base text-terracotta tracking-tight shadow-subtle">
            PU
          </div>
          <div>
            <span className="font-heading font-bold text-lg tracking-tight text-white flex items-center gap-2">
              PocketUni
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 bg-slate-blue/30 text-stone-warm rounded-full border border-slate-blue/40">
                MITS Gwalior
              </span>
            </span>
          </div>
        </div>

        <button
          onClick={() => {
            clearAuthError();
            setErrorMessage(null);
            setSelectedRole(null);
            setIsLoginModalOpen(true);
          }}
          className="px-5 py-2.5 rounded-xl bg-terracotta hover:bg-terracotta-dark text-white text-xs font-semibold shadow-subtle transition-all flex items-center gap-2"
        >
          <LogIn className="w-4 h-4" />
          Institutional Sign In
        </button>
      </header>

      {/* OAuth Verifying Overlay */}
      {oauthVerifying && (
        <div className="fixed inset-0 z-50 bg-ink-navy/90 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 rounded-2xl bg-ink-dark border border-terracotta/40 flex items-center justify-center mb-4 shadow-elevated">
            <Loader2 className="w-8 h-8 text-terracotta animate-spin" />
          </div>
          <h2 className="text-xl font-heading font-bold text-white mb-2">Verifying Institutional Identity</h2>
          <p className="text-xs text-stone-warm/80 max-w-sm">
            Validating Google token claims against the MITS institutional roster and server allowlist...
          </p>
        </div>
      )}

      {/* Hero Section */}
      <main className="px-6 lg:px-12 py-12 flex-1 flex flex-col justify-center max-w-6xl mx-auto w-full relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Mission */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-blue/20 border border-slate-blue/30 text-[11px] font-semibold text-stone-warm">
              <Sparkles className="w-3.5 h-3.5 text-terracotta" />
              Official AI Assistant for Centre for Artificial Intelligence
            </div>

            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-[1.1]">
              Academic Intelligence, <br />
              <span className="text-terracotta">Grounded in Reality.</span>
            </h1>

            <p className="text-stone-warm/85 text-sm sm:text-base leading-relaxed max-w-xl">
              PocketUni transforms institutional workflows at MITS Gwalior with grounded AI assistance, verified student discovery, and automated formal applications—strictly anchored to official academic syllabuses, schemes, and calendars.
            </p>

            <div className="pt-2 flex flex-wrap gap-4">
              <button
                onClick={() => {
                  clearAuthError();
                  setErrorMessage(null);
                  setSelectedRole('STUDENT');
                  setIsLoginModalOpen(true);
                }}
                className="px-6 py-3 rounded-xl bg-terracotta hover:bg-terracotta-dark text-white text-sm font-semibold shadow-subtle transition-all flex items-center gap-2 group"
              >
                <span>Sign In with Google</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </button>

              <button
                onClick={() => {
                  clearAuthError();
                  setErrorMessage(null);
                  setSelectedRole('FACULTY');
                  setIsLoginModalOpen(true);
                }}
                className="px-6 py-3 rounded-xl bg-ink-dark/80 hover:bg-ink-dark text-stone-warm border border-stone-warm/20 text-sm font-semibold transition-all flex items-center gap-2"
              >
                <GraduationCap className="w-4 h-4 text-slate-blue" />
                <span>Faculty & Mentors</span>
              </button>
            </div>

            {/* Institutional Compliance Badges */}
            <div className="grid grid-cols-3 gap-3 pt-6 border-t border-slate-blue/20">
              <div className="flex items-center gap-2 text-[11px] text-stone-warm/70">
                <CheckCircle2 className="w-4 h-4 text-sage shrink-0" />
                <span>Zero Hallucinations</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-stone-warm/70">
                <CheckCircle2 className="w-4 h-4 text-sage shrink-0" />
                <span>Private Internal Marks</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-stone-warm/70">
                <CheckCircle2 className="w-4 h-4 text-sage shrink-0" />
                <span>Role-Gated RBAC</span>
              </div>
            </div>
          </div>

          {/* Right Column: Live Grounded AI Preview Card */}
          <div className="lg:col-span-5">
            <div className="bg-ink-dark/70 border border-slate-blue/30 rounded-2xl p-6 shadow-elevated backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between border-b border-slate-blue/20 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-sage animate-pulse" />
                  <span className="text-xs font-semibold text-white">Live Grounded Retrieval</span>
                </div>
                <span className="text-[10px] text-stone-warm/60 uppercase font-mono">Gemini 2.5 Flash</span>
              </div>

              <div className="space-y-3 min-h-[160px] flex flex-col justify-center">
                <div className="bg-ink-navy/60 rounded-xl p-3 border border-slate-blue/20 text-xs text-white flex gap-2.5 items-start">
                  <span className="text-terracotta font-bold shrink-0">Q:</span>
                  <span>{demoConversation[demoStep].q}</span>
                </div>

                <div className="bg-slate-blue/15 rounded-xl p-3 border border-slate-blue/30 text-xs text-stone-warm flex gap-2.5 items-start leading-relaxed">
                  <span className="text-sage font-bold shrink-0">A:</span>
                  <span>{demoConversation[demoStep].a}</span>
                </div>
              </div>

              <div className="pt-2 text-[10px] text-stone-warm/60 flex items-center justify-between">
                <span>Verified Source: MITS Centre for AI</span>
                <span className="text-terracotta font-medium">3072-Dim Embeddings</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 lg:px-12 py-6 border-t border-slate-blue/20 text-center text-xs text-stone-warm/60 relative z-10">
        <p>Madhav Institute of Technology & Science, Gwalior (M.P.) — Centre for Artificial Intelligence</p>
      </footer>

      {/* Institutional Sign-In Modal */}
      {isLoginModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-paper border border-stone-warm text-ink-navy rounded-2xl max-w-md w-full p-6 shadow-elevated relative animate-in fade-in zoom-in-95 duration-200">
            {/* Close Button */}
            <button
              onClick={() => {
                setIsLoginModalOpen(false);
                setSelectedRole(null);
                setErrorMessage(null);
              }}
              className="absolute top-4 right-4 p-1.5 rounded-xl hover:bg-stone-warm/50 text-slate-blue transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Modal Header */}
            <div className="mb-5 text-center">
              <div className="w-12 h-12 rounded-2xl bg-ink-navy text-terracotta mx-auto flex items-center justify-center font-heading font-bold text-lg mb-2 shadow-subtle">
                PU
              </div>
              <h2 className="text-xl font-heading font-bold text-ink-navy">
                Institutional Authentication
              </h2>
              <p className="text-xs text-slate-blue mt-1">
                Choose your institutional role to continue with Google OAuth 2.0
              </p>
            </div>

            {/* Error Banner */}
            {(errorMessage || authError) && (
              <div className="mb-4 p-3 rounded-xl bg-terracotta-light border border-terracotta/40 text-terracotta text-xs flex gap-2 items-start leading-relaxed">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold">Access Notice:</p>
                  <p>{errorMessage || authError}</p>
                </div>
              </div>
            )}

            {/* Step 1: Select Role */}
            {!selectedRole ? (
              <div className="space-y-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-blue/80 px-1">
                  Select Your Account Type:
                </p>

                {/* Role 1: Student */}
                <button
                  onClick={() => setSelectedRole('STUDENT')}
                  className="w-full p-3.5 rounded-xl border border-stone-warm hover:border-terracotta hover:bg-stone-warm/20 flex items-center justify-between text-left transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-terracotta-light text-terracotta flex items-center justify-center group-hover:scale-105 transition-transform">
                      <GraduationCap className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-ink-navy group-hover:text-terracotta">
                        Student
                      </p>
                      <p className="text-[11px] text-slate-blue">
                        Requires official <span className="font-mono font-medium text-ink-navy">@mitsgwl.ac.in</span>
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-blue group-hover:text-terracotta group-hover:translate-x-0.5 transition-transform" />
                </button>

                {/* Role 2: Faculty */}
                <button
                  onClick={() => setSelectedRole('FACULTY')}
                  className="w-full p-3.5 rounded-xl border border-stone-warm hover:border-slate-blue hover:bg-stone-warm/20 flex items-center justify-between text-left transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-slate-blue/15 text-slate-blue flex items-center justify-center group-hover:scale-105 transition-transform">
                      <Users className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-ink-navy group-hover:text-slate-blue">
                        Faculty & Mentors
                      </p>
                      <p className="text-[11px] text-slate-blue">
                        Requires official <span className="font-mono font-medium text-ink-navy">@mitsgwalior.in</span>
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-blue group-hover:text-slate-blue group-hover:translate-x-0.5 transition-transform" />
                </button>

                {/* Role 3: Super Admin */}
                <button
                  onClick={() => setSelectedRole('SUPER_ADMIN')}
                  className="w-full p-3.5 rounded-xl border border-stone-warm hover:border-ink-navy hover:bg-stone-warm/20 flex items-center justify-between text-left transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-ink-navy/10 text-ink-navy flex items-center justify-center group-hover:scale-105 transition-transform">
                      <Shield className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-ink-navy">
                        Super Administrator
                      </p>
                      <p className="text-[11px] text-slate-blue">
                        Restricted to explicit server allowlist
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-blue group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            ) : (
              /* Step 2: Confirmation & Continue with Google */
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-stone-warm/40 border border-stone-warm text-center space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-blue">
                    Selected Role
                  </span>
                  <p className="text-base font-bold text-ink-navy">
                    {selectedRole === 'SUPER_ADMIN' ? 'Super Administrator' : selectedRole === 'FACULTY' ? 'Faculty Member / Mentor' : 'Student'}
                  </p>
                  <p className="text-xs text-slate-blue">
                    {selectedRole === 'SUPER_ADMIN'
                      ? 'Authenticated accounts must match the server-managed allowlist.'
                      : selectedRole === 'FACULTY'
                      ? 'Must authenticate using official @mitsgwalior.in Google account.'
                      : 'Must authenticate using official @mitsgwl.ac.in Google account.'}
                  </p>
                </div>

                <button
                  onClick={handleInitiateGoogleLogin}
                  disabled={isLoadingOAuthUrl}
                  className="w-full py-3.5 px-4 rounded-xl bg-ink-navy hover:bg-ink-light text-white font-semibold text-sm flex items-center justify-center gap-3 shadow-subtle transition-all disabled:opacity-50"
                >
                  {isLoadingOAuthUrl ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-terracotta" />
                      <span>Redirecting to Google...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" viewBox="0 0 24 24">
                        <path
                          fill="#4285F4"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="#34A853"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="#FBBC05"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                        />
                        <path
                          fill="#EA4335"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                        />
                      </svg>
                      <span>Continue with Google</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => setSelectedRole(null)}
                  className="w-full text-center text-xs font-semibold text-slate-blue hover:text-ink-navy py-1"
                >
                  ← Choose a different account type
                </button>
              </div>
            )}

            {/* Three-Account Sandbox Testing */}
            <div className="pt-4 mt-4 border-t border-sand">
              <button
                onClick={() => setShowDevBypass(!showDevBypass)}
                className="w-full text-center text-xs font-semibold text-forest hover:text-midnight flex items-center justify-center gap-1.5 py-1"
              >
                <span>Institutional Sandbox Environment (One-Click Testing)</span>
                <span className="text-[10px] bg-sand px-2 py-0.5 rounded font-mono font-bold text-midnight">SANDBOX</span>
              </button>

              {showDevBypass && (
                <div className="mt-3 p-3 rounded-2xl bg-sand/30 border border-sand space-y-2.5">
                  <p className="text-[11px] font-bold text-charcoal uppercase tracking-wider">
                    Select Test Sandbox Persona:
                  </p>
                  <div className="space-y-2">
                    {/* Persona 1: Student Sandbox */}
                    <button
                      onClick={async () => {
                        setIsSandboxLoading(true);
                        setErrorMessage(null);
                        try {
                          const ok = await sandboxLogin('STUDENT');
                          if (ok) setIsLoginModalOpen(false);
                        } catch (err: any) {
                          setErrorMessage(err.message || 'Student sandbox login failed.');
                        } finally {
                          setIsSandboxLoading(false);
                        }
                      }}
                      disabled={isSandboxLoading}
                      className="w-full p-2.5 rounded-xl bg-porcelain border border-sand hover:border-forest flex items-center gap-3 transition-all text-left shadow-sm hover:shadow group disabled:opacity-50"
                    >
                      <div className="w-10 h-10 rounded-lg bg-sage/20 border border-sage/40 flex items-center justify-center shrink-0 text-forest font-heading font-black text-xs">
                        ST
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-bold text-midnight group-hover:text-forest">Student Sandbox</p>
                          <span className="text-[10px] bg-sage/20 text-forest font-semibold px-2 py-0.5 rounded-full">B.Tech CAI</span>
                        </div>
                        <p className="text-[11px] text-charcoal/70 truncate">Academic query, syllabus, applications & peer discovery</p>
                      </div>
                    </button>

                    {/* Persona 2: Faculty Sandbox */}
                    <button
                      onClick={async () => {
                        setIsSandboxLoading(true);
                        setErrorMessage(null);
                        try {
                          const ok = await sandboxLogin('FACULTY');
                          if (ok) setIsLoginModalOpen(false);
                        } catch (err: any) {
                          setErrorMessage(err.message || 'Faculty sandbox login failed.');
                        } finally {
                          setIsSandboxLoading(false);
                        }
                      }}
                      disabled={isSandboxLoading}
                      className="w-full p-2.5 rounded-xl bg-porcelain border border-sand hover:border-forest flex items-center gap-3 transition-all text-left shadow-sm hover:shadow group disabled:opacity-50"
                    >
                      <div className="w-10 h-10 rounded-lg bg-forest/15 border border-forest/30 flex items-center justify-center shrink-0 text-forest font-heading font-black text-xs">
                        FC
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-bold text-midnight group-hover:text-forest">Faculty Sandbox</p>
                          <span className="text-[10px] bg-forest/15 text-forest font-semibold px-2 py-0.5 rounded-full">Mentor & Reviewer</span>
                        </div>
                        <p className="text-[11px] text-charcoal/70 truncate">Incoming formal applications review & approvals</p>
                      </div>
                    </button>

                    {/* Persona 3: Super Admin Sandbox */}
                    <button
                      onClick={async () => {
                        setIsSandboxLoading(true);
                        setErrorMessage(null);
                        try {
                          const ok = await sandboxLogin('SUPER_ADMIN');
                          if (ok) setIsLoginModalOpen(false);
                        } catch (err: any) {
                          setErrorMessage(err.message || 'Super admin sandbox login failed.');
                        } finally {
                          setIsSandboxLoading(false);
                        }
                      }}
                      disabled={isSandboxLoading}
                      className="w-full p-2.5 rounded-xl bg-porcelain border border-sand hover:border-copper flex items-center gap-3 transition-all text-left shadow-sm hover:shadow group disabled:opacity-50"
                    >
                      <div className="w-10 h-10 rounded-lg bg-copper/15 border border-copper/30 flex items-center justify-center shrink-0 text-copper font-heading font-black text-xs">
                        SA
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-bold text-midnight group-hover:text-copper">Super Admin Sandbox</p>
                          <span className="text-[10px] bg-copper/15 text-copper font-semibold px-2 py-0.5 rounded-full">Operations</span>
                        </div>
                        <p className="text-[11px] text-charcoal/70 truncate">Institutional RAG, system health, sync & user oversight</p>
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
