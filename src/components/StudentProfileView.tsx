import React, { useState } from 'react';
import {
  User,
  Mail,
  GraduationCap,
  Sparkles,
  Github,
  Linkedin,
  Globe,
  Upload,
  Check,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Code2,
  Briefcase,
  Award,
  Users,
  FileText,
  Clock,
  Lock,
  ShieldCheck
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { SkillProficiency, StudentProject, StudentSkill } from '../types';

export const StudentProfileView: React.FC = () => {
  const {
    currentUser,
    currentStudentProfile,
    updateStudentProfile,
    profileSaveIndicator
  } = useApp();

  // Local states for adding skill/project
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState<SkillProficiency>('Intermediate');
  const [showAddProject, setShowAddProject] = useState(false);
  const [newProject, setNewProject] = useState<Partial<StudentProject>>({
    title: '',
    description: '',
    repoUrl: '',
    liveUrl: '',
    techNotes: []
  });
  const [projectTechInput, setProjectTechInput] = useState('');
  const [resumeUploadError, setResumeUploadError] = useState<string | null>(null);

  if (!currentUser || !currentStudentProfile) {
    return (
      <div className="p-8 text-center text-brand-muted text-sm">
        Please sign in as a student to edit your profile.
      </div>
    );
  }

  const p = currentStudentProfile;

  const handleToggleDiscovery = () => {
    updateStudentProfile({ profileVisible: !p.profileVisible });
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    const newSkill: StudentSkill = {
      id: `sk-${Date.now()}`,
      name: newSkillName.trim(),
      proficiency: newSkillProficiency
    };

    updateStudentProfile({
      skills: [...p.skills, newSkill],
      techStack: Array.from(new Set([...p.techStack, newSkillName.trim()]))
    });

    setNewSkillName('');
  };

  const handleRemoveSkill = (id: string) => {
    updateStudentProfile({
      skills: p.skills.filter(s => s.id !== id)
    });
  };

  const handleAddProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProject.title?.trim() || !newProject.description?.trim()) return;

    const techList = projectTechInput
      .split(',')
      .map(t => t.trim())
      .filter(Boolean);

    const project: StudentProject = {
      id: `proj-${Date.now()}`,
      title: newProject.title.trim(),
      description: newProject.description.trim(),
      repoUrl: newProject.repoUrl?.trim(),
      liveUrl: newProject.liveUrl?.trim(),
      techNotes: techList.length > 0 ? techList : ['React', 'TypeScript']
    };

    updateStudentProfile({
      projects: [...p.projects, project]
    });

    setNewProject({ title: '', description: '', repoUrl: '', liveUrl: '', techNotes: [] });
    setProjectTechInput('');
    setShowAddProject(false);
  };

  const handleRemoveProject = (id: string) => {
    updateStudentProfile({
      projects: p.projects.filter(proj => proj.id !== id)
    });
  };

  const handleResumeSimulatedUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResumeUploadError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    // PRD Section 16.6 & 21.1: Max 5 MB, PDF format validation
    if (file.type !== 'application/pdf') {
      setResumeUploadError('Only PDF files are supported for resumes.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setResumeUploadError('File size exceeds the 5 MB limit.');
      return;
    }

    const sizeFormatted = (file.size / (1024 * 1024)).toFixed(1) + ' MB';
    updateStudentProfile({
      resumeFileName: file.name,
      resumeFileSize: sizeFormatted,
      resumeUploadedAt: new Date().toISOString()
    });
  };

  const handleRemoveResume = () => {
    updateStudentProfile({
      resumeFileName: undefined,
      resumeFileSize: undefined,
      resumeUploadedAt: undefined
    });
  };

  return (
    <div className="flex-1 overflow-y-auto bg-brand-surface/40 p-4 sm:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Profile Header & Identity Card (PRD Section 7.7) */}
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative">
          {/* Autosave Status Indicator */}
          {profileSaveIndicator && (
            <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-medium animate-fade-in">
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>Autosaved</span>
            </div>
          )}

          <div className="flex items-center gap-4">
            <img
              src={currentUser.pictureUrl}
              alt={currentUser.fullName}
              className="w-20 h-20 rounded-2xl object-cover border-2 border-brand-accent/40 shadow-card shrink-0"
            />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-heading font-bold text-xl text-brand-primary">
                  {currentUser.fullName}
                </h2>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-brand-softAccentLight/40 text-brand-secondary">
                  Google Verified
                </span>
              </div>
              <p className="text-xs text-brand-muted flex items-center gap-1.5 mt-1">
                <Mail className="w-3.5 h-3.5" />
                {currentUser.email.includes('@example.invalid')
                  ? 'aarav.sharma@mitsgwl.ac.in (Verified Institutional Student Identity)'
                  : currentUser.email}
              </p>
              <p className="text-xs font-medium text-brand-secondary mt-0.5">
                {currentUser.branch || 'CSE'} • Roll No: {currentUser.rollNumber || '0901CS231001'}
              </p>
            </div>
          </div>

          {/* Profile Completeness Meter (PRD Section 7.7 & FR-6.3) */}
          <div className="w-full md:w-56 p-4 rounded-2xl bg-brand-surface border border-brand-border/60">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-brand-primary">Profile Completeness</span>
              <span className="font-mono font-bold text-brand-accent">
                {p.completenessScore}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-brand-borderSubtle overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-secondary via-brand-accent to-brand-softAccent rounded-full transition-all duration-300"
                style={{ width: `${p.completenessScore}%` }}
              />
            </div>
            <p className="text-[10px] text-brand-muted mt-2 leading-tight">
              Higher completeness ranks your profile higher in peer discovery searches.
            </p>
          </div>
        </div>

        {/* Institution-Controlled Master Identity (Locked / Read-Only) */}
        <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-subtle space-y-3">
          <div className="flex items-center justify-between border-b border-stone-100 pb-2.5">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-amber-600" />
              <h3 className="font-heading font-semibold text-xs text-ink-navy uppercase tracking-wider">
                Institution-Controlled Academic Record (Locked)
              </h3>
            </div>
            <span className="text-[10px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-amber-600" />
              Verified by Registrar
            </span>
          </div>

          <p className="text-[11px] text-slate-blue">
            These fields are verified against the official MITS academic roster and cannot be changed by students. To request modifications, contact the Centre for AI academic coordinator.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Roll Number</span>
              <p className="font-mono text-xs font-semibold text-ink-navy truncate">{currentUser.rollNumber || 'DEMO-0901AI231001'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Enrolment No</span>
              <p className="font-mono text-xs font-semibold text-ink-navy truncate">{currentUser.enrolmentNumber || currentUser.rollNumber || '0901AI231001'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Programme</span>
              <p className="text-xs font-semibold text-ink-navy truncate">{currentUser.programme || 'B.Tech'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Department</span>
              <p className="text-xs font-semibold text-ink-navy truncate">{currentUser.departmentName || 'Centre for AI'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Branch</span>
              <p className="text-xs font-semibold text-ink-navy truncate">{currentUser.branch || 'AI & Machine Learning'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Batch</span>
              <p className="font-mono text-xs font-semibold text-ink-navy truncate">{currentUser.batch || '2023-2027'}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Semester & Sec</span>
              <p className="font-mono text-xs font-semibold text-ink-navy truncate">Sem {currentUser.semester || 5} (Sec {currentUser.section || 'A'})</p>
            </div>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-100">
              <span className="text-[10px] font-bold text-slate-blue uppercase">Academic Year</span>
              <p className="font-mono text-xs font-semibold text-ink-navy truncate">{currentUser.academicYear || '2026-2027'}</p>
            </div>
          </div>
        </div>

        {/* Discovery Visibility Toggle (PRD Section 7.7 & A-3) */}
        <div className="bg-white rounded-2xl border border-brand-border p-4 shadow-subtle flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl ${p.profileVisible ? 'bg-brand-softAccentLight/50 text-brand-secondary' : 'bg-gray-100 text-gray-500'}`}>
              {p.profileVisible ? <Eye className="w-5 h-5 text-brand-accent" /> : <EyeOff className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="font-heading font-semibold text-sm text-brand-primary">
                Show my profile in student discovery
              </h3>
              <p className="text-xs text-brand-muted">
                Allow fellow MITS students to find you for hackathon teams and project collaborations.
              </p>
            </div>
          </div>

          <button
            onClick={handleToggleDiscovery}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              p.profileVisible
                ? 'bg-brand-accent text-white shadow-sm'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {p.profileVisible ? 'Discovery Active' : 'Hidden'}
          </button>
        </div>

        {/* Bio & Looking For */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider">
            About & Teammate Search Goals
          </h3>

          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <label className="font-semibold text-brand-primary">Student Bio</label>
              <span className="text-[11px] text-brand-muted font-mono">{p.bio.length} / 500</span>
            </div>
            <textarea
              maxLength={500}
              rows={3}
              value={p.bio}
              onChange={(e) => updateStudentProfile({ bio: e.target.value })}
              placeholder="Tell MITS peers about your background, strengths, and coding passions..."
              className="w-full p-3 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent focus:bg-white leading-relaxed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-brand-primary mb-1">
              What are you looking for?
            </label>
            <input
              type="text"
              value={p.lookingFor}
              onChange={(e) => updateStudentProfile({ lookingFor: e.target.value })}
              placeholder="e.g. Teammates for Smart India Hackathon, need backend/cloud devs..."
              className="w-full px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent focus:bg-white"
            />
          </div>
        </div>

        {/* Collaboration Signals (PRD Section 8.6 & 10) */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-5">
          <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider flex items-center gap-2">
            <Users className="w-4 h-4 text-brand-accent" />
            Collaboration Signals
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Open for Hackathons */}
            <div
              onClick={() => updateStudentProfile({ openForHackathons: !p.openForHackathons })}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                p.openForHackathons
                  ? 'bg-brand-softAccentLight/30 border-brand-accent text-brand-primary'
                  : 'bg-brand-surface border-brand-border text-brand-muted hover:border-brand-border'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-brand-primary">Open for Hackathons</span>
                <span className={`w-3.5 h-3.5 rounded-full ${p.openForHackathons ? 'bg-brand-accent' : 'bg-gray-300'}`} />
              </div>
              <p className="text-[11px] text-brand-muted mt-1">Available to join hackathon teams</p>
            </div>

            {/* Open Source Contributor */}
            <div
              onClick={() => updateStudentProfile({ openSourceContributor: !p.openSourceContributor })}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                p.openSourceContributor
                  ? 'bg-brand-softAccentLight/30 border-brand-accent text-brand-primary'
                  : 'bg-brand-surface border-brand-border text-brand-muted hover:border-brand-border'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-brand-primary">Open Source Contributor</span>
                <span className={`w-3.5 h-3.5 rounded-full ${p.openSourceContributor ? 'bg-brand-accent' : 'bg-gray-300'}`} />
              </div>
              <p className="text-[11px] text-brand-muted mt-1">Contributes to GitHub repos</p>
            </div>

            {/* Competitive Programming */}
            <div
              onClick={() => updateStudentProfile({ competitiveProgramming: !p.competitiveProgramming })}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                p.competitiveProgramming
                  ? 'bg-brand-softAccentLight/30 border-brand-accent text-brand-primary'
                  : 'bg-brand-surface border-brand-border text-brand-muted hover:border-brand-border'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-brand-primary">Competitive Coder</span>
                <span className={`w-3.5 h-3.5 rounded-full ${p.competitiveProgramming ? 'bg-brand-accent' : 'bg-gray-300'}`} />
              </div>
              <p className="text-[11px] text-brand-muted mt-1">LeetCode / Codeforces active</p>
            </div>
          </div>

          {/* Weekly Availability Slider */}
          <div className="pt-2">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-brand-primary">Availability (Hours / Week)</span>
              <span className="font-mono font-bold text-brand-accent">
                {p.availabilityHoursPerWeek} hrs / week
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={60}
              step={2}
              value={p.availabilityHoursPerWeek}
              onChange={(e) => updateStudentProfile({ availabilityHoursPerWeek: Number(e.target.value) })}
              className="w-full accent-brand-accent cursor-pointer"
            />
            <input
              type="text"
              value={p.availabilityNotes}
              onChange={(e) => updateStudentProfile({ availabilityNotes: e.target.value })}
              placeholder="e.g., Evenings after 5 PM and full weekends"
              className="mt-2 w-full px-3 py-1.5 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent"
            />
          </div>
        </div>

        {/* Skills & Taxonomy (PRD Section 8.6 & 16.3) */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider flex items-center gap-2">
              <Code2 className="w-4 h-4 text-brand-accent" />
              Technical Skills & Proficiencies
            </h3>
          </div>

          {/* Skill Pills */}
          <div className="flex flex-wrap gap-2">
            {p.skills.map((skill) => (
              <span
                key={skill.id}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium bg-brand-surface border border-brand-border text-brand-primary group"
              >
                <span>{skill.name}</span>
                <span className="text-[10px] text-brand-muted font-normal">• {skill.proficiency}</span>
                <button
                  onClick={() => handleRemoveSkill(skill.id)}
                  className="text-brand-muted hover:text-rose-600 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>

          {/* Add Skill Form */}
          <form onSubmit={handleAddSkill} className="flex items-center gap-2 pt-2">
            <input
              type="text"
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              placeholder="Add skill (e.g. Flutter, PyTorch, Go)..."
              className="flex-1 px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent focus:bg-white"
            />
            <select
              value={newSkillProficiency}
              onChange={(e) => setNewSkillProficiency(e.target.value as SkillProficiency)}
              className="px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface text-brand-primary focus:outline-none"
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-brand-primary hover:bg-brand-primaryLight text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </form>
        </div>

        {/* Projects Showcase (PRD Section 8.6) */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-secondary" />
              Featured Projects ({p.projects.length})
            </h3>
            <button
              onClick={() => setShowAddProject(!showAddProject)}
              className="inline-flex items-center gap-1 text-xs font-semibold text-brand-secondary hover:text-brand-accent"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Project</span>
            </button>
          </div>

          {/* Projects List */}
          <div className="space-y-3">
            {p.projects.map((proj) => (
              <div key={proj.id} className="p-4 rounded-xl border border-brand-border bg-brand-surface/40 relative">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-heading font-semibold text-xs text-brand-primary">{proj.title}</h4>
                    <p className="text-xs text-brand-muted mt-1 leading-relaxed">{proj.description}</p>
                  </div>
                  <button
                    onClick={() => handleRemoveProject(proj.id)}
                    className="text-brand-muted hover:text-rose-600 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-center gap-3 mt-3 text-[11px]">
                  {proj.repoUrl && (
                    <a href={proj.repoUrl} target="_blank" rel="noreferrer" className="text-brand-accent hover:underline flex items-center gap-1">
                      <Github className="w-3 h-3" /> Code
                    </a>
                  )}
                  {proj.liveUrl && (
                    <a href={proj.liveUrl} target="_blank" rel="noreferrer" className="text-brand-secondary hover:underline flex items-center gap-1">
                      <Globe className="w-3 h-3" /> Live Demo
                    </a>
                  )}
                </div>

                <div className="flex flex-wrap gap-1 mt-2.5">
                  {proj.techNotes.map((t, idx) => (
                    <span key={idx} className="px-2 py-0.5 text-[10px] bg-white border border-brand-borderSubtle text-brand-primary rounded font-mono">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* New Project Form */}
          {showAddProject && (
            <form onSubmit={handleAddProject} className="p-4 rounded-2xl border border-brand-accent/40 bg-brand-surface space-y-3 animate-fade-in">
              <input
                type="text"
                placeholder="Project Title"
                value={newProject.title || ''}
                onChange={(e) => setNewProject(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 text-xs rounded-xl border border-brand-border bg-white"
                required
              />
              <textarea
                placeholder="Project summary and architecture details..."
                value={newProject.description || ''}
                onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
                rows={2}
                className="w-full p-3 text-xs rounded-xl border border-brand-border bg-white"
                required
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  placeholder="GitHub Repo URL"
                  value={newProject.repoUrl || ''}
                  onChange={(e) => setNewProject(prev => ({ ...prev, repoUrl: e.target.value }))}
                  className="px-3 py-2 text-xs rounded-xl border border-brand-border bg-white"
                />
                <input
                  type="text"
                  placeholder="Tech used (comma separated: React, Supabase)"
                  value={projectTechInput}
                  onChange={(e) => setProjectTechInput(e.target.value)}
                  className="px-3 py-2 text-xs rounded-xl border border-brand-border bg-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowAddProject(false)}
                  className="px-3 py-1.5 rounded-lg border border-brand-border text-xs text-brand-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-brand-accent text-white text-xs font-semibold"
                >
                  Save Project
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Links & Resume (PRD Section 8.6 & 16.6) */}
        <div className="bg-white rounded-2xl border border-brand-border p-6 shadow-subtle space-y-4">
          <h3 className="font-heading font-bold text-sm text-brand-primary uppercase tracking-wider">
            Public Links & Resume
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-brand-primary mb-1">GitHub Profile</label>
              <input
                type="text"
                value={p.githubUrl}
                onChange={(e) => updateStudentProfile({ githubUrl: e.target.value })}
                placeholder="https://github.com/..."
                className="w-full px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-brand-primary mb-1">LinkedIn Profile</label>
              <input
                type="text"
                value={p.linkedinUrl}
                onChange={(e) => updateStudentProfile({ linkedinUrl: e.target.value })}
                placeholder="https://linkedin.com/in/..."
                className="w-full px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-brand-primary mb-1">Portfolio URL</label>
              <input
                type="text"
                value={p.portfolioUrl}
                onChange={(e) => updateStudentProfile({ portfolioUrl: e.target.value })}
                placeholder="https://..."
                className="w-full px-3 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent"
              />
            </div>
          </div>

          {/* Resume Upload Simulator */}
          <div className="pt-2">
            <label className="block text-[11px] font-semibold text-brand-primary mb-1">
              Resume (PDF upload up to 5 MB)
            </label>

            {p.resumeFileName ? (
              <div className="p-3.5 rounded-xl border border-brand-accent/40 bg-brand-surface flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-brand-softAccentLight/40 text-brand-secondary flex items-center justify-center">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-semibold text-xs text-brand-primary">{p.resumeFileName}</p>
                    <p className="text-[10px] text-brand-muted">
                      {p.resumeFileSize} • Uploaded on {p.resumeUploadedAt ? new Date(p.resumeUploadedAt).toLocaleDateString() : 'Recent'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleRemoveResume}
                  className="text-xs text-rose-600 hover:underline font-medium"
                >
                  Remove
                </button>
              </div>
            ) : (
              <label className="p-6 rounded-2xl border-2 border-dashed border-brand-border hover:border-brand-accent/50 bg-brand-surface/50 hover:bg-white flex flex-col items-center justify-center cursor-pointer transition-all">
                <Upload className="w-6 h-6 text-brand-muted mb-2" />
                <span className="text-xs font-semibold text-brand-primary">Click to upload your resume</span>
                <span className="text-[10px] text-brand-muted mt-0.5">PDF format only (Max 5 MB)</span>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handleResumeSimulatedUpload}
                  className="hidden"
                />
              </label>
            )}

            {resumeUploadError && (
              <p className="text-xs text-rose-600 mt-1 font-medium">{resumeUploadError}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
