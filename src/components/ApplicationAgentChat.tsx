import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Square,
  Sparkles,
  Edit3,
  Share2,
  Search,
  Check,
  X,
  FileText,
  UserCheck
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { useApp } from '../context/AppContext';
import { MITS_FACULTY, searchFaculty } from '../data/facultyData';
import { FacultyProfile } from '../types';

export const ApplicationAgentChat: React.FC = () => {
  const {
    currentUser,
    chatMessages,
    isStreaming,
    stopStreaming,
    sendMessage,
    currentDraftApplication,
    updateApplicationContent,
    shareApplicationToProfessor,
    setActiveView,
    createNewChat
  } = useApp();

  const [inputText, setInputText] = useState('');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProf, setSelectedProf] = useState<FacultyProfile | null>(null);
  const [filteredFaculty, setFilteredFaculty] = useState<FacultyProfile[]>(MITS_FACULTY);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debounced search for Share to Professor modal (250ms debounced per PRD FR-5.4 & Section 7.4)
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilteredFaculty(searchFaculty(searchQuery));
    }, 250);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isStreaming]);

  // Set initial edited text when draft is ready
  useEffect(() => {
    if (currentDraftApplication) {
      setEditedText(currentDraftApplication.content);
    }
  }, [currentDraftApplication]);

  const handleSend = () => {
    if (!inputText.trim() || isStreaming) return;
    sendMessage(inputText.trim());
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSaveEditor = () => {
    if (currentDraftApplication && editedText.trim()) {
      updateApplicationContent(currentDraftApplication.id, editedText.trim());
      setIsEditModalOpen(false);
    }
  };

  const handleConfirmShare = () => {
    if (!currentDraftApplication || !selectedProf) return;

    const ok = shareApplicationToProfessor(currentDraftApplication.id, selectedProf.facultyId);
    if (ok) {
      setIsShareModalOpen(false);

      // Celebrate with subtle confetti
      try {
        confetti({
          particleCount: 60,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#2A835F', '#8BBB92', '#12544F']
        });
      } catch (e) {
        // Safe fallback
      }

      // Automatically return to Application List with new item at top (PRD Section 6)
      setActiveView('applications_list');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-white relative overflow-hidden">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
        <div className="max-w-[760px] mx-auto space-y-6">
          {chatMessages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.role === 'user' ? 'items-end' : 'items-start'
              } animate-fade-in`}
            >
              {msg.role === 'user' ? (
                <div className="max-w-[85%] sm:max-w-[75%] px-4 py-3 rounded-2xl bg-brand-secondary text-white shadow-subtle text-sm leading-relaxed font-sans font-medium">
                  {msg.content}
                </div>
              ) : (
                <div className="w-full space-y-4">
                  <div className="flex items-center gap-2 text-xs font-semibold text-brand-secondary">
                    <div className="w-5 h-5 rounded-md bg-brand-accent text-white flex items-center justify-center text-[10px] font-heading font-bold shadow-sm">
                      PU
                    </div>
                    <span>Application Agent</span>
                  </div>

                  {/* Message Body */}
                  <div className="text-sm text-brand-primary/95 leading-relaxed font-sans space-y-3">
                    {msg.contentType === 'application_draft' && currentDraftApplication ? (
                      <div className="space-y-4">
                        <p className="text-sm text-brand-primary font-medium">
                          I have drafted your formal application below adhering to MITS academic letter standards:
                        </p>

                        {/* Formal Letter Card Preview */}
                        <div className="p-6 rounded-2xl bg-brand-surface border border-brand-border/80 shadow-subtle font-mono text-xs text-brand-primary whitespace-pre-wrap leading-relaxed relative">
                          <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2 py-0.5 rounded bg-brand-softAccentLight/40 text-brand-secondary text-[10px] font-sans font-semibold">
                            <FileText className="w-3 h-3" />
                            Draft Preview
                          </div>
                          {currentDraftApplication.content}
                        </div>

                        {/* Action Buttons: Edit Application and Share to Professor (PRD Section 7.4) */}
                        <div className="flex flex-wrap items-center gap-3 pt-2">
                          <button
                            onClick={() => {
                              setEditedText(currentDraftApplication.content);
                              setIsEditModalOpen(true);
                            }}
                            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-brand-border bg-white hover:bg-brand-surface text-brand-primary text-xs font-semibold shadow-subtle hover:border-brand-secondary transition-all"
                          >
                            <Edit3 className="w-3.5 h-3.5 text-brand-secondary" />
                            <span>Edit Application</span>
                          </button>

                          <button
                            onClick={() => setIsShareModalOpen(true)}
                            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-accent hover:bg-brand-accentHover text-white text-xs font-semibold shadow-card transition-all"
                          >
                            <Share2 className="w-3.5 h-3.5" />
                            <span>Share to Professor</span>
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {isStreaming && (
            <div className="flex items-center gap-2 text-xs text-brand-muted animate-pulse-subtle">
              <span className="w-2 h-2 rounded-full bg-brand-accent" />
              <span>Application Agent is preparing draft...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area with Chip "Application Agent" above input (PRD Section 7.4) */}
      <div className="p-4 sm:p-6 bg-white border-t border-brand-border/40">
        <div className="max-w-[760px] mx-auto relative space-y-2">
          {/* Labeled Chip "Application Agent" */}
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-softAccentLight/40 border border-brand-softAccent/40 text-[11px] font-semibold text-brand-secondary">
              <Sparkles className="w-3 h-3 text-brand-accent" />
              <span>Application Agent</span>
            </div>
            <span className="text-[11px] text-brand-muted">
              Auto-prefills your name, roll no, and branch
            </span>
          </div>

          <div className="rounded-2xl border border-brand-border bg-brand-surface/50 shadow-subtle focus-within:border-brand-accent focus-within:bg-white focus-within:ring-2 focus-within:ring-brand-accent/20 transition-all">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              placeholder="e.g., 'I need leave for 3 days due to sickness' or 'make it shorter'..."
              className="w-full px-4 pt-3 pb-2 text-sm bg-transparent resize-none text-brand-primary placeholder:text-brand-muted/70 focus:outline-none max-h-[180px]"
            />

            <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
              <span className="text-[11px] text-brand-muted/70 hidden sm:inline">
                Enter to send • Shift + Enter for newline
              </span>

              <div className="flex items-center gap-2 ml-auto">
                {isStreaming ? (
                  <button
                    onClick={stopStreaming}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-medium"
                  >
                    <Square className="w-3 h-3 fill-current" />
                    <span>Stop</span>
                  </button>
                ) : (
                  <button
                    onClick={handleSend}
                    disabled={!inputText.trim()}
                    aria-label="Send message"
                    className="p-2 rounded-xl bg-brand-secondary hover:bg-brand-primary disabled:opacity-40 disabled:hover:bg-brand-secondary text-white transition-all shadow-sm focus:outline-none"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Application Modal (PRD Section 7.4) */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-2xl bg-white rounded-3xl shadow-float border border-brand-border p-6 flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between pb-3 border-b border-brand-border/60">
              <div className="flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-brand-accent" />
                <h3 className="font-heading font-bold text-base text-brand-primary">
                  Edit Application Draft
                </h3>
              </div>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="p-1 rounded-lg text-brand-muted hover:text-brand-primary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 flex-1 overflow-y-auto">
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                rows={16}
                className="w-full p-4 rounded-xl border border-brand-border font-mono text-xs text-brand-primary bg-brand-surface/40 leading-relaxed focus:outline-none focus:border-brand-accent"
              />
            </div>

            <div className="pt-3 border-t border-brand-border/60 flex items-center justify-between">
              <span className="text-[11px] text-brand-muted">
                Changes will be saved as a new version before sharing.
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-brand-border text-brand-muted hover:text-brand-primary text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEditor}
                  className="px-5 py-2 rounded-xl bg-brand-primary hover:bg-brand-primaryLight text-white text-xs font-semibold shadow-sm transition-all"
                >
                  Save Draft
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Share to Professor Modal (PRD Section 7.4) */}
      {isShareModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-lg bg-white rounded-3xl shadow-float border border-brand-border p-6 flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between pb-3 border-b border-brand-border/60">
              <div>
                <h3 className="font-heading font-bold text-base text-brand-primary">
                  Share to Professor
                </h3>
                <p className="text-xs text-brand-muted mt-0.5">
                  Select a recipient faculty member from the official MITS directory
                </p>
              </div>
              <button
                onClick={() => setIsShareModalOpen(false)}
                className="p-1 rounded-lg text-brand-muted hover:text-brand-primary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Debounced 250ms Search Input */}
            <div className="py-3">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-brand-muted" />
                <input
                  type="text"
                  placeholder="Search professor by name, department, or area..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-brand-border bg-brand-surface focus:outline-none focus:border-brand-accent focus:bg-white"
                />
              </div>
            </div>

            {/* Professor Candidates List */}
            <div className="flex-1 overflow-y-auto divide-y divide-brand-borderSubtle max-h-72">
              {filteredFaculty.length === 0 ? (
                <div className="py-8 text-center text-xs text-brand-muted">
                  No professors match your search with hint to try a different spelling.
                </div>
              ) : (
                filteredFaculty.map((prof) => {
                  const isSelected = selectedProf?.facultyId === prof.facultyId;
                  return (
                    <div
                      key={prof.facultyId}
                      onClick={() => setSelectedProf(prof)}
                      className={`p-3 flex items-center justify-between cursor-pointer transition-colors rounded-xl ${
                        isSelected
                          ? 'bg-brand-softAccentLight/30 border border-brand-softAccent/40'
                          : 'hover:bg-brand-surface'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <img
                          src={prof.photoUrl}
                          alt={prof.name}
                          className="w-10 h-10 rounded-xl object-cover border border-brand-border shrink-0"
                        />
                        <div>
                          <h4 className="font-heading font-semibold text-xs text-brand-primary">
                            {prof.name}
                          </h4>
                          <p className="text-[11px] text-brand-muted">
                            {prof.designation} • {prof.department}
                          </p>
                          <p className="text-[10px] text-brand-secondary font-medium">
                            {prof.emailPublic}
                          </p>
                        </div>
                      </div>

                      <div
                        className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 ${
                          isSelected
                            ? 'bg-brand-accent border-brand-accent text-white'
                            : 'border-brand-border'
                        }`}
                      >
                        {isSelected && <Check className="w-3 h-3" />}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Footer with Send */}
            <div className="pt-4 border-t border-brand-border/60 flex items-center justify-between">
              <span className="text-[11px] text-brand-muted">
                {selectedProf ? `Selected: ${selectedProf.name}` : 'Select a professor to proceed'}
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsShareModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-brand-border text-brand-muted hover:text-brand-primary text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmShare}
                  disabled={!selectedProf}
                  className="px-5 py-2 rounded-xl bg-brand-accent hover:bg-brand-accentHover disabled:opacity-40 text-white text-xs font-semibold shadow-card transition-all"
                >
                  Send Application
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
