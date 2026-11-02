import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Square,
  Sparkles,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  RotateCcw,
  ArrowDown,
  Info,
  Users,
  Building,
  GraduationCap,
  Calendar,
  X,
  Clock,
  CheckCircle,
  MapPin,
  Mail,
  Phone,
  BookOpen
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Message, MessageSource, StudentMatchCard } from '../types';

export const ChatView: React.FC = () => {
  const {
    currentUser,
    chatMessages,
    isStreaming,
    stopStreaming,
    sendMessage,
    setMessageFeedback,
    setPreviewStudentCard
  } = useApp();

  const [inputText, setInputText] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<MessageSource | null>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea up to 8 lines (~190px)
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 190)}px`;
    }
  }, [inputText]);

  // Handle user scrolling to toggle "Jump to latest" pill
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 100;
    setShowScrollBottom(!isAtBottom);
  };

  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  };

  useEffect(() => {
    if (!showScrollBottom) {
      scrollToBottom();
    }
  }, [chatMessages, isStreaming]);

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

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const firstName = currentUser?.fullName?.split(' ')[0] || 'there';

  // Institutional academic prompt chips for empty state
  const quickPrompts = [
    {
      icon: <Calendar className="w-3.5 h-3.5 text-brand-secondary" />,
      text: 'What is my timetable tomorrow?'
    },
    {
      icon: <Clock className="w-3.5 h-3.5 text-brand-accent" />,
      text: 'Which teacher has no scheduled class at 2 PM on Tuesday?'
    },
    {
      icon: <Users className="w-3.5 h-3.5 text-brand-secondary" />,
      text: 'Who is the class coordinator for 2nd year AIR?'
    },
    {
      icon: <Building className="w-3.5 h-3.5 text-brand-accent" />,
      text: 'Which laboratories are available in the Centre for AI?'
    },
    {
      icon: <BookOpen className="w-3.5 h-3.5 text-brand-secondary" />,
      text: 'Explain the current syllabus for my semester'
    },
    {
      icon: <GraduationCap className="w-3.5 h-3.5 text-brand-accent" />,
      text: 'Draft an application for leave'
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-white relative overflow-hidden">
      {/* Scrollable Conversation Container */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 sm:px-6 py-6"
      >
        <div className="max-w-[760px] mx-auto space-y-6">
          {chatMessages.length === 0 ? (
            /* Centered Empty State */
            <div className="min-h-[50vh] flex flex-col items-center justify-center text-center space-y-6 pt-10 animate-fade-in">
              <div className="w-14 h-14 rounded-2xl bg-brand-surface border border-brand-border/60 flex items-center justify-center text-brand-secondary shadow-card">
                <Sparkles className="w-7 h-7 text-brand-accent" />
              </div>

              <div className="space-y-2">
                <h2 className="font-heading font-bold text-2xl sm:text-3xl text-brand-primary tracking-tight">
                  How can I help, {firstName}?
                </h2>
                <p className="text-sm text-brand-muted max-w-md mx-auto leading-relaxed">
                  Ask me anything about MITS Gwalior academics, timetables, Centre for AI laboratories, faculty availability, or campus workflows.
                </p>
              </div>

              {/* Quick Prompt Suggestions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-xl text-left pt-2">
                {quickPrompts.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      sendMessage(q.text);
                    }}
                    className="p-3 rounded-2xl border border-brand-border/70 bg-brand-surface/60 hover:bg-white hover:border-brand-accent/50 hover:shadow-card transition-all duration-150 flex items-start gap-2.5 group"
                  >
                    <span className="p-1 rounded-lg bg-white border border-brand-borderSubtle group-hover:bg-brand-softAccentLight/40 transition-colors">
                      {q.icon}
                    </span>
                    <span className="text-xs font-medium text-brand-primary/90 group-hover:text-brand-primary transition-colors leading-relaxed">
                      {q.text}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Message Thread */
            chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                } animate-fade-in`}
              >
                {/* User Message Bubble */}
                {msg.role === 'user' ? (
                  <div className="max-w-[85%] sm:max-w-[75%] px-4 py-3 rounded-2xl bg-brand-secondary text-white shadow-subtle text-sm leading-relaxed font-sans font-medium">
                    {msg.content}
                  </div>
                ) : (
                  /* Assistant Message */
                  <div className="w-full space-y-4">
                    <div className="flex items-center gap-2 text-xs font-semibold text-brand-secondary">
                      <div className="w-5 h-5 rounded-md bg-brand-primary text-white flex items-center justify-center text-[10px] font-heading font-bold">
                        PU
                      </div>
                      <span>PocketUni Assistant</span>
                    </div>

                    {/* Markdown / Formatted text */}
                    <div className="text-sm text-brand-primary/95 leading-relaxed font-sans space-y-3 prose prose-slate max-w-none">
                      {renderFormattedMessage(msg.content)}
                    </div>

                    {/* Discovery Profile Cards */}
                    {msg.profileCards && msg.profileCards.length > 0 && (
                      <div className="pt-2">
                        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-brand-secondary uppercase tracking-wider">
                          <Users className="w-4 h-4 text-brand-accent" />
                          <span>Matched Student Profiles</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {msg.profileCards.map((card) => (
                            <div
                              key={card.studentId}
                              onClick={() => setPreviewStudentCard(card)}
                              className="p-3.5 rounded-2xl bg-brand-surface border border-brand-border/80 hover:border-brand-accent/60 hover:shadow-card transition-all cursor-pointer group text-left"
                            >
                              <div className="flex items-start gap-3">
                                <img
                                  src={card.pictureUrl}
                                  alt={card.name}
                                  className="w-11 h-11 rounded-xl object-cover border border-white shadow-sm shrink-0"
                                />
                                <div className="min-w-0 flex-1">
                                  <div className="flex items-center justify-between">
                                    <h4 className="font-heading font-semibold text-xs text-brand-primary group-hover:text-brand-accent transition-colors truncate">
                                      {card.name}
                                    </h4>
                                    <span className="text-[10px] font-semibold text-brand-secondary bg-brand-softAccentLight/50 px-1.5 py-0.2 rounded shrink-0">
                                      Yr {card.year}
                                    </span>
                                  </div>
                                  <p className="text-[11px] text-brand-muted truncate">
                                    {card.branch}
                                  </p>
                                </div>
                              </div>

                              <p className="text-[11px] text-brand-primary/80 mt-2 line-clamp-2 leading-relaxed">
                                {card.bio}
                              </p>

                              {/* Tags */}
                              <div className="flex flex-wrap gap-1 mt-2.5">
                                {card.matchedTags.slice(0, 3).map((tag, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 rounded text-[10px] font-medium bg-white border border-brand-borderSubtle text-brand-primary"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {card.openForHackathons && (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-brand-softAccentLight/40 text-brand-secondary border border-brand-softAccent/40">
                                    Hackathons
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Interactive Institutional Widgets */}
                    {msg.widget && msg.widget.type === 'TIMETABLE_CARD' && (
                      <div className="pt-2">
                        <div className="rounded-2xl border border-brand-border/80 bg-brand-surface/40 p-4 space-y-3">
                          <div className="flex items-center justify-between border-b border-brand-border/60 pb-2.5">
                            <div className="flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-brand-secondary" />
                              <span className="font-heading font-semibold text-xs text-brand-primary">
                                {msg.widget.data.day} Schedule • {msg.widget.data.semester}
                              </span>
                            </div>
                            <span className="text-[10px] font-semibold text-brand-secondary bg-white px-2 py-0.5 rounded-full border border-brand-border/70">
                              {msg.widget.data.classes?.length || 0} Lectures
                            </span>
                          </div>

                          <div className="space-y-2">
                            {msg.widget.data.classes?.map((c: any, idx: number) => (
                              <div
                                key={idx}
                                className="p-2.5 rounded-xl bg-white border border-brand-border/60 flex items-center justify-between text-xs"
                              >
                                <div className="flex items-center gap-2.5">
                                  <span className="w-7 h-7 rounded-lg bg-brand-surface text-brand-secondary font-bold text-[11px] flex items-center justify-center shrink-0 border border-brand-borderSubtle">
                                    P{c.period}
                                  </span>
                                  <div>
                                    <div className="font-semibold text-brand-primary flex items-center gap-1.5">
                                      <span>{c.subject}</span>
                                      <span className="text-[10px] font-mono text-brand-muted">({c.course_code})</span>
                                      {c.is_lab && (
                                        <span className="text-[9px] font-bold uppercase tracking-wider bg-brand-softAccentLight text-brand-secondary px-1.5 py-0.2 rounded">
                                          Lab
                                        </span>
                                      )}
                                    </div>
                                    <div className="text-[11px] text-brand-muted mt-0.5">
                                      Faculty: <span className="text-brand-primary font-medium">{c.faculty}</span>
                                    </div>
                                  </div>
                                </div>
                                <div className="text-right shrink-0">
                                  <span className="inline-block px-2 py-0.5 rounded-md bg-stone-warm/50 text-[10px] font-mono font-semibold text-brand-primary border border-stone-border/60">
                                    {c.room}
                                  </span>
                                  <div className="text-[10px] text-brand-muted mt-0.5">{c.time}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {msg.widget && msg.widget.type === 'FACULTY_AVAILABILITY_CARD' && (
                      <div className="pt-2">
                        <div className="rounded-2xl border border-brand-border/80 bg-brand-surface/40 p-4 space-y-3">
                          <div className="flex items-center justify-between border-b border-brand-border/60 pb-2.5">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-brand-accent" />
                              <span className="font-heading font-semibold text-xs text-brand-primary">
                                {msg.widget.data.day} • {msg.widget.data.slot_label} ({msg.widget.data.time_window})
                              </span>
                            </div>
                            <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                              {msg.widget.data.free_faculty_count} Available Faculty
                            </span>
                          </div>

                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {msg.widget.data.free_faculty?.slice(0, 10).map((f: any, idx: number) => (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs bg-white border border-brand-borderSubtle text-brand-primary shadow-subtle"
                              >
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                <span className="font-medium text-[11px]">{f.name}</span>
                              </span>
                            ))}
                          </div>

                          <p className="text-[11px] text-brand-muted italic border-t border-brand-border/40 pt-2 leading-relaxed">
                            {msg.widget.data.disclaimer}
                          </p>
                        </div>
                      </div>
                    )}

                    {msg.widget && msg.widget.type === 'COORDINATOR_CARD' && (
                      <div className="pt-2">
                        <div className="p-3.5 rounded-2xl bg-white border border-brand-border/80 shadow-subtle flex items-start justify-between">
                          <div className="space-y-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-brand-secondary bg-brand-surface px-2 py-0.5 rounded border border-brand-borderSubtle">
                              {msg.widget.data.year} Coordinator • {msg.widget.data.branch}
                            </span>
                            <h4 className="font-heading font-bold text-sm text-brand-primary pt-1">
                              {msg.widget.data.name}
                            </h4>
                            <div className="flex items-center gap-3 text-xs text-brand-muted pt-1">
                              <span className="flex items-center gap-1">
                                <Phone className="w-3.5 h-3.5 text-brand-accent" />
                                {msg.widget.data.contact_number}
                              </span>
                              <a
                                href={`mailto:${msg.widget.data.institutional_email}`}
                                className="flex items-center gap-1 text-brand-secondary hover:underline"
                              >
                                <Mail className="w-3.5 h-3.5" />
                                {msg.widget.data.institutional_email}
                              </a>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Source Chips Under AI Answers (PRD FR-2.5 & Section 7.2) */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="pt-1 flex items-center flex-wrap gap-2">
                        <span className="text-[11px] font-semibold text-brand-muted uppercase tracking-wider">
                          Sources:
                        </span>
                        {msg.sources.map((src, idx) => (
                          <button
                            key={idx}
                            onClick={() => setSelectedSource(src)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-brand-surface border border-brand-border/70 text-brand-secondary hover:bg-brand-softAccentLight/30 hover:border-brand-accent/40 transition-all shadow-subtle"
                          >
                            <span className="w-4 h-4 rounded bg-brand-secondary/10 text-brand-secondary text-[10px] flex items-center justify-center font-bold">
                              {src.rank}
                            </span>
                            <span className="truncate max-w-[200px]">{src.title}</span>
                            <ExternalLink className="w-3 h-3 text-brand-muted" />
                          </button>
                        ))}
                      </div>
                    )}

                    {/* AI Message Action Toolbar */}
                    <div className="flex items-center gap-1 pt-1 text-brand-muted">
                      <button
                        onClick={() => handleCopy(msg.id, msg.content)}
                        className="p-1.5 rounded-lg hover:text-brand-primary hover:bg-brand-surface transition-colors"
                        title="Copy answer"
                      >
                        {copiedId === msg.id ? (
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>

                      <button
                        onClick={() => setMessageFeedback(msg.id, 1)}
                        className={`p-1.5 rounded-lg hover:text-brand-primary hover:bg-brand-surface transition-colors ${
                          msg.feedback === 1 ? 'text-brand-accent bg-brand-surface' : ''
                        }`}
                        title="Helpful"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>

                      <button
                        onClick={() => setMessageFeedback(msg.id, -1)}
                        className={`p-1.5 rounded-lg hover:text-brand-primary hover:bg-brand-surface transition-colors ${
                          msg.feedback === -1 ? 'text-rose-500 bg-rose-50' : ''
                        }`}
                        title="Not helpful"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}

          {/* Streaming Indicator */}
          {isStreaming && (
            <div className="flex items-center gap-2 text-xs text-brand-muted animate-pulse-subtle">
              <span className="w-2 h-2 rounded-full bg-brand-accent" />
              <span>PocketUni assistant is thinking and generating response...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating Jump to Latest Pill */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom(true)}
          className="absolute bottom-24 right-8 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-primary text-white text-xs font-medium shadow-float hover:bg-brand-primaryLight transition-all animate-fade-in"
        >
          <ArrowDown className="w-3.5 h-3.5" />
          <span>Jump to latest</span>
        </button>
      )}

      {/* Sticky Bottom Input Area */}
      <div className="p-4 sm:p-6 bg-white border-t border-brand-border/40">
        <div className="max-w-[760px] mx-auto relative">
          <div className="rounded-2xl border border-brand-border bg-brand-surface/50 shadow-subtle focus-within:border-brand-accent focus-within:bg-white focus-within:ring-2 focus-within:ring-brand-accent/20 transition-all">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              placeholder="Ask about MITS academics, policies, placements or find teammates..."
              className="w-full px-4 pt-3 pb-2 text-sm bg-transparent resize-none text-brand-primary placeholder:text-brand-muted/70 focus:outline-none max-h-[190px]"
            />

            <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
              <span className="text-[11px] text-brand-muted/70 hidden sm:inline">
                Enter to send • Shift + Enter for newline
              </span>

              <div className="flex items-center gap-2 ml-auto">
                {isStreaming ? (
                  <button
                    onClick={stopStreaming}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-medium transition-all"
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

      {/* Source Citation Drawer / Modal */}
      {selectedSource && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-lg bg-white rounded-3xl shadow-float border border-brand-border p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-brand-softAccentLight/50 text-brand-secondary">
                  {selectedSource.category} • Grounded Reference
                </span>
                <h3 className="font-heading font-bold text-base text-brand-primary mt-1">
                  {selectedSource.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedSource(null)}
                className="p-1 rounded-lg text-brand-muted hover:text-brand-primary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-brand-surface border border-brand-border/60 text-xs text-brand-primary/90 leading-relaxed font-sans">
              <p>{selectedSource.snippet}</p>
            </div>

            <div className="flex items-center justify-between pt-2">
              <a
                href={selectedSource.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-secondary hover:text-brand-accent transition-colors"
              >
                <span>Open official page on web.mitsgwalior.in</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <button
                onClick={() => setSelectedSource(null)}
                className="px-4 py-2 rounded-xl bg-brand-primary text-white text-xs font-medium hover:bg-brand-primaryLight transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Formatter to render bullets, bold, and code blocks cleanly
function renderFormattedMessage(content: string) {
  const lines = content.split('\n');
  return (
    <div className="space-y-1.5">
      {lines.map((line, idx) => {
        if (!line.trim()) {
          return <div key={idx} className="h-1.5" />;
        }
        if (line.startsWith('• ') || line.startsWith('- ')) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2">
              <span className="text-brand-accent mt-1.5 w-1.5 h-1.5 rounded-full bg-brand-accent shrink-0" />
              <div dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(line.substring(2)) }} />
            </div>
          );
        }
        return (
          <p key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(line) }} />
        );
      })}
    </div>
  );
}

function formatInlineMarkdown(text: string): string {
  // Replace bold **text**
  let res = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-brand-primary">$1</strong>');
  // Replace citations like [1] with stylized badge
  res = res.replace(/\[(\d+)\]/g, '<span class="inline-flex items-center justify-center px-1 py-0.2 mx-0.5 text-[10px] font-bold text-brand-secondary bg-brand-secondary/10 rounded">[$1]</span>');
  return res;
}
