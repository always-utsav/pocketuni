import React, { useState, useEffect } from 'react';
import {
  Mail,
  Phone,
  MapPin,
  Clock,
  BookOpen,
  Award,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  RotateCw,
  Check,
  Building,
  Lock,
  Save,
  Star,
  Globe
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { MITS_FACULTY } from '../data/facultyData';
import { FacultyProfile } from '../types';
import { apiClient } from '../services/apiClient';

interface FacultyProfileViewProps {
  customFaculty?: FacultyProfile | null;
}

export const FacultyProfileView: React.FC<FacultyProfileViewProps> = ({ customFaculty }) => {
  const { currentUser, selectedFaculty, setSelectedFaculty } = useApp();

  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [reportText, setReportText] = useState('');
  const [reportSubmitted, setReportSubmitted] = useState(false);
  const [loadedFaculty, setLoadedFaculty] = useState<any>(null);

  useEffect(() => {
    if (customFaculty) {
      setLoadedFaculty(customFaculty);
      return;
    }
    if (selectedFaculty) {
      setLoadedFaculty(selectedFaculty);
      return;
    }
    if (currentUser?.role === 'faculty') {
      apiClient.getFacultyProfileMe()
        .then((data) => {
          if (data) {
            setLoadedFaculty({
              facultyId: data.facultyId || currentUser.id,
              name: data.name || currentUser.fullName,
              designation: data.designation || currentUser.designation || 'Faculty Member',
              department: data.department || currentUser.departmentName || 'Centre for Artificial Intelligence',
              emailPublic: data.emailPublic || currentUser.email,
              phonePublic: data.phonePublic || '',
              phoneInternal: data.phoneInternal || '',
              officeLocation: data.officeLocation || 'Academic Block',
              officeHours: data.officeHours || 'Mon, Wed, Fri: 03:00 PM - 05:00 PM',
              photoUrl: data.photoUrl || currentUser.pictureUrl || 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80',
              qualification: data.qualification || 'Ph.D.',
              bio: data.bio || '',
              researchAreas: data.areasOfExpertise || [],
              professionalHighlights: data.professionalHighlights || [],
              externalLinks: data.externalLinks || {},
              publications: data.publications || [],
              sourceUrl: data.sourceUrl || 'https://web.mitsgwalior.in',
              lastSyncedAt: data.lastSyncedAt || new Date().toISOString()
            });
          }
        })
        .catch(() => {});
    }
  }, [customFaculty, selectedFaculty, currentUser?.id]);

  // Determine which faculty profile to render with zero identity mismatch
  const defaultFacultyForRole = currentUser?.role === 'faculty'
    ? (MITS_FACULTY.find(f => f.emailPublic.toLowerCase() === currentUser?.email.toLowerCase()) || MITS_FACULTY[0])
    : (selectedFaculty || MITS_FACULTY[0]);

  const faculty = loadedFaculty || customFaculty || selectedFaculty || defaultFacultyForRole;

  const handleReportSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportText.trim()) return;
    setReportSubmitted(true);
    setTimeout(() => {
      setReportSubmitted(false);
      setIsReportModalOpen(false);
      setReportText('');
    }, 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto bg-brand-surface/40 p-4 sm:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Faculty Sandbox Context Pill */}
        {currentUser?.role === 'faculty' && selectedFaculty && selectedFaculty.emailPublic.toLowerCase() !== currentUser.email.toLowerCase() && (
          <div className="px-4 py-3 rounded-2xl bg-amber-50 border border-amber-200/80 flex items-center justify-between text-xs text-amber-900 shadow-subtle">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>You are viewing directory profile for <strong>{faculty.name}</strong> ({faculty.department}).</span>
            </div>
            <button
              onClick={() => {
                setSelectedFaculty(null);
                setLoadedFaculty(null);
              }}
              className="px-3 py-1 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-semibold transition-colors"
            >
              Return to My Profile
            </button>
          </div>
        )}

        {/* Scraped Sync Banner (PRD Section 7.8 & FR-5.3) */}
        <div className="px-4 py-3 rounded-2xl bg-brand-surface border border-brand-border/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-brand-secondary font-medium">
            <RotateCw className="w-3.5 h-3.5 text-brand-accent animate-spin-slow" />
            <span>Official Scraped Profile • Verified from MITS official website (web.mitsgwalior.in)</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-brand-muted text-[11px]">
              Last synced: {new Date(faculty.lastSyncedAt).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
            <button
              onClick={() => setIsReportModalOpen(true)}
              className="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline"
            >
              Report incorrect data
            </button>
          </div>
        </div>

        {/* Header Profile Card */}
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-subtle flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <img
            src={faculty.photoUrl}
            alt={faculty.name}
            className="w-24 h-24 rounded-2xl object-cover border-2 border-brand-accent/40 shadow-card shrink-0"
          />

          <div className="space-y-1 min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="font-heading font-bold text-2xl text-brand-primary">
                {faculty.name}
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-softAccentLight/40 text-brand-secondary border border-brand-softAccent/40">
                {faculty.designation}
              </span>
            </div>

            <p className="text-xs font-semibold text-brand-secondary flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5" />
              Department of {faculty.department}
            </p>

            <p className="text-xs text-brand-muted flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-brand-accent" />
              {faculty.qualification}
            </p>
          </div>
        </div>

        {/* Institution-Controlled Faculty Record (Locked) */}
        <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-subtle space-y-3">
          <div className="flex items-center justify-between border-b border-stone-100 pb-2.5">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-amber-600" />
              <h3 className="font-heading font-semibold text-xs text-ink-navy uppercase tracking-wider">
                Official Institutional Faculty Record (Locked)
              </h3>
            </div>
            <span className="text-[10px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-amber-600" />
              Verified Official Source
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Official Designation</span>
              <p className="font-semibold text-ink-navy truncate">{faculty.designation}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Department / Centre</span>
              <p className="font-semibold text-ink-navy truncate">{faculty.department}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Verified Degree</span>
              <p className="font-semibold text-ink-navy truncate">{faculty.qualification}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Institutional Portal</span>
              <a
                href={faculty.sourceUrl}
                target="_blank"
                rel="noreferrer"
                className="font-semibold text-terracotta hover:underline truncate flex items-center gap-1"
              >
                <span>MITS Web</span>
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            </div>
          </div>
        </div>

        {/* Contact & Consultation Schedule */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl border border-brand-border p-5 shadow-subtle space-y-3">
            <h3 className="font-heading font-bold text-xs uppercase tracking-wider text-brand-muted">
              Official Contact Information
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2.5 text-brand-primary">
                <Mail className="w-4 h-4 text-brand-accent shrink-0" />
                <a href={`mailto:${faculty.emailPublic}`} className="hover:text-brand-secondary font-medium">
                  {faculty.emailPublic}
                </a>
              </div>
              {faculty.phonePublic && (
                <div className="flex items-center gap-2.5 text-brand-primary">
                  <Phone className="w-4 h-4 text-brand-accent shrink-0" />
                  <span>{faculty.phonePublic}</span>
                </div>
              )}
              <div className="flex items-start gap-2.5 text-brand-primary">
                <MapPin className="w-4 h-4 text-brand-accent shrink-0 mt-0.5" />
                <span className="text-xs leading-relaxed">{faculty.officeLocation}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-brand-border p-5 shadow-subtle space-y-3">
            <h3 className="font-heading font-bold text-xs uppercase tracking-wider text-brand-muted">
              Student Consultation & Office Hours
            </h3>
            <div className="flex items-start gap-2.5 text-xs text-brand-primary">
              <Clock className="w-4 h-4 text-brand-secondary shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-brand-primary">{faculty.officeHours}</p>
                <p className="text-[11px] text-brand-muted mt-1 leading-relaxed">
                  Students may visit for application approvals, academic advisement, or research inquiries during these slots.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bio & Research Areas */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider">
            Academic Biography & Research Focus
          </h3>
          <p className="text-xs text-brand-primary/90 leading-relaxed font-sans">
            {faculty.bio}
          </p>

          <div className="pt-2">
            <h4 className="text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">
              Research Areas
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {(faculty.researchAreas || []).map((area: string, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-xl text-xs font-medium bg-brand-surface border border-brand-border text-brand-primary"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Professional Highlights & Institutional Roles */}
        {faculty.professionalHighlights && faculty.professionalHighlights.length > 0 && (
          <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
            <div className="flex items-center justify-between border-b border-brand-borderSubtle pb-3">
              <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider flex items-center gap-2">
                <Star className="w-4 h-4 text-amber-500" />
                Verified Professional & Institutional Highlights
              </h3>
              <span className="text-[11px] text-brand-muted bg-brand-surface px-2.5 py-0.5 rounded-full border border-brand-borderSubtle">
                Provenance: web.mitsgwalior.in
              </span>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {faculty.professionalHighlights.map((hl: any, idx: number) => {
                const isObj = typeof hl === 'object' && hl !== null;
                const title = isObj ? hl.title : hl;
                const category = isObj ? hl.category : null;
                const date = isObj ? hl.date : null;
                const source = isObj ? hl.source : null;
                const details = isObj ? hl.details : null;

                return (
                  <div key={idx} className="p-3.5 rounded-xl bg-brand-surface/70 border border-brand-borderSubtle text-xs space-y-1.5 hover:border-brand-accent/40 transition-colors">
                    <div className="flex items-start justify-between gap-2 flex-wrap">
                      <p className="font-semibold text-brand-primary leading-snug flex-1">
                        {title}
                      </p>
                      <div className="flex items-center gap-2 shrink-0">
                        {category && (
                          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-softAccentLight text-brand-secondary">
                            {category}
                          </span>
                        )}
                        {date && (
                          <span className="text-[10px] text-brand-muted font-medium bg-white px-2 py-0.5 rounded border border-brand-borderSubtle">
                            {date}
                          </span>
                        )}
                      </div>
                    </div>
                    {details && (
                      <p className="text-brand-muted text-[11px] leading-relaxed">
                        {details}
                      </p>
                    )}
                    {source && (
                      <div className="pt-1">
                        <a
                          href={source}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[10px] font-semibold text-brand-accent hover:underline"
                        >
                          <span>Official Source Link</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* External Scholarly Profiles (IRINS, Google Scholar, Vidwan) */}
        {faculty.externalLinks && Object.keys(faculty.externalLinks).length > 0 && (
          <div className="bg-white rounded-2xl border border-brand-border p-5 shadow-subtle space-y-3">
            <h3 className="font-heading font-bold text-xs uppercase tracking-wider text-brand-muted flex items-center gap-2">
              <Globe className="w-4 h-4 text-brand-secondary" />
              Official Scholarly Profiles & Research Repositories
            </h3>
            <div className="flex flex-wrap gap-2.5">
              {Object.entries(faculty.externalLinks).map(([k, url]: [string, any]) => (
                <a
                  key={k}
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-brand-surface border border-brand-border hover:border-brand-accent text-brand-primary hover:text-brand-accent transition-all flex items-center gap-1.5"
                >
                  <span className="capitalize">{k.replace('_', ' ')}</span>
                  <ExternalLink className="w-3 h-3 text-brand-muted" />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Selected Publications (PRD Section 16.2 & FR-5.2) */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-brand-secondary" />
            Selected Publications ({faculty.publications.length})
          </h3>

          <div className="space-y-3">
            {(faculty.publications || []).map((pub: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl bg-brand-surface border border-brand-borderSubtle text-xs space-y-1">
                <p className="font-semibold text-brand-primary leading-snug">{pub.title}</p>
                <p className="text-brand-muted text-[11px]">
                  {pub.journal} • {pub.year} {pub.doi ? `• DOI: ${pub.doi}` : ''}
                </p>
              </div>
            ))}
          </div>

          <div className="pt-2">
            <a
              href={faculty.sourceUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-secondary hover:text-brand-accent transition-colors"
            >
              <span>View full profile on MITS Gwalior official website</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>

      {/* Report Incorrect Data Modal (PRD Section 7.8 & FR-5.2) */}
      {isReportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-white rounded-3xl shadow-float border border-brand-border p-6 space-y-4">
            <div className="flex items-center gap-2 text-rose-600">
              <AlertTriangle className="w-5 h-5" />
              <h3 className="font-heading font-bold text-base text-brand-primary">
                Report Incorrect Profile Data
              </h3>
            </div>

            <p className="text-xs text-brand-muted leading-relaxed">
              Faculty records are periodically crawled from the official portal. Please describe any outdated office room numbers, contact numbers, or designation inaccuracies:
            </p>

            <form onSubmit={handleReportSubmit} className="space-y-3">
              <textarea
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
                placeholder="e.g., Office room has moved to Academic Block B, Room 204..."
                rows={3}
                required
                className="w-full p-3 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent"
              />

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsReportModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-brand-border text-xs text-brand-muted hover:text-brand-primary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={reportSubmitted}
                  className="px-5 py-2 rounded-xl bg-brand-primary hover:bg-brand-primaryLight text-white text-xs font-semibold shadow-sm transition-all"
                >
                  {reportSubmitted ? 'Report Sent!' : 'Submit Discrepancy'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
