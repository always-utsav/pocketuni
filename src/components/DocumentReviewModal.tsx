import React, { useState } from 'react';
import {
  X,
  FileText,
  Table as TableIcon,
  CheckCircle2,
  AlertTriangle,
  Download,
  Building,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  Archive,
  RefreshCw,
  Users,
  Lock
} from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface DocumentReviewModalProps {
  documentId: string;
  onClose: () => void;
  onRefresh: () => void;
}

const CATEGORIES = [
  'TIMETABLE',
  'SCHEME_OF_STUDY',
  'SYLLABUS',
  'INDUCTION_NOTICE',
  'GENERAL_NOTICE',
  'EXAMINATION_DATESHEET',
  'INTERNAL_MARKS',
  'FINAL_RESULTS',
  'ACADEMIC_CALENDAR',
  'PROFESSIONAL_CERTIFICATION_LIST',
  'COURSE_STRUCTURE',
  'LAB_MANUAL',
  'ACADEMIC_POLICY',
  'FACULTY_DOCUMENT',
  'GENERAL_INSTITUTIONAL_DOCUMENT',
  'OTHER'
];

export const DocumentReviewModal: React.FC<DocumentReviewModalProps> = ({
  documentId,
  onClose,
  onRefresh
}) => {
  const [doc, setDoc] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'extracted_text' | 'tables' | 'metadata' | 'audience' | 'reconciliation'>('extracted_text');
  const [isPublishing, setIsPublishing] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form states for metadata correction
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('OTHER');
  const [academicYear, setAcademicYear] = useState('');
  const [semester, setSemester] = useState('');
  const [branch, setBranch] = useState('');
  const [programme, setProgramme] = useState('');
  const [batch, setBatch] = useState('');
  const [issuingAuthority, setIssuingAuthority] = useState('');
  const [audiences, setAudiences] = useState<{ scopeType: string; scopeValue?: string }[]>([]);

  // Marks reconciliation state
  const [reconciliation, setReconciliation] = useState<any>(null);
  const [loadingRecon, setLoadingRecon] = useState(false);

  React.useEffect(() => {
    loadDocument();
  }, [documentId]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDocumentReview(documentId);
      setDoc(data);
      setTitle(data.title || '');
      setCategory(data.category || data.suggestedCategory || 'OTHER');
      setAcademicYear(data.academicYear || '2026-2027');
      setSemester(data.semester || '');
      setBranch(data.branch || '');
      setProgramme(data.programme || '');
      setBatch(data.batch || '');
      setIssuingAuthority(data.issuingAuthority || '');
      setAudiences(data.audiences && data.audiences.length > 0 ? data.audiences : [{ scopeType: 'ENTIRE_INSTITUTION' }]);

      if (data.category === 'INTERNAL_MARKS') {
        loadReconciliation();
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load document review data');
    } finally {
      setLoading(false);
    }
  };

  const loadReconciliation = async () => {
    try {
      setLoadingRecon(true);
      const res = await apiClient.getMarksReconciliation(documentId);
      setReconciliation(res);
    } catch (e: any) {
      console.warn('Reconciliation fetch failed:', e);
    } finally {
      setLoadingRecon(false);
    }
  };

  const handleSaveMetadata = async () => {
    try {
      setErrorMsg(null);
      await apiClient.updateDocumentMetadata(documentId, {
        title,
        category,
        academicYear,
        semester,
        branch,
        programme,
        batch,
        issuingAuthority,
        audiences
      });
      setSuccessMsg('Metadata and audience updated successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
      loadDocument();
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handlePublish = async () => {
    if (category === 'INTERNAL_MARKS') {
      alert('Internal marks documents contain confidential student records and cannot be published to general audiences.');
      return;
    }
    try {
      setIsPublishing(true);
      setErrorMsg(null);
      await apiClient.publishDocument(documentId, {
        isAuthoritative: true,
        audiences,
        changeSummary: 'Approved and published authoritative version by Super Admin.'
      });
      setSuccessMsg('Document successfully published as authoritative institutional record.');
      setTimeout(() => {
        onRefresh();
        onClose();
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleArchive = async () => {
    if (!confirm('Are you sure you want to archive this document? It will no longer be visible as active.')) return;
    try {
      await apiClient.archiveDocument(documentId);
      onRefresh();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const toggleAudienceScope = (scope: string) => {
    const exists = audiences.some(a => a.scopeType === scope);
    if (exists) {
      setAudiences(audiences.filter(a => a.scopeType !== scope));
    } else {
      setAudiences([...audiences, { scopeType: scope }]);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 bg-ink-navy/60 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-sm w-full text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-slate-blue animate-spin mx-auto" />
          <p className="text-sm font-medium text-ink-navy">Inspecting extracted institutional document...</p>
        </div>
      </div>
    );
  }

  const isInternalMarks = category === 'INTERNAL_MARKS' || doc?.category === 'INTERNAL_MARKS';

  return (
    <div className="fixed inset-0 z-50 bg-ink-navy/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 overflow-hidden">
      <div className="bg-white rounded-3xl max-w-5xl w-full h-[90vh] flex flex-col shadow-2xl border border-stone-warm overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-stone-warm flex items-start justify-between bg-paper shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-ink-navy text-white uppercase tracking-wider">
                {doc?.category || 'DOCUMENT'}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                doc?.status === 'PUBLISHED' ? 'bg-sage/20 text-sage' : 'bg-terracotta/20 text-terracotta'
              }`}>
                {doc?.status}
              </span>
              {doc?.currentVersionNo > 1 && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-stone-warm text-ink-navy">
                  v{doc.currentVersionNo}
                </span>
              )}
              {isInternalMarks && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 flex items-center gap-1">
                  <Lock className="w-3 h-3" /> Confidential Marks
                </span>
              )}
            </div>
            <h2 className="font-heading font-bold text-lg text-ink-navy mt-1 truncate max-w-2xl">
              {doc?.title}
            </h2>
            <p className="text-xs text-slate-blue flex items-center gap-2 mt-0.5">
              <span>{doc?.fileName}</span>
              <span>•</span>
              <span>{((doc?.fileSizeBytes || 0) / 1024).toFixed(1)} KB</span>
              <span>•</span>
              <span>SHA-256: {doc?.contentHash?.slice(0, 8)}...</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={apiClient.getDocumentDownloadUrl(documentId)}
              target="_blank"
              rel="noreferrer"
              className="p-2 rounded-xl text-slate-blue hover:text-ink-navy hover:bg-stone-warm/50 transition-colors"
              title="Download original file"
            >
              <Download className="w-5 h-5" />
            </a>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-blue hover:text-ink-navy hover:bg-stone-warm/50 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Alerts */}
        {successMsg && (
          <div className="bg-sage/10 text-sage text-xs px-5 py-2.5 border-b border-sage/20 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}
        {errorMsg && (
          <div className="bg-red-50 text-red-700 text-xs px-5 py-2.5 border-b border-red-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 px-5 border-b border-stone-warm bg-white shrink-0 overflow-x-auto">
          <button
            onClick={() => setActiveTab('extracted_text')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'extracted_text'
                ? 'border-terracotta text-terracotta'
                : 'border-transparent text-slate-blue hover:text-ink-navy'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Extracted Text ({doc?.extractedContents?.length || 0} blocks)</span>
          </button>

          <button
            onClick={() => setActiveTab('tables')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'tables'
                ? 'border-terracotta text-terracotta'
                : 'border-transparent text-slate-blue hover:text-ink-navy'
            }`}
          >
            <TableIcon className="w-3.5 h-3.5" />
            <span>Structured Tables ({doc?.extractedTables?.length || 0})</span>
          </button>

          {isInternalMarks && (
            <button
              onClick={() => { setActiveTab('reconciliation'); loadReconciliation(); }}
              className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
                activeTab === 'reconciliation'
                  ? 'border-terracotta text-terracotta'
                  : 'border-transparent text-slate-blue hover:text-ink-navy'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Marks Reconciliation ({reconciliation?.totalRecords || 0})</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab('metadata')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'metadata'
                ? 'border-terracotta text-terracotta'
                : 'border-transparent text-slate-blue hover:text-ink-navy'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Scope & Metadata</span>
          </button>

          <button
            onClick={() => setActiveTab('audience')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'audience'
                ? 'border-terracotta text-terracotta'
                : 'border-transparent text-slate-blue hover:text-ink-navy'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Audience Rules ({audiences.length})</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-paper">
          {/* TAB 1: EXTRACTED TEXT */}
          {activeTab === 'extracted_text' && (
            <div className="space-y-4 max-w-4xl mx-auto">
              {doc?.latestJob?.warnings && doc.latestJob.warnings.length > 0 && (
                <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-1">
                  <div className="flex items-center gap-2 font-semibold">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Extraction Engine Warnings</span>
                  </div>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                    {doc.latestJob.warnings.map((w: string, i: number) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-white rounded-2xl p-5 border border-stone-warm shadow-subtle space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-blue border-b border-stone-warm pb-2">
                  <span>Engine: {doc?.latestJob?.extractorEngine || 'Native Parser'}</span>
                  <span>Execution Time: {doc?.latestJob?.executionTimeMs || 0} ms</span>
                </div>

                <div className="space-y-2 text-xs text-ink-navy leading-relaxed max-h-[500px] overflow-y-auto pr-2">
                  {doc?.extractedContents && doc.extractedContents.length > 0 ? (
                    doc.extractedContents.map((block: any) => (
                      <div
                        key={block.id}
                        className={`p-2 rounded-lg ${
                          block.heading
                            ? 'bg-paper font-bold text-ink-navy text-sm border-l-4 border-terracotta'
                            : 'hover:bg-paper/60'
                        }`}
                      >
                        {block.content}
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-blue italic text-center py-8">
                      No text blocks extracted. The document may be image-only. Check the OCR status.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: TABLES */}
          {activeTab === 'tables' && (
            <div className="space-y-6 max-w-5xl mx-auto">
              {doc?.extractedTables && doc.extractedTables.length > 0 ? (
                doc.extractedTables.map((tbl: any, tIdx: number) => (
                  <div key={tbl.id || tIdx} className="bg-white rounded-2xl p-4 border border-stone-warm shadow-subtle space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-heading font-bold text-ink-navy flex items-center gap-2">
                        <TableIcon className="w-4 h-4 text-terracotta" />
                        Table {tIdx + 1} {tbl.sheetName ? `(${tbl.sheetName})` : ''} — Page {tbl.pageNumber || 1}
                      </span>
                      <span className="text-[11px] text-slate-blue font-medium">{tbl.rowCount} rows</span>
                    </div>

                    <div className="overflow-x-auto max-h-80 border border-stone-warm rounded-xl">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead className="bg-paper text-slate-blue font-semibold sticky top-0 border-b border-stone-warm">
                          <tr>
                            {tbl.headers?.map((h: string, hIdx: number) => (
                              <th key={hIdx} className="px-3 py-2 border-r border-stone-warm text-[11px] truncate max-w-xs">
                                {h}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-stone-warm text-ink-navy">
                          {tbl.rows?.map((row: any[], rIdx: number) => (
                            <tr key={rIdx} className="hover:bg-paper/50">
                              {row.map((cell: any, cIdx: number) => (
                                <td key={cIdx} className="px-3 py-1.5 border-r border-stone-warm text-[11px] truncate max-w-xs">
                                  {cell !== null && cell !== undefined ? String(cell) : ''}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-white rounded-2xl p-12 text-center text-slate-blue border border-stone-warm">
                  <TableIcon className="w-8 h-8 text-stone-warm mx-auto mb-2" />
                  <p className="text-xs font-medium">No structured tables detected in this document.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CONFIDENTIAL MARKS RECONCILIATION */}
          {activeTab === 'reconciliation' && (
            <div className="space-y-4 max-w-5xl mx-auto">
              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-amber-950">
                  <Lock className="w-4 h-4" />
                  <span>Confidential Student Records Isolation Notice</span>
                </div>
                <p>
                  These marks are extracted from official minor evaluation records. They are strictly isolated to the Super Admin review workflow and are <strong>NEVER</strong> exposed to peer students, public search, or RAG assistants.
                </p>
              </div>

              {/* Stats Strip */}
              <div className="grid grid-cols-4 gap-3">
                <div className="bg-white p-3 rounded-xl border border-stone-warm text-center">
                  <p className="text-[10px] text-slate-blue uppercase font-bold">Total Extracted</p>
                  <p className="text-xl font-extrabold text-ink-navy mt-0.5">{reconciliation?.totalRecords ?? '—'}</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-stone-warm text-center">
                  <p className="text-[10px] text-sage uppercase font-bold">Matched in DB</p>
                  <p className="text-xl font-extrabold text-sage mt-0.5">{reconciliation?.matchedCount ?? '—'}</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-stone-warm text-center">
                  <p className="text-[10px] text-slate-blue uppercase font-bold">Unregistered</p>
                  <p className="text-xl font-extrabold text-slate-blue mt-0.5">{reconciliation?.unmatchedCount ?? '—'}</p>
                </div>
                <div className="bg-white p-3 rounded-xl border border-stone-warm text-center">
                  <p className="text-[10px] text-amber-600 uppercase font-bold">Duplicates</p>
                  <p className="text-xl font-extrabold text-amber-600 mt-0.5">{reconciliation?.duplicateCount ?? 0}</p>
                </div>
              </div>

              {/* Records Preview Table */}
              <div className="bg-white rounded-2xl border border-stone-warm overflow-hidden shadow-subtle">
                <div className="p-3 border-b border-stone-warm bg-paper flex items-center justify-between text-xs font-semibold text-ink-navy">
                  <span>Student Enrollment Reconciliation Preview</span>
                  {loadingRecon && <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-blue" />}
                </div>

                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-paper text-slate-blue font-semibold text-[11px] border-b border-stone-warm sticky top-0">
                      <tr>
                        <th className="px-3 py-2">Enrollment No.</th>
                        <th className="px-3 py-2">Document Student Name</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Matched User in System</th>
                        <th className="px-3 py-2">Page</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-warm">
                      {reconciliation?.records?.slice(0, 50).map((r: any, idx: number) => (
                        <tr key={idx} className="hover:bg-paper/50">
                          <td className="px-3 py-2 font-mono text-[11px] font-semibold text-ink-navy">{r.enrollmentNumber}</td>
                          <td className="px-3 py-2 text-ink-navy">{r.studentName}</td>
                          <td className="px-3 py-2">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              r.matchStatus === 'MATCHED' ? 'bg-sage/20 text-sage' : 'bg-slate-100 text-slate-600'
                            }`}>
                              {r.matchStatus}
                            </span>
                          </td>
                          <td className="px-3 py-2 text-slate-blue text-[11px]">
                            {r.matchedUserName ? `${r.matchedUserName} (${r.matchedUserId?.slice(0, 8)})` : '—'}
                          </td>
                          <td className="px-3 py-2 text-slate-blue text-[11px]">P.{r.pageNumber}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: METADATA & SCOPE */}
          {activeTab === 'metadata' && (
            <div className="bg-white rounded-2xl p-6 border border-stone-warm shadow-subtle max-w-3xl mx-auto space-y-4">
              <h3 className="font-heading font-bold text-sm text-ink-navy">Curate Document Classification & Scope</h3>
              <p className="text-xs text-slate-blue">Verify or override the heuristic tags extracted from the document.</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="sm:col-span-2">
                  <label className="block text-slate-blue font-semibold mb-1">Document Title</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta bg-white"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Academic Year</label>
                  <input
                    type="text"
                    value={academicYear}
                    onChange={(e) => setAcademicYear(e.target.value)}
                    placeholder="e.g. 2026-2027"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Batch</label>
                  <input
                    type="text"
                    value={batch}
                    onChange={(e) => setBatch(e.target.value)}
                    placeholder="e.g. 2025-26, 2024-25"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Programme</label>
                  <input
                    type="text"
                    value={programme}
                    onChange={(e) => setProgramme(e.target.value)}
                    placeholder="e.g. B.Tech"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Semester</label>
                  <input
                    type="text"
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    placeholder="e.g. III Semester"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div>
                  <label className="block text-slate-blue font-semibold mb-1">Branch</label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    placeholder="e.g. Artificial Intelligence"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-slate-blue font-semibold mb-1">Issuing Authority / Department</label>
                  <input
                    type="text"
                    value={issuingAuthority}
                    onChange={(e) => setIssuingAuthority(e.target.value)}
                    placeholder="e.g. Centre for Artificial Intelligence"
                    className="w-full px-3 py-2 rounded-xl border border-stone-warm text-ink-navy focus:outline-none focus:border-terracotta"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-stone-warm flex justify-end">
                <button
                  onClick={handleSaveMetadata}
                  className="px-4 py-2 rounded-xl bg-ink-navy text-white text-xs font-semibold hover:bg-slate-blue transition-colors"
                >
                  Save Metadata & Scope
                </button>
              </div>
            </div>
          )}

          {/* TAB 5: AUDIENCE RULES */}
          {activeTab === 'audience' && (
            <div className="bg-white rounded-2xl p-6 border border-stone-warm shadow-subtle max-w-3xl mx-auto space-y-4 text-xs">
              <h3 className="font-heading font-bold text-sm text-ink-navy">Target Audience Governance</h3>
              <p className="text-slate-blue">
                Select which campus groups are authorized to view this document when published.
              </p>

              <div className="space-y-2">
                {[
                  { id: 'ENTIRE_INSTITUTION', label: 'Entire Institution (All Students & Faculty)' },
                  { id: 'CENTRE_FOR_AI', label: 'Centre for Artificial Intelligence Only' },
                  { id: 'STUDENTS_ONLY', label: 'Students Only' },
                  { id: 'FACULTY_ONLY', label: 'Faculty Only' },
                  { id: 'SPECIFIC_ROLES', label: 'Super Admin Only (Restricted / Internal)' }
                ].map((aud) => {
                  const isChecked = audiences.some(a => a.scopeType === aud.id);
                  return (
                    <label
                      key={aud.id}
                      className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                        isChecked ? 'bg-stone-warm/30 border-terracotta text-ink-navy font-semibold' : 'border-stone-warm text-slate-blue hover:bg-paper'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleAudienceScope(aud.id)}
                        className="rounded border-stone-warm text-terracotta focus:ring-terracotta"
                      />
                      <span>{aud.label}</span>
                    </label>
                  );
                })}
              </div>

              <div className="pt-3 border-t border-stone-warm flex justify-end">
                <button
                  onClick={handleSaveMetadata}
                  className="px-4 py-2 rounded-xl bg-ink-navy text-white text-xs font-semibold hover:bg-slate-blue transition-colors"
                >
                  Save Audience Rules
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-stone-warm bg-paper flex items-center justify-between shrink-0">
          <button
            onClick={handleArchive}
            className="px-3.5 py-2 rounded-xl border border-stone-warm text-slate-blue hover:text-red-700 hover:border-red-300 text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            <Archive className="w-3.5 h-3.5" />
            <span>Archive Version</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-slate-blue hover:text-ink-navy text-xs font-semibold transition-colors"
            >
              Cancel
            </button>

            {!isInternalMarks && (
              <button
                onClick={handlePublish}
                disabled={isPublishing}
                className="px-5 py-2 rounded-xl bg-terracotta text-white text-xs font-bold hover:bg-terracotta/90 transition-all shadow-subtle flex items-center gap-1.5 disabled:opacity-50"
              >
                {isPublishing ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <ShieldCheck className="w-4 h-4" />
                )}
                <span>Publish as Authoritative</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
