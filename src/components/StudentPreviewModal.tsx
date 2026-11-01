import React from 'react';
import { X, Github, Linkedin, Globe, Sparkles, Award, Code2, Users, Briefcase } from 'lucide-react';
import { StudentMatchCard } from '../types';
import { INITIAL_STUDENTS } from '../data/studentData';

interface StudentPreviewModalProps {
  card: StudentMatchCard | null;
  onClose: () => void;
}

export const StudentPreviewModal: React.FC<StudentPreviewModalProps> = ({ card, onClose }) => {
  if (!card) return null;

  // Retrieve extended profile data if available
  const fullRecord = INITIAL_STUDENTS.find(s => s.user.id === card.studentId);
  const profile = fullRecord?.profile;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-primary/40 backdrop-blur-sm animate-fade-in">
      <div
        className="relative w-full max-w-xl max-h-[90vh] bg-white rounded-3xl shadow-float border border-brand-border/60 overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Banner */}
        <div className="h-24 bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent p-4 relative flex items-start justify-end">
          <button
            onClick={onClose}
            className="p-1.5 rounded-full bg-white/20 hover:bg-white/30 text-white backdrop-blur-md transition-all"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Container */}
        <div className="px-6 pb-6 pt-0 overflow-y-auto space-y-5 -mt-12">
          {/* Avatar & Title */}
          <div className="flex items-end justify-between gap-4">
            <div className="relative">
              <img
                src={card.pictureUrl}
                alt={card.name}
                className="w-20 h-20 rounded-2xl object-cover border-4 border-white shadow-card bg-brand-surface"
              />
              {card.openForHackathons && (
                <span className="absolute -bottom-1 -right-1 p-1 bg-brand-accent text-white rounded-lg shadow-sm" title="Open for Hackathons">
                  <Sparkles className="w-3.5 h-3.5" />
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 pb-1">
              {card.githubUrl && (
                <a
                  href={card.githubUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 rounded-xl text-brand-muted hover:text-brand-primary hover:bg-brand-surface border border-brand-borderSubtle transition-all"
                  title="GitHub Profile"
                >
                  <Github className="w-4 h-4" />
                </a>
              )}
              {card.linkedinUrl && (
                <a
                  href={card.linkedinUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 rounded-xl text-brand-muted hover:text-brand-primary hover:bg-brand-surface border border-brand-borderSubtle transition-all"
                  title="LinkedIn Profile"
                >
                  <Linkedin className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-heading font-bold text-xl text-brand-primary">{card.name}</h3>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-softAccentLight/50 text-brand-secondary">
                Year {card.year}
              </span>
            </div>
            <p className="text-xs font-medium text-brand-muted mt-0.5">
              {card.branch} • MITS Gwalior {card.rollNumber ? `(${card.rollNumber})` : ''}
            </p>
          </div>

          {/* Bio */}
          <div className="p-3.5 rounded-2xl bg-brand-surface border border-brand-border/40">
            <p className="text-xs text-brand-primary/90 leading-relaxed font-sans">{card.bio}</p>
          </div>

          {/* Collaboration Status */}
          {profile?.lookingFor && (
            <div className="p-3 rounded-xl bg-brand-softAccentLight/30 border border-brand-softAccent/40 flex items-start gap-2.5">
              <Users className="w-4 h-4 text-brand-secondary shrink-0 mt-0.5" />
              <div>
                <p className="text-[11px] font-semibold text-brand-secondary uppercase tracking-wider">Looking For</p>
                <p className="text-xs text-brand-primary/90 mt-0.5 font-medium">{profile.lookingFor}</p>
              </div>
            </div>
          )}

          {/* Skills & Badges */}
          <div>
            <h4 className="text-xs font-semibold text-brand-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Code2 className="w-3.5 h-3.5 text-brand-accent" />
              Skills & Proficiencies
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {profile?.skills ? (
                profile.skills.map((s) => (
                  <span
                    key={s.id}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-white border border-brand-border/80 text-brand-primary"
                  >
                    <span>{s.name}</span>
                    <span className="text-[10px] text-brand-muted font-normal">• {s.proficiency}</span>
                  </span>
                ))
              ) : (
                card.topSkills.map((sk, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-brand-surface border border-brand-border/80 text-brand-primary"
                  >
                    {sk}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Preferred Roles & Availability */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-brand-surface border border-brand-borderSubtle">
              <p className="font-semibold text-brand-muted text-[11px] uppercase tracking-wider">Preferred Roles</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {card.preferredRoles.map((r, i) => (
                  <span key={i} className="font-medium text-brand-primary">{r}{i < card.preferredRoles.length - 1 ? ',' : ''}</span>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-brand-surface border border-brand-borderSubtle">
              <p className="font-semibold text-brand-muted text-[11px] uppercase tracking-wider">Availability</p>
              <p className="mt-1 font-medium text-brand-primary">
                {profile?.availabilityHoursPerWeek ? `${profile.availabilityHoursPerWeek} hrs/week` : 'Flexible'}
              </p>
              {profile?.availabilityNotes && (
                <p className="text-[10px] text-brand-muted mt-0.5 truncate">{profile.availabilityNotes}</p>
              )}
            </div>
          </div>

          {/* Featured Projects if any */}
          {profile?.projects && profile.projects.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-brand-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-brand-secondary" />
                Featured Projects
              </h4>
              <div className="space-y-2">
                {profile.projects.map(proj => (
                  <div key={proj.id} className="p-3 rounded-xl bg-white border border-brand-border/70 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-brand-primary">{proj.title}</span>
                      {proj.repoUrl && (
                        <a href={proj.repoUrl} target="_blank" rel="noreferrer" className="text-brand-accent hover:underline flex items-center gap-0.5 text-[11px]">
                          Code <Globe className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    <p className="text-brand-muted mt-1 leading-relaxed text-[11px]">{proj.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {proj.techNotes.map((t, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 text-[10px] bg-brand-surface text-brand-secondary rounded font-medium">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Footer */}
          <div className="pt-2 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-brand-primary text-white text-xs font-medium hover:bg-brand-primaryLight transition-all"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
