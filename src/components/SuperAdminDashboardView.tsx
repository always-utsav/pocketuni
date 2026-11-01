import React, { useState, useEffect } from 'react';
import {
  Layers,
  Upload,
  FileText,
  Calendar,
  Clock,
  BookOpen,
  Award,
  Users,
  GraduationCap,
  Building,
  History,
  Shield,
  Settings,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  Plus,
  Eye,
  Filter,
  Download,
  Database,
  ExternalLink,
  ChevronRight,
  FileSpreadsheet,
  Globe,
  Check,
  X,
  ArrowUpRight,
  Play
} from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { DocumentReviewModal } from './DocumentReviewModal';

export const SuperAdminDashboardView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [stats, setStats] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [timetables, setTimetables] = useState<any[]>([]);
  const [datesheets, setDatesheets] = useState<any[]>([]);
  const [calendars, setCalendars] = useState<any[]>([]);
  const [resultsList, setResultsList] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [facultyList, setFacultyList] = useState<any[]>([]);
  const [studentsList, setStudentsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Document upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('');
  const [uploadYear, setUploadYear] = useState('2026-2027');
  const [uploadBatch, setUploadBatch] = useState('');
  const [uploadProgramme, setUploadProgramme] = useState('B.Tech');
  const [uploadBranch, setUploadBranch] = useState('Centre for Artificial Intelligence');
  const [uploadSemester, setUploadSemester] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Review modal state
  const [reviewDocId, setReviewDocId] = useState<string | null>(null);

  // Search & filter
  const [docFilterCategory, setDocFilterCategory] = useState<string>('ALL');
  const [docFilterStatus, setDocFilterStatus] = useState<string>('ALL');
  const [docFilterSemester, setDocFilterSemester] = useState<string>('ALL');
  const [docSearchQuery, setDocSearchQuery] = useState<string>('');

  // Results import
  const [resultsFile, setResultsFile] = useState<File | null>(null);
  const [resultsSession, setResultsSession] = useState('June 2026');
  const [resultsImporting, setResultsImporting] = useState(false);
  const [resultsMsg, setResultsMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Roster Management (Module 2.5)
  const [rosterEntityType, setRosterEntityType] = useState<'students' | 'faculty'>('students');
  const [rosterFile, setRosterFile] = useState<File | null>(null);
  const [rosterPreview, setRosterPreview] = useState<any | null>(null);
  const [rosterPreviewing, setRosterPreviewing] = useState(false);
  const [rosterImporting, setRosterImporting] = useState(false);
  const [rosterMessage, setRosterMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [rosterSyncStatus, setRosterSyncStatus] = useState<any | null>(null);
  const [downloadingExport, setDownloadingExport] = useState(false);

  // Web Crawler & Portals (Module 2.5 Addendum)
  const [websiteSources, setWebsiteSources] = useState<any[]>([]);
  const [websitePortals, setWebsitePortals] = useState<any[]>([]);
  const [websiteStats, setWebsiteStats] = useState<any | null>(null);
  const [crawlMaxPages, setCrawlMaxPages] = useState<number>(10);
  const [crawling, setCrawling] = useState(false);
  const [crawlMessage, setCrawlMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadOverviewData();
  }, []);

  const loadOverviewData = async () => {
    setLoading(true);
    try {
      const [sData, hData, dData, aData] = await Promise.allSettled([
        apiClient.getAdminStats(),
        apiClient.getSystemHealth(),
        apiClient.listDocuments(),
        apiClient.getAuditLogs(30)
      ]);
      if (sData.status === 'fulfilled') setStats(sData.value);
      if (hData.status === 'fulfilled') setHealth(hData.value);
      if (dData.status === 'fulfilled') setDocuments(dData.value);
      if (aData.status === 'fulfilled') setAuditLogs(aData.value);
    } catch (e) {
      console.warn('Admin load failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadTabSpecificData = async (tab: string) => {
    setActiveTab(tab);
    try {
      if (tab === 'timetables' && timetables.length === 0) {
        const t = await apiClient.getTimetables();
        setTimetables(t);
      } else if (tab === 'datesheets' && datesheets.length === 0) {
        const d = await apiClient.getDatesheets();
        setDatesheets(d);
      } else if (tab === 'calendars' && calendars.length === 0) {
        const c = await apiClient.getCalendars();
        setCalendars(c);
      } else if (tab === 'results' && resultsList.length === 0) {
        const r = await apiClient.getAllResultsAdmin();
        setResultsList(r);
      } else if (tab === 'templates' && templates.length === 0) {
        const t = await apiClient.getTemplates();
        setTemplates(t);
      } else if (tab === 'faculty' && facultyList.length === 0) {
        const f = await apiClient.getFacultyDirectory();
        setFacultyList(f);
      } else if (tab === 'students' && studentsList.length === 0) {
        const st = await apiClient.getStudentDiscovery();
        setStudentsList(st);
      } else if (tab === 'documents') {
        const d = await apiClient.listDocuments();
        setDocuments(d);
      } else if (tab === 'audit') {
        const a = await apiClient.getAuditLogs(60);
        setAuditLogs(a);
      } else if (tab === 'roster') {
        const status = await apiClient.getRosterSyncStatus();
        setRosterSyncStatus(status);
      } else if (tab === 'website') {
        const [srcs, portals, wStats] = await Promise.all([
          apiClient.getWebsiteSources(),
          apiClient.getInstitutionalPortals(),
          apiClient.getWebsiteCrawlerStats()
        ]);
        setWebsiteSources(srcs);
        setWebsitePortals(portals);
        setWebsiteStats(wStats);
      }
    } catch (e) {
      console.warn('Tab load failed:', e);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      setUploadMessage(null);
      const res = await apiClient.uploadDocument(uploadFile, {
        title: uploadTitle.trim() || undefined,
        category: uploadCategory || undefined,
        academicYear: uploadYear || undefined,
        batch: uploadBatch || undefined,
        programme: uploadProgramme || undefined,
        branch: uploadBranch || undefined,
        semester: uploadSemester || undefined,
      });
      setUploadMessage({
        type: 'success',
        text: `Successfully uploaded '${uploadFile.name}'. Extracted ${res.extractedContents?.length || 0} blocks and ${res.extractedTables?.length || 0} tables.`
      });
      setUploadFile(null);
      setUploadTitle('');
      setUploadCategory('');
      setUploadBatch('');
      setUploadSemester('');
      loadOverviewData();
      // Prompt open review modal
      setReviewDocId(res.id);
    } catch (err: any) {
      setUploadMessage({
        type: 'error',
        text: err.message || 'Document upload or extraction failed.'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleResultsImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resultsFile) return;
    try {
      setResultsImporting(true);
      setResultsMsg(null);
      const res = await apiClient.importResults(resultsFile, resultsSession);
      setResultsMsg({
        type: 'success',
        text: `Results imported successfully: ${res.imported_entries} subject entries recorded.`
      });
      setResultsFile(null);
      const updated = await apiClient.getAllResultsAdmin();
      setResultsList(updated);
    } catch (err: any) {
      setResultsMsg({
        type: 'error',
        text: err.message || 'Results validation failed.'
      });
    } finally {
      setResultsImporting(false);
    }
  };

  const handleRosterPreview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rosterFile) return;
    try {
      setRosterPreviewing(true);
      setRosterMessage(null);
      const prev = await apiClient.previewRoster(rosterFile, rosterEntityType);
      setRosterPreview(prev);
    } catch (err: any) {
      setRosterMessage({
        type: 'error',
        text: err.message || 'Roster validation preview failed.'
      });
    } finally {
      setRosterPreviewing(false);
    }
  };

  const handleRosterImport = async () => {
    if (!rosterFile) return;
    try {
      setRosterImporting(true);
      setRosterMessage(null);
      const res = await apiClient.importRoster(rosterFile, rosterEntityType);
      setRosterMessage({
        type: 'success',
        text: `Roster import committed: ${res.created_users_count} users created, ${res.updated_users_count} updated, ${res.total_rows_imported} records committed to PostgreSQL.`
      });
      setRosterFile(null);
      setRosterPreview(null);
      const status = await apiClient.getRosterSyncStatus();
      setRosterSyncStatus(status);
      loadOverviewData();
    } catch (err: any) {
      setRosterMessage({
        type: 'error',
        text: err.message || 'Roster import commit failed.'
      });
    } finally {
      setRosterImporting(false);
    }
  };

  const handleDownloadWorkbook = async (entity: 'students' | 'faculty') => {
    try {
      setDownloadingExport(true);
      const token = localStorage.getItem('pocketuni_token');
      const res = await fetch(`/api/v1/admin/roster/export/${entity}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      if (!res.ok) {
        throw new Error(`Export failed with HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pocketuni_${entity}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    } finally {
      setDownloadingExport(false);
    }
  };

  const handleTriggerCrawl = async () => {
    try {
      setCrawling(true);
      setCrawlMessage(null);
      const res = await apiClient.triggerWebsiteCrawl(crawlMaxPages);
      setCrawlMessage({
        type: 'success',
        text: `Crawling completed: ${res.crawled_pages || 0} pages fetched, ${res.extracted_documents || 0} extracted, ${res.embedded_chunks || 0} RAG chunks generated.`
      });
      const [srcs, portals, wStats] = await Promise.all([
        apiClient.getWebsiteSources(),
        apiClient.getInstitutionalPortals(),
        apiClient.getWebsiteCrawlerStats()
      ]);
      setWebsiteSources(srcs);
      setWebsitePortals(portals);
      setWebsiteStats(wStats);
    } catch (err: any) {
      setCrawlMessage({
        type: 'error',
        text: err.message || 'Website crawl failed.'
      });
    } finally {
      setCrawling(false);
    }
  };

  const filteredDocs = documents.filter((d) => {
    const matchesCat = docFilterCategory === 'ALL' || d.category === docFilterCategory;
    const matchesStat = docFilterStatus === 'ALL' || d.status === docFilterStatus;
    const matchesSem = docFilterSemester === 'ALL' || (d.semester && d.semester.toLowerCase().includes(docFilterSemester.toLowerCase()));
    const matchesQ =
      !docSearchQuery.trim() ||
      d.title.toLowerCase().includes(docSearchQuery.toLowerCase()) ||
      d.fileName.toLowerCase().includes(docSearchQuery.toLowerCase());
    return matchesCat && matchesStat && matchesSem && matchesQ;
  });

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-paper overflow-hidden text-ink-navy">
      {/* Top Banner */}
      <div className="px-6 py-4 border-b border-stone-warm bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-heading font-bold text-lg text-ink-navy">Institutional Super Admin Portal</h2>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-ink-navy text-stone-warm">
              MITS Gwalior
            </span>
          </div>
          <p className="text-xs text-slate-blue">
            Authoritative institutional records, extraction pipeline, target audience governance & sensitive marks repository.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              loadOverviewData();
              loadTabSpecificData(activeTab);
            }}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl border border-stone-warm text-slate-blue hover:text-ink-navy hover:bg-paper text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Records</span>
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sub-navigation sidebar */}
        <div className="w-60 border-r border-stone-warm bg-paper/60 p-3 overflow-y-auto shrink-0 space-y-1">
          <div className="text-[11px] font-bold text-slate-blue uppercase tracking-wider px-2.5 py-1.5">
            Administration
          </div>
          {[
            { id: 'overview', label: '1. Overview', icon: Layers },
            { id: 'upload', label: '2. Upload Documents', icon: Upload },
            { id: 'documents', label: '3. Document Library', icon: FileText },
            { id: 'timetables', label: '4. Timetable Management', icon: Clock },
            { id: 'datesheets', label: '5. Exam Datesheets', icon: Calendar },
            { id: 'calendars', label: '6. Academic Calendar', icon: Calendar },
            { id: 'notices', label: '7. Notices & Announcements', icon: BookOpen },
            { id: 'results', label: '8. Results & Marks (Restricted)', icon: Award },
            { id: 'students', label: '9. Student Records', icon: Users },
            { id: 'faculty', label: '10. Faculty Directory', icon: GraduationCap },
            { id: 'departments', label: '11. Depts & Programmes', icon: Building },
            { id: 'templates', label: '12. Application Templates', icon: BookOpen },
            { id: 'versions', label: '13. Version History', icon: History },
            { id: 'audit', label: '14. Immutable Audit Logs', icon: Shield },
            { id: 'settings', label: '15. System Health & Settings', icon: Settings },
            { id: 'roster', label: '16. Roster & Excel Sync', icon: FileSpreadsheet },
            { id: 'website', label: '17. Web Crawler & Portals', icon: Globe },
          ].map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => loadTabSpecificData(item.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-left transition-all ${
                  isActive
                    ? 'bg-ink-navy text-white shadow-subtle font-semibold'
                    : 'text-slate-blue hover:text-ink-navy hover:bg-stone-warm/50'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-terracotta' : 'text-slate-blue'}`} />
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content Pane */}
        <div className="flex-1 overflow-y-auto p-6 bg-white">
          {/* SECTION 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6 max-w-5xl">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Database & Operational Overview</h3>
                <p className="text-xs text-slate-blue">Live counts queried directly from local PostgreSQL instance.</p>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Total Students</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {stats?.totalStudents ?? '—'}
                  </p>
                  <span className="text-[10px] text-sage font-medium">Centre for AI</span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Verified Faculty</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {stats?.totalFaculty ?? '—'}
                  </p>
                  <span className="text-[10px] text-slate-blue font-medium">web.mitsgwalior.in</span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Institutional Docs</p>
                  <p className="font-heading font-extrabold text-2xl text-terracotta mt-1">
                    {stats?.totalDocuments ?? '—'}
                  </p>
                  <span className="text-[10px] text-slate-blue font-medium">
                    {stats?.publishedDocuments ?? 0} Published • {stats?.pendingReviewDocuments ?? 0} In Review
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Audit Events</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {stats?.totalAudits ?? '—'}
                  </p>
                  <span className="text-[10px] text-slate-blue font-medium">Cryptographic Trace</span>
                </div>
              </div>

              {/* System Health Strip */}
              <div className="p-4 rounded-2xl bg-paper border border-stone-warm flex flex-wrap items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-slate-blue" />
                  <div>
                    <p className="font-semibold text-ink-navy">Database Connection</p>
                    <p className="text-slate-blue">{health?.database || 'PostgreSQL Localhost (5432)'}</p>
                  </div>
                </div>

                <div>
                  <p className="font-semibold text-ink-navy">Storage Subsystem</p>
                  <p className="text-slate-blue">{health?.storageAccessible ? 'Local Filesystem Active' : 'Restricted'}</p>
                </div>

                <div>
                  <p className="font-semibold text-ink-navy">OCR Engine</p>
                  <p className="text-slate-blue">
                    {health?.ocrAvailable ? 'Tesseract OCR Ready' : 'Pending Configuration (Image Fallback Active)'}
                  </p>
                </div>
              </div>

              {/* Recent Audit Activities */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-heading font-semibold text-sm text-ink-navy">Recent Security & Administrative Actions</h4>
                  <button
                    onClick={() => setActiveTab('audit')}
                    className="text-xs text-terracotta font-semibold hover:underline flex items-center gap-1"
                  >
                    <span>View all logs</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                      <tr>
                        <th className="px-4 py-2.5">Timestamp</th>
                        <th className="px-4 py-2.5">Actor</th>
                        <th className="px-4 py-2.5">Action</th>
                        <th className="px-4 py-2.5">Summary</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-warm text-ink-navy">
                      {auditLogs.slice(0, 6).map((log) => (
                        <tr key={log.id} className="hover:bg-paper">
                          <td className="px-4 py-2 text-slate-blue font-mono text-[11px]">
                            {new Date(log.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </td>
                          <td className="px-4 py-2 font-medium">{log.actorEmail}</td>
                          <td className="px-4 py-2">
                            <span className="px-2 py-0.5 rounded-full bg-stone-warm text-[10px] font-mono font-semibold">
                              {log.action}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-slate-blue truncate max-w-xs">{log.changeSummary}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 2: UPLOAD DOCUMENTS */}
          {activeTab === 'upload' && (
            <div className="max-w-2xl space-y-6">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Upload Institutional Document</h3>
                <p className="text-xs text-slate-blue">
                  Upload official timetables, datesheets, calendars, and academic notices. The document will be verified, stored locally, digested with SHA-256, and sent to the extraction engine.
                </p>
              </div>

              {uploadMessage && (
                <div
                  className={`p-4 rounded-xl text-xs flex items-center gap-2 ${
                    uploadMessage.type === 'success'
                      ? 'bg-sage-bg border border-sage-border text-sage font-medium'
                      : 'bg-rose-50 border border-rose-200 text-rose-700'
                  }`}
                >
                  {uploadMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                  <span>{uploadMessage.text}</span>
                </div>
              )}

              <form onSubmit={handleFileUpload} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-ink-navy mb-1">Document Display Title (Optional)</label>
                    <input
                      type="text"
                      value={uploadTitle}
                      onChange={(e) => setUploadTitle(e.target.value)}
                      placeholder="e.g. Centre for AI Even Semester Timetable 2026-27"
                      className="w-full px-3 py-2 text-xs rounded-xl border border-stone-warm bg-paper focus:outline-none focus:border-terracotta"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-ink-navy mb-1">Document Category</label>
                    <select
                      value={uploadCategory}
                      onChange={(e) => setUploadCategory(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-stone-warm bg-paper focus:outline-none focus:border-terracotta"
                    >
                      <option value="">Auto-Detect from Content</option>
                      <option value="TIMETABLE">TIMETABLE</option>
                      <option value="SCHEME_OF_STUDY">SCHEME OF STUDY</option>
                      <option value="SYLLABUS">SYLLABUS</option>
                      <option value="INDUCTION_NOTICE">INDUCTION NOTICE</option>
                      <option value="GENERAL_NOTICE">GENERAL NOTICE</option>
                      <option value="EXAMINATION_DATESHEET">EXAMINATION DATESHEET</option>
                      <option value="INTERNAL_MARKS">INTERNAL MARKS (Confidential)</option>
                      <option value="FINAL_RESULTS">FINAL RESULTS</option>
                      <option value="ACADEMIC_CALENDAR">ACADEMIC CALENDAR</option>
                      <option value="PROFESSIONAL_CERTIFICATION_LIST">PROFESSIONAL CERTIFICATION LIST</option>
                      <option value="COURSE_STRUCTURE">COURSE STRUCTURE</option>
                      <option value="LAB_MANUAL">LAB MANUAL</option>
                      <option value="ACADEMIC_POLICY">ACADEMIC POLICY</option>
                      <option value="FACULTY_DOCUMENT">FACULTY DOCUMENT</option>
                      <option value="GENERAL_INSTITUTIONAL_DOCUMENT">GENERAL INSTITUTIONAL DOCUMENT</option>
                      <option value="OTHER">OTHER</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-ink-navy mb-1">Academic Year</label>
                    <input
                      type="text"
                      value={uploadYear}
                      onChange={(e) => setUploadYear(e.target.value)}
                      placeholder="e.g. 2026-2027"
                      className="w-full px-3 py-2 text-xs rounded-xl border border-stone-warm bg-paper focus:outline-none focus:border-terracotta"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-ink-navy mb-1">Applicable Batch</label>
                    <input
                      type="text"
                      value={uploadBatch}
                      onChange={(e) => setUploadBatch(e.target.value)}
                      placeholder="e.g. 2025-26, 2024-25"
                      className="w-full px-3 py-2 text-xs rounded-xl border border-stone-warm bg-paper focus:outline-none focus:border-terracotta"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-ink-navy mb-1">Semester</label>
                    <input
                      type="text"
                      value={uploadSemester}
                      onChange={(e) => setUploadSemester(e.target.value)}
                      placeholder="e.g. III Semester, V Semester"
                      className="w-full px-3 py-2 text-xs rounded-xl border border-stone-warm bg-paper focus:outline-none focus:border-terracotta"
                    />
                  </div>
                </div>

                <div className="border-2 border-dashed border-stone-warm hover:border-terracotta rounded-2xl p-8 text-center transition-all bg-paper/50">
                  <Upload className="w-8 h-8 text-slate-blue mx-auto mb-2" />
                  <p className="text-xs font-semibold text-ink-navy">
                    {uploadFile ? uploadFile.name : 'Choose a document file to attach'}
                  </p>
                  <p className="text-[11px] text-slate-blue mt-1">
                    Supported: PDF, DOCX, XLSX, XLS, CSV, TXT, PNG, JPG (Max 25MB)
                  </p>
                  <input
                    type="file"
                    id="doc-upload-input"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadFile(e.target.files[0]);
                      }
                    }}
                  />
                  <div className="mt-4">
                    <label
                      htmlFor="doc-upload-input"
                      className="px-4 py-2 rounded-xl bg-ink-navy text-white text-xs font-semibold hover:bg-ink-light cursor-pointer shadow-subtle inline-block"
                    >
                      Browse Local Files
                    </label>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={!uploadFile || uploading}
                  className="w-full py-2.5 rounded-xl bg-terracotta hover:bg-terracotta-hover text-white text-xs font-semibold shadow-subtle disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Extracting Content & Classifying...</span>
                    </>
                  ) : (
                    <span>Upload & Trigger Extraction Pipeline</span>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* SECTION 3: DOCUMENT LIBRARY */}
          {activeTab === 'documents' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h3 className="font-heading font-bold text-base text-ink-navy">Document Library</h3>
                  <p className="text-xs text-slate-blue">Manage extracted institutional assets and publication state.</p>
                </div>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="px-3.5 py-1.5 rounded-xl bg-terracotta text-white text-xs font-semibold hover:bg-terracotta-hover flex items-center gap-1.5 self-start shadow-subtle"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Upload Document</span>
                </button>
              </div>

              {/* Filters */}
              <div className="flex flex-wrap items-center gap-3 bg-paper p-3 rounded-xl border border-stone-warm">
                <div className="relative flex-1 min-w-[200px]">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-blue" />
                  <input
                    type="text"
                    value={docSearchQuery}
                    onChange={(e) => setDocSearchQuery(e.target.value)}
                    placeholder="Search documents by title or filename..."
                    className="w-full pl-8 pr-3 py-1.5 text-xs bg-white rounded-lg border border-stone-warm focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <Filter className="w-3.5 h-3.5 text-slate-blue" />
                  <select
                    value={docFilterCategory}
                    onChange={(e) => setDocFilterCategory(e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg border border-stone-warm bg-white focus:outline-none text-ink-navy"
                  >
                    <option value="ALL">All Categories</option>
                    <option value="TIMETABLE">TIMETABLE</option>
                    <option value="SCHEME_OF_STUDY">SCHEME OF STUDY</option>
                    <option value="SYLLABUS">SYLLABUS</option>
                    <option value="INDUCTION_NOTICE">INDUCTION NOTICE</option>
                    <option value="GENERAL_NOTICE">GENERAL NOTICE</option>
                    <option value="EXAMINATION_DATESHEET">EXAMINATION DATESHEET</option>
                    <option value="INTERNAL_MARKS">INTERNAL MARKS</option>
                    <option value="FINAL_RESULTS">FINAL RESULTS</option>
                    <option value="ACADEMIC_CALENDAR">ACADEMIC CALENDAR</option>
                    <option value="PROFESSIONAL_CERTIFICATION_LIST">PROFESSIONAL CERTIFICATION LIST</option>
                    <option value="COURSE_STRUCTURE">COURSE STRUCTURE</option>
                    <option value="LAB_MANUAL">LAB MANUAL</option>
                    <option value="ACADEMIC_POLICY">ACADEMIC POLICY</option>
                    <option value="FACULTY_DOCUMENT">FACULTY DOCUMENT</option>
                    <option value="GENERAL_INSTITUTIONAL_DOCUMENT">GENERAL INSTITUTIONAL</option>
                    <option value="OTHER">OTHER</option>
                  </select>

                  <select
                    value={docFilterStatus}
                    onChange={(e) => setDocFilterStatus(e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg border border-stone-warm bg-white focus:outline-none text-ink-navy"
                  >
                    <option value="ALL">All Statuses</option>
                    <option value="NEEDS_REVIEW">Needs Review</option>
                    <option value="READY_TO_PUBLISH">Ready to Publish</option>
                    <option value="PUBLISHED">Published</option>
                    <option value="ARCHIVED">Archived</option>
                    <option value="SUPERSEDED">Superseded</option>
                  </select>
                </div>
              </div>

              {/* Documents Table */}
              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Title & File</th>
                      <th className="px-4 py-2.5">Category</th>
                      <th className="px-4 py-2.5">Version</th>
                      <th className="px-4 py-2.5">Status</th>
                      <th className="px-4 py-2.5">Uploaded</th>
                      <th className="px-4 py-2.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {filteredDocs.map((doc) => (
                      <tr key={doc.id} className="hover:bg-paper">
                        <td className="px-4 py-2.5">
                          <p className="font-semibold text-ink-navy">{doc.title}</p>
                          <p className="text-[11px] text-slate-blue">{doc.fileName} • {doc.fileExtension.toUpperCase()}</p>
                        </td>
                        <td className="px-4 py-2.5">
                          <span className="px-2 py-0.5 rounded-full bg-slate-subtle text-slate-blue text-[10px] font-semibold">
                            {doc.category}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 font-mono text-[11px]">v{doc.currentVersionNo}</td>
                        <td className="px-4 py-2.5">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                            doc.status === 'PUBLISHED' ? 'bg-sage-bg text-sage border border-sage-border' :
                            doc.status === 'NEEDS_REVIEW' ? 'bg-amber-50 text-amber-800 border border-amber-200' :
                            doc.status === 'READY_TO_PUBLISH' ? 'bg-blue-50 text-slate-blue border border-slate-subtle' :
                            'bg-stone-warm text-ink-navy'
                          }`}>
                            {doc.status.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-slate-blue text-[11px]">
                          {new Date(doc.uploadedAt).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-2.5 text-right space-x-1">
                          <button
                            onClick={() => setReviewDocId(doc.id)}
                            className="px-2.5 py-1 rounded-lg bg-ink-navy text-white text-[11px] font-semibold hover:bg-ink-light"
                          >
                            Review / Publish
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 4: TIMETABLE MANAGEMENT */}
          {activeTab === 'timetables' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Timetable Management</h3>
                <p className="text-xs text-slate-blue">Structured lecture slots and lab timings for Centre for AI.</p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Day</th>
                      <th className="px-4 py-2.5">Time</th>
                      <th className="px-4 py-2.5">Subject & Code</th>
                      <th className="px-4 py-2.5">Faculty</th>
                      <th className="px-4 py-2.5">Room</th>
                      <th className="px-4 py-2.5">Branch</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {timetables.map((t) => (
                      <tr key={t.id} className="hover:bg-paper">
                        <td className="px-4 py-2 font-semibold">{t.day}</td>
                        <td className="px-4 py-2 font-mono text-[11px]">{t.startTime} – {t.endTime}</td>
                        <td className="px-4 py-2 font-medium">{t.subject} ({t.subjectCode})</td>
                        <td className="px-4 py-2 text-slate-blue">{t.facultyName}</td>
                        <td className="px-4 py-2 font-mono">{t.room}</td>
                        <td className="px-4 py-2 text-slate-blue text-[11px]">{t.branch}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 5: EXAMINATION DATESHEETS */}
          {activeTab === 'datesheets' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Examination Datesheets</h3>
                <p className="text-xs text-slate-blue">Official MITS Autonomous CBCS examination schedule.</p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Date</th>
                      <th className="px-4 py-2.5">Time</th>
                      <th className="px-4 py-2.5">Subject & Code</th>
                      <th className="px-4 py-2.5">Exam Type</th>
                      <th className="px-4 py-2.5">Semester</th>
                      <th className="px-4 py-2.5">Branch</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {datesheets.map((e) => (
                      <tr key={e.id} className="hover:bg-paper">
                        <td className="px-4 py-2 font-mono font-semibold">{e.date}</td>
                        <td className="px-4 py-2 font-mono text-[11px]">{e.time}</td>
                        <td className="px-4 py-2 font-medium">{e.subject} ({e.subjectCode})</td>
                        <td className="px-4 py-2 text-slate-blue">{e.examinationType}</td>
                        <td className="px-4 py-2 font-semibold">{e.semester}</td>
                        <td className="px-4 py-2 text-slate-blue text-[11px]">{e.branch}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 6: ACADEMIC CALENDAR */}
          {activeTab === 'calendars' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Official Academic Calendar (2026–2027)</h3>
                <p className="text-xs text-slate-blue">
                  Distinguishing 2nd/3rd year and final-year milestone schedules per institutional regulations.
                </p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Applicable Group</th>
                      <th className="px-4 py-2.5">Timeline</th>
                      <th className="px-4 py-2.5">Academic Event / Milestone</th>
                      <th className="px-4 py-2.5">Remarks</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {calendars.map((c) => (
                      <tr key={c.id} className="hover:bg-paper">
                        <td className="px-4 py-2">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            c.applicableSemester === 'Final Year' ? 'bg-amber-100 text-amber-900' : 'bg-slate-subtle text-slate-blue'
                          }`}>
                            {c.applicableSemester}
                          </span>
                        </td>
                        <td className="px-4 py-2 font-mono text-[11px]">
                          {c.startDate} {c.endDate ? `– ${c.endDate}` : ''}
                        </td>
                        <td className="px-4 py-2 font-medium">{c.activity}</td>
                        <td className="px-4 py-2 text-slate-blue text-[11px]">{c.remarks}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 8: RESULTS & MARKS (RESTRICTED) */}
          {activeTab === 'results' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">
                  Restricted Student Results & Marks Repository
                </h3>
                <p className="text-xs text-slate-blue">
                  High-sensitivity records. Every access is audited. Super Admin CSV/XLSX imports with automated validation.
                </p>
              </div>

              {/* Import Box */}
              <div className="p-4 rounded-xl bg-paper border border-stone-warm space-y-3">
                <h4 className="font-semibold text-xs text-ink-navy">Import Examination Results Dataset</h4>
                {resultsMsg && (
                  <p className={`text-xs ${resultsMsg.type === 'success' ? 'text-sage font-medium' : 'text-rose-700'}`}>
                    {resultsMsg.text}
                  </p>
                )}
                <form onSubmit={handleResultsImport} className="flex flex-wrap items-center gap-3">
                  <input
                    type="file"
                    accept=".csv,.xlsx"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) setResultsFile(e.target.files[0]);
                    }}
                    className="text-xs"
                  />
                  <input
                    type="text"
                    value={resultsSession}
                    onChange={(e) => setResultsSession(e.target.value)}
                    placeholder="Session (e.g. June 2026)"
                    className="px-3 py-1.5 text-xs rounded-lg border border-stone-warm bg-white focus:outline-none"
                  />
                  <button
                    type="submit"
                    disabled={!resultsFile || resultsImporting}
                    className="px-4 py-1.5 rounded-lg bg-ink-navy text-white text-xs font-semibold hover:bg-ink-light disabled:opacity-50"
                  >
                    {resultsImporting ? 'Validating...' : 'Validate & Import'}
                  </button>
                </form>
              </div>

              {/* Results Table */}
              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Roll Number</th>
                      <th className="px-4 py-2.5">Student Name</th>
                      <th className="px-4 py-2.5">Branch</th>
                      <th className="px-4 py-2.5">Semester</th>
                      <th className="px-4 py-2.5">SGPA / CGPA</th>
                      <th className="px-4 py-2.5">Subjects Recorded</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {resultsList.map((r) => (
                      <tr key={r.id} className="hover:bg-paper">
                        <td className="px-4 py-2 font-mono font-semibold">{r.rollNumber}</td>
                        <td className="px-4 py-2 font-medium">{r.studentName}</td>
                        <td className="px-4 py-2 text-slate-blue">{r.branch}</td>
                        <td className="px-4 py-2">{r.semester}</td>
                        <td className="px-4 py-2 font-mono font-semibold text-terracotta">
                          {r.sgpa} / {r.cgpa}
                        </td>
                        <td className="px-4 py-2 text-slate-blue">
                          {r.subjects.map((s: any) => `${s.subjectCode} (${s.grade})`).join(', ')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 9: STUDENT RECORDS */}
          {activeTab === 'students' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Centre for AI Enrolled Students</h3>
                <p className="text-xs text-slate-blue">Synthetic student records strictly tagged with is_demo = true.</p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Roll Number</th>
                      <th className="px-4 py-2.5">Name</th>
                      <th className="px-4 py-2.5">Branch</th>
                      <th className="px-4 py-2.5">Year</th>
                      <th className="px-4 py-2.5">Top Skills</th>
                      <th className="px-4 py-2.5">Hackathons</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {studentsList.map((s) => (
                      <tr key={s.studentId} className="hover:bg-paper">
                        <td className="px-4 py-2 font-mono font-semibold">{s.rollNumber}</td>
                        <td className="px-4 py-2 font-medium">{s.name}</td>
                        <td className="px-4 py-2 text-slate-blue">{s.branch}</td>
                        <td className="px-4 py-2">{s.year} Year</td>
                        <td className="px-4 py-2 text-slate-blue">{s.topSkills?.join(', ')}</td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            s.openForHackathons ? 'bg-sage-bg text-sage' : 'bg-stone-warm text-slate-blue'
                          }`}>
                            {s.openForHackathons ? 'Open' : 'Unavailable'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 10: FACULTY DIRECTORY */}
          {activeTab === 'faculty' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Official MITS Faculty Directory</h3>
                <p className="text-xs text-slate-blue">Verified Centre for Artificial Intelligence faculty from web.mitsgwalior.in.</p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Faculty Name</th>
                      <th className="px-4 py-2.5">Designation</th>
                      <th className="px-4 py-2.5">Department</th>
                      <th className="px-4 py-2.5">Research Areas</th>
                      <th className="px-4 py-2.5">Mentor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {facultyList.map((f) => (
                      <tr key={f.facultyId} className="hover:bg-paper">
                        <td className="px-4 py-2 font-semibold text-ink-navy">{f.name}</td>
                        <td className="px-4 py-2 text-slate-blue">{f.designation}</td>
                        <td className="px-4 py-2">{f.department}</td>
                        <td className="px-4 py-2 text-slate-blue text-[11px]">{f.researchAreas?.join(', ')}</td>
                        <td className="px-4 py-2">
                          {f.isMentor && (
                            <span className="px-2 py-0.5 rounded-full bg-terracotta-light text-terracotta text-[10px] font-bold">
                              Mentor
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 12: APPLICATION TEMPLATES */}
          {activeTab === 'templates' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Conventional Academic Templates</h3>
                <p className="text-xs text-slate-blue">Conventional Indian academic application formats with placeholders.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((tpl) => (
                  <div key={tpl.id} className="p-4 rounded-xl border border-stone-warm bg-paper space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-xs text-ink-navy">{tpl.title}</h4>
                      <span className="px-2 py-0.5 rounded-full bg-stone-warm text-[10px] font-mono uppercase">{tpl.type}</span>
                    </div>
                    <p className="text-[10px] text-terracotta font-medium">{tpl.notice}</p>
                    <pre className="text-[10px] font-mono p-2.5 rounded-lg bg-white border border-stone-warm max-h-40 overflow-y-auto whitespace-pre-wrap text-slate-blue">
                      {tpl.template}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION 14: AUDIT LOGS */}
          {activeTab === 'audit' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Immutable Audit Logs</h3>
                <p className="text-xs text-slate-blue">Tamper-evident record of privileged actions, uploads, and data access.</p>
              </div>

              <div className="rounded-xl border border-stone-warm overflow-hidden shadow-subtle">
                <table className="w-full text-left text-xs">
                  <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                    <tr>
                      <th className="px-4 py-2.5">Time</th>
                      <th className="px-4 py-2.5">Actor</th>
                      <th className="px-4 py-2.5">Role</th>
                      <th className="px-4 py-2.5">Action</th>
                      <th className="px-4 py-2.5">Entity</th>
                      <th className="px-4 py-2.5">Change Summary</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-warm text-ink-navy">
                    {auditLogs.map((l) => (
                      <tr key={l.id} className="hover:bg-paper">
                        <td className="px-4 py-2 font-mono text-[11px] text-slate-blue">
                          {new Date(l.createdAt).toLocaleString()}
                        </td>
                        <td className="px-4 py-2 font-medium">{l.actorEmail}</td>
                        <td className="px-4 py-2 font-mono text-[10px]">{l.actorRole}</td>
                        <td className="px-4 py-2">
                          <span className="px-2 py-0.5 rounded-full bg-stone-warm text-[10px] font-mono font-semibold">
                            {l.action}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-slate-blue">{l.targetEntity}</td>
                        <td className="px-4 py-2 text-slate-blue">{l.changeSummary}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SECTION 15: SETTINGS */}
          {activeTab === 'settings' && (
            <div className="space-y-4 max-w-xl">
              <div>
                <h3 className="font-heading font-bold text-base text-ink-navy">Administrative Configuration</h3>
                <p className="text-xs text-slate-blue">Platform boundaries, database settings, and storage parameters.</p>
              </div>

              <div className="p-4 rounded-xl border border-stone-warm bg-paper space-y-3 text-xs">
                <div>
                  <p className="font-semibold text-ink-navy">Super Admin Allowlist</p>
                  <p className="text-slate-blue font-mono text-[11px]">utsavkumawat05@gmail.com, guptamahi0207@gmail.com</p>
                </div>
                <div>
                  <p className="font-semibold text-ink-navy">Student Domain Allowance</p>
                  <p className="text-slate-blue font-mono text-[11px]">@mitsgwl.ac.in, example.invalid</p>
                </div>
                <div>
                  <p className="font-semibold text-ink-navy">Faculty Domain Allowance</p>
                  <p className="text-slate-blue font-mono text-[11px]">@mitsgwalior.in, example.invalid</p>
                </div>
                <div>
                  <p className="font-semibold text-ink-navy">Local Filesystem Storage Root</p>
                  <p className="text-slate-blue font-mono text-[11px]">PocketUni/storage/</p>
                </div>
                <div>
                  <p className="font-semibold text-ink-navy">Authoritative Database Engine</p>
                  <p className="text-slate-blue font-mono text-[11px]">PostgreSQL 18 (Localhost:5432 / pocketuni)</p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 16: ROSTER & EXCEL SYNC */}
          {activeTab === 'roster' && (
            <div className="space-y-6 max-w-5xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="font-heading font-bold text-base text-ink-navy">
                    Institutional Roster Management & Excel Synchronization
                  </h3>
                  <p className="text-xs text-slate-blue">
                    Import, validate, and manage official student and faculty rosters. Master data is stored in PostgreSQL and mirrored to local Excel workbooks.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDownloadWorkbook('students')}
                    disabled={downloadingExport}
                    className="px-3 py-1.5 rounded-xl border border-stone-warm text-slate-blue hover:text-ink-navy hover:bg-paper text-xs font-semibold flex items-center gap-1.5 transition-all"
                  >
                    <Download className="w-3.5 h-3.5 text-sage" />
                    <span>Download Students (.xlsx)</span>
                  </button>
                  <button
                    onClick={() => handleDownloadWorkbook('faculty')}
                    disabled={downloadingExport}
                    className="px-3 py-1.5 rounded-xl border border-stone-warm text-slate-blue hover:text-ink-navy hover:bg-paper text-xs font-semibold flex items-center gap-1.5 transition-all"
                  >
                    <Download className="w-3.5 h-3.5 text-terracotta" />
                    <span>Download Faculty (.xlsx)</span>
                  </button>
                </div>
              </div>

              {rosterMessage && (
                <div
                  className={`p-3.5 rounded-xl text-xs flex items-center gap-2 ${
                    rosterMessage.type === 'success'
                      ? 'bg-sage/10 text-sage border border-sage/20'
                      : 'bg-terracotta/10 text-terracotta border border-terracotta/20'
                  }`}
                >
                  {rosterMessage.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                  )}
                  <span>{rosterMessage.text}</span>
                </div>
              )}

              {/* Roster Upload & Preview Form */}
              <div className="p-5 rounded-2xl bg-paper border border-stone-warm space-y-4">
                <h4 className="font-heading font-semibold text-sm text-ink-navy flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-terracotta" />
                  <span>Upload & Validate Workbook</span>
                </h4>

                <form onSubmit={handleRosterPreview} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-blue uppercase mb-1">
                        Roster Entity Type
                      </label>
                      <select
                        value={rosterEntityType}
                        onChange={(e) => {
                          setRosterEntityType(e.target.value as any);
                          setRosterPreview(null);
                        }}
                        className="w-full px-3 py-2 rounded-xl border border-stone-warm bg-white text-xs font-medium focus:outline-none focus:border-ink-navy"
                      >
                        <option value="students">Student Roster (pocketuni_students.xlsx)</option>
                        <option value="faculty">Faculty Directory (pocketuni_faculty.xlsx)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-blue uppercase mb-1">
                        Select Excel File (.xlsx)
                      </label>
                      <input
                        type="file"
                        accept=".xlsx"
                        onChange={(e) => {
                          setRosterFile(e.target.files?.[0] || null);
                          setRosterPreview(null);
                        }}
                        className="w-full text-xs text-slate-blue file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-ink-navy file:text-white hover:file:bg-ink-navy/90"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      type="submit"
                      disabled={!rosterFile || rosterPreviewing}
                      className="px-4 py-2 rounded-xl bg-ink-navy text-white text-xs font-semibold flex items-center gap-2 hover:bg-ink-navy/90 transition-all disabled:opacity-50"
                    >
                      <Eye className={`w-3.5 h-3.5 ${rosterPreviewing ? 'animate-spin' : ''}`} />
                      <span>{rosterPreviewing ? 'Validating...' : 'Validate & Preview Roster'}</span>
                    </button>
                    {rosterFile && (
                      <span className="text-xs text-slate-blue">
                        Selected: <span className="font-mono font-medium text-ink-navy">{rosterFile.name}</span>
                      </span>
                    )}
                  </div>
                </form>

                {/* Preview Table & Validation Results */}
                {rosterPreview && (
                  <div className="mt-4 pt-4 border-t border-stone-warm space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 text-xs">
                        <span className="font-semibold text-ink-navy">
                          Total Rows: <span className="font-mono">{rosterPreview.total_rows}</span>
                        </span>
                        <span className="text-sage font-semibold">
                          Valid: <span className="font-mono">{rosterPreview.valid_rows}</span>
                        </span>
                        {rosterPreview.invalid_rows > 0 && (
                          <span className="text-terracotta font-semibold">
                            Invalid: <span className="font-mono">{rosterPreview.invalid_rows}</span>
                          </span>
                        )}
                        {rosterPreview.duplicates_count > 0 && (
                          <span className="text-amber-600 font-semibold">
                            Duplicates: <span className="font-mono">{rosterPreview.duplicates_count}</span>
                          </span>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={handleRosterImport}
                        disabled={rosterImporting || rosterPreview.valid_rows === 0}
                        className="px-4 py-2 rounded-xl bg-sage text-white text-xs font-semibold flex items-center gap-2 hover:bg-sage/90 transition-all shadow-subtle disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>{rosterImporting ? 'Importing...' : 'Commit to Database'}</span>
                      </button>
                    </div>

                    {rosterPreview.errors?.length > 0 && (
                      <div className="p-3 rounded-xl bg-terracotta/5 border border-terracotta/20 text-xs text-terracotta space-y-1 max-h-32 overflow-y-auto">
                        <p className="font-bold">Validation Issues:</p>
                        {rosterPreview.errors.map((err: any, idx: number) => (
                          <p key={idx} className="font-mono text-[11px]">
                            Row {err.row}: {err.error}
                          </p>
                        ))}
                      </div>
                    )}

                    {rosterPreview.preview?.length > 0 && (
                      <div className="border border-stone-warm rounded-xl overflow-hidden max-h-60 overflow-y-auto bg-white">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm sticky top-0">
                            <tr>
                              <th className="px-3 py-2">Identifier</th>
                              <th className="px-3 py-2">Full Name</th>
                              <th className="px-3 py-2">Email</th>
                              <th className="px-3 py-2">Department</th>
                              <th className="px-3 py-2">Role/Prog</th>
                              <th className="px-3 py-2">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-stone-warm">
                            {rosterPreview.preview.map((row: any, i: number) => (
                              <tr key={i} className="hover:bg-paper">
                                <td className="px-3 py-1.5 font-mono text-[11px] font-semibold text-ink-navy">
                                  {row.roll_number || row.faculty_identifier || '—'}
                                </td>
                                <td className="px-3 py-1.5">{row.full_name || row.name || '—'}</td>
                                <td className="px-3 py-1.5 font-mono text-[11px] text-slate-blue">
                                  {row.institutional_email || row.official_email || '—'}
                                </td>
                                <td className="px-3 py-1.5 text-slate-blue">{row.department || '—'}</td>
                                <td className="px-3 py-1.5 text-slate-blue">
                                  {row.programme || row.designation || '—'}
                                </td>
                                <td className="px-3 py-1.5">
                                  <span
                                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                      row.valid !== false
                                        ? 'bg-sage/15 text-sage'
                                        : 'bg-terracotta/15 text-terracotta'
                                    }`}
                                  >
                                    {row.valid !== false ? 'Valid' : 'Error'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Recent Import Batches */}
              <div className="p-5 rounded-2xl bg-paper border border-stone-warm space-y-4">
                <h4 className="font-heading font-semibold text-sm text-ink-navy flex items-center gap-2">
                  <Database className="w-4 h-4 text-slate-blue" />
                  <span>Recent Roster Import Batches</span>
                </h4>

                {rosterSyncStatus?.recent_batches?.length > 0 ? (
                  <div className="border border-stone-warm rounded-xl overflow-hidden bg-white">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                        <tr>
                          <th className="px-3 py-2">Batch ID</th>
                          <th className="px-3 py-2">Entity</th>
                          <th className="px-3 py-2">Filename</th>
                          <th className="px-3 py-2">Imported</th>
                          <th className="px-3 py-2">Created</th>
                          <th className="px-3 py-2">Updated</th>
                          <th className="px-3 py-2">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-stone-warm">
                        {rosterSyncStatus.recent_batches.map((b: any) => (
                          <tr key={b.id} className="hover:bg-paper">
                            <td className="px-3 py-1.5 font-mono text-[11px] text-slate-blue truncate max-w-[120px]">
                              {b.id}
                            </td>
                            <td className="px-3 py-1.5 uppercase font-bold text-[10px]">{b.entity_type}</td>
                            <td className="px-3 py-1.5 text-slate-blue font-mono text-[11px]">{b.file_name}</td>
                            <td className="px-3 py-1.5 font-semibold text-sage">{b.total_rows_imported}</td>
                            <td className="px-3 py-1.5 font-semibold text-ink-navy">{b.created_users_count}</td>
                            <td className="px-3 py-1.5 font-semibold text-slate-blue">{b.updated_users_count}</td>
                            <td className="px-3 py-1.5 font-mono text-[10px] text-slate-blue">
                              {new Date(b.created_at).toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-slate-blue italic">No roster import batches recorded yet.</p>
                )}
              </div>
            </div>
          )}

          {/* SECTION 17: WEB CRAWLER & PORTALS */}
          {activeTab === 'website' && (
            <div className="space-y-6 max-w-5xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="font-heading font-bold text-base text-ink-navy">
                    MITS Web Ecosystem Crawler & Institutional Portals
                  </h3>
                  <p className="text-xs text-slate-blue">
                    Automated polite ingestion of official MITS web domains (web.mitsgwalior.in, ams.mitsgwalior.in) into RAG vector repository.
                  </p>
                </div>
              </div>

              {crawlMessage && (
                <div
                  className={`p-3.5 rounded-xl text-xs flex items-center gap-2 ${
                    crawlMessage.type === 'success'
                      ? 'bg-sage/10 text-sage border border-sage/20'
                      : 'bg-terracotta/10 text-terracotta border border-terracotta/20'
                  }`}
                >
                  {crawlMessage.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                  )}
                  <span>{crawlMessage.text}</span>
                </div>
              )}

              {/* Crawler Telemetry Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Official Sources</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {websiteStats?.total_sources ?? websiteSources.length}
                  </p>
                  <span className="text-[10px] text-sage font-medium">web.mitsgwalior.in</span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Crawled Pages</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {websiteStats?.total_pages_crawled ?? '—'}
                  </p>
                  <span className="text-[10px] text-slate-blue font-medium">HTML pages</span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Web Docs Extracted</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {websiteStats?.extracted_documents ?? '—'}
                  </p>
                  <span className="text-[10px] text-terracotta font-medium">Clean text & tables</span>
                </div>

                <div className="p-4 rounded-2xl bg-paper border border-stone-warm">
                  <p className="text-[11px] font-semibold text-slate-blue uppercase">Web RAG Chunks</p>
                  <p className="font-heading font-extrabold text-2xl text-ink-navy mt-1">
                    {websiteStats?.embedded_chunks ?? '—'}
                  </p>
                  <span className="text-[10px] text-sage font-medium">gemini-embedding-001</span>
                </div>
              </div>

              {/* Ingestion Trigger Control */}
              <div className="p-5 rounded-2xl bg-paper border border-stone-warm space-y-4">
                <h4 className="font-heading font-semibold text-sm text-ink-navy flex items-center gap-2">
                  <Globe className="w-4 h-4 text-terracotta" />
                  <span>Execute Web Ingestion Pipeline</span>
                </h4>
                <p className="text-xs text-slate-blue">
                  Politely crawls official institutional endpoints, removes boilerplate, hashes content for deduplication, and generates vector embeddings.
                </p>

                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                  <div className="flex items-center gap-2">
                    <label className="text-xs font-semibold text-slate-blue">Max Pages to Crawl:</label>
                    <input
                      type="number"
                      min={1}
                      max={30}
                      value={crawlMaxPages}
                      onChange={(e) => setCrawlMaxPages(Math.max(1, parseInt(e.target.value) || 1))}
                      className="w-20 px-3 py-1.5 rounded-xl border border-stone-warm bg-white text-xs font-mono font-semibold"
                    />
                  </div>

                  <button
                    onClick={handleTriggerCrawl}
                    disabled={crawling}
                    className="px-4 py-2 rounded-xl bg-ink-navy text-white text-xs font-semibold flex items-center gap-2 hover:bg-ink-navy/90 transition-all shadow-subtle disabled:opacity-50"
                  >
                    <Play className={`w-3.5 h-3.5 ${crawling ? 'animate-spin' : ''}`} />
                    <span>{crawling ? 'Crawling MITS Web Ecosystem...' : 'Start Web Ingestion'}</span>
                  </button>
                </div>

                <div className="p-3 rounded-xl bg-white border border-stone-warm text-[11px] text-slate-blue">
                  <span className="font-semibold text-ink-navy">Security Sandbox:</span> Polite crawl rate of 0.5s per page. SSRF firewall permits only <code className="font-mono text-ink-navy">web.mitsgwalior.in</code> and <code className="font-mono text-ink-navy">ams.mitsgwalior.in</code>. Loopback addresses and external domains are strictly blocked.
                </div>
              </div>

              {/* Official Sources Table */}
              <div className="p-5 rounded-2xl bg-paper border border-stone-warm space-y-4">
                <h4 className="font-heading font-semibold text-sm text-ink-navy flex items-center gap-2">
                  <ExternalLink className="w-4 h-4 text-sage" />
                  <span>Configured Institutional Sources</span>
                </h4>

                {websiteSources.length > 0 ? (
                  <div className="border border-stone-warm rounded-xl overflow-hidden bg-white">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                        <tr>
                          <th className="px-3 py-2">Source Name</th>
                          <th className="px-3 py-2">Base URL</th>
                          <th className="px-3 py-2">Category</th>
                          <th className="px-3 py-2">Status</th>
                          <th className="px-3 py-2">Pages</th>
                          <th className="px-3 py-2">Last Crawled</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-stone-warm">
                        {websiteSources.map((s: any) => (
                          <tr key={s.id} className="hover:bg-paper">
                            <td className="px-3 py-1.5 font-semibold text-ink-navy">{s.name}</td>
                            <td className="px-3 py-1.5 font-mono text-[11px] text-slate-blue truncate max-w-xs">
                              <a
                                href={s.base_url}
                                target="_blank"
                                rel="noreferrer"
                                className="hover:underline flex items-center gap-1 text-ink-navy"
                              >
                                {s.base_url}
                                <ArrowUpRight className="w-3 h-3 text-slate-blue" />
                              </a>
                            </td>
                            <td className="px-3 py-1.5 text-slate-blue capitalize">{s.source_type}</td>
                            <td className="px-3 py-1.5">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                  s.is_active ? 'bg-sage/15 text-sage' : 'bg-stone-warm text-slate-blue'
                                }`}
                              >
                                {s.is_active ? 'Active' : 'Disabled'}
                              </span>
                            </td>
                            <td className="px-3 py-1.5 font-mono text-slate-blue">{s.total_pages_crawled ?? 0}</td>
                            <td className="px-3 py-1.5 font-mono text-[10px] text-slate-blue">
                              {s.last_crawled_at ? new Date(s.last_crawled_at).toLocaleDateString() : 'Never'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-slate-blue italic">No website sources registered yet.</p>
                )}
              </div>

              {/* Official E-Governance Portals Catalogue */}
              <div className="p-5 rounded-2xl bg-paper border border-stone-warm space-y-4">
                <h4 className="font-heading font-semibold text-sm text-ink-navy flex items-center gap-2">
                  <Building className="w-4 h-4 text-terracotta" />
                  <span>MITS E-Governance Portals Directory</span>
                </h4>

                {websitePortals.length > 0 ? (
                  <div className="border border-stone-warm rounded-xl overflow-hidden bg-white">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm">
                        <tr>
                          <th className="px-3 py-2">Portal Name</th>
                          <th className="px-3 py-2">Code</th>
                          <th className="px-3 py-2">URL</th>
                          <th className="px-3 py-2">Category</th>
                          <th className="px-3 py-2">Auth</th>
                          <th className="px-3 py-2">Target Audience</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-stone-warm">
                        {websitePortals.map((p: any) => (
                          <tr key={p.id} className="hover:bg-paper">
                            <td className="px-3 py-1.5 font-semibold text-ink-navy">{p.name}</td>
                            <td className="px-3 py-1.5 font-mono text-[11px] font-bold text-terracotta">
                              {p.portal_code}
                            </td>
                            <td className="px-3 py-1.5 font-mono text-[11px] text-slate-blue truncate max-w-xs">
                              <a
                                href={p.url}
                                target="_blank"
                                rel="noreferrer"
                                className="hover:underline flex items-center gap-1 text-ink-navy"
                              >
                                {p.url}
                                <ArrowUpRight className="w-3 h-3 text-slate-blue" />
                              </a>
                            </td>
                            <td className="px-3 py-1.5 text-slate-blue capitalize">{p.category}</td>
                            <td className="px-3 py-1.5">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                  p.requires_auth ? 'bg-amber-100 text-amber-800' : 'bg-sage/15 text-sage'
                                }`}
                              >
                                {p.requires_auth ? 'Login Required' : 'Public'}
                              </span>
                            </td>
                            <td className="px-3 py-1.5 text-slate-blue font-mono text-[10px]">{p.target_audience}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-slate-blue italic">No institutional portals catalogue recorded yet.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {reviewDocId && (
        <DocumentReviewModal
          documentId={reviewDocId}
          onClose={() => setReviewDocId(null)}
          onRefresh={() => {
            loadOverviewData();
            loadTabSpecificData(activeTab);
          }}
        />
      )}
    </div>
  );
};
