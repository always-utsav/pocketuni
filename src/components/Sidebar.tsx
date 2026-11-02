import React, { useState } from 'react';
import {
  MessageSquare,
  Plus,
  FileText,
  Users,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
  Trash2,
  Edit2,
  GraduationCap,
  Sparkles,
  Search,
  Shield
} from 'lucide-react';
import { useApp } from '../context/AppContext';

interface SidebarProps {
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, setMobileOpen }) => {
  const {
    currentUser,
    sidebarCollapsed,
    setSidebarCollapsed,
    chats,
    currentChatId,
    setCurrentChatId,
    createNewChat,
    deleteChat,
    renameChat,
    activeView,
    setActiveView,
    setSelectedFaculty
  } = useApp();

  const [chatSearch, setChatSearch] = useState('');
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [menuChatId, setMenuChatId] = useState<string | null>(null);

  // Filter chats by search
  const filteredChats = chats.filter(c =>
    c.title.toLowerCase().includes(chatSearch.toLowerCase()) && c.kind === 'general'
  );

  // Group chats by date (Today, Yesterday, Earlier)
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000;

  const todayChats = filteredChats.filter(c => new Date(c.createdAt).getTime() >= today);
  const yesterdayChats = filteredChats.filter(c => {
    const t = new Date(c.createdAt).getTime();
    return t < today && t >= yesterday;
  });
  const earlierChats = filteredChats.filter(c => new Date(c.createdAt).getTime() < yesterday);

  const handleStartRename = (id: string, currentTitle: string) => {
    setEditingChatId(id);
    setEditingTitle(currentTitle);
    setMenuChatId(null);
  };

  const handleSaveRename = (id: string) => {
    if (editingTitle.trim()) {
      renameChat(id, editingTitle.trim());
    }
    setEditingChatId(null);
  };

  const handleSelectChat = (id: string) => {
    setCurrentChatId(id);
    setActiveView('chat');
    setMobileOpen(false);
  };

  const handleGoToAppAgent = () => {
    // Open application agent
    if (currentUser?.role === 'faculty') {
      setActiveView('applications_list');
    } else {
      // Find existing active draft chat or create new
      const appChat = chats.find(c => c.kind === 'application_agent' && c.status === 'active');
      if (appChat) {
        setCurrentChatId(appChat.id);
        setActiveView('application_agent_chat');
      } else {
        createNewChat('application_agent');
      }
    }
    setMobileOpen(false);
  };

  const handleGoToApplications = () => {
    setActiveView('applications_list');
    setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-brand-primary/40 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 flex flex-col bg-[#092328] text-white border-r border-[#12544F]/40 transition-all duration-200 ease-in-out ${
          sidebarCollapsed ? 'w-20' : 'w-72'
        } ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Top Header & Branding */}
        <div className="flex items-center justify-between p-4 border-b border-[#12544F]/30">
          {!sidebarCollapsed ? (
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-secondary via-brand-accent to-brand-softAccent flex items-center justify-center text-white shadow-sm font-heading font-extrabold text-sm tracking-tight">
                PU
              </div>
              <div>
                <span className="font-heading font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                  PocketUni
                  <span className="text-[10px] uppercase font-semibold px-1.5 py-0.2 bg-brand-accent/25 text-brand-softAccent rounded">
                    MITS
                  </span>
                </span>
                <p className="text-[10px] text-brand-darkMuted leading-none">MITS Gwalior Assistant</p>
              </div>
            </div>
          ) : (
            <div className="w-full flex justify-center">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-secondary via-brand-accent to-brand-softAccent flex items-center justify-center text-white font-heading font-bold text-sm">
                PU
              </div>
            </div>
          )}

          {/* Desktop Collapse Toggle */}
          <button
            onClick={() => setSidebarCollapsed(prev => !prev)}
            className="hidden lg:flex p-1.5 rounded-lg text-brand-darkMuted hover:text-white hover:bg-white/10 transition-colors"
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              createNewChat('general');
              setMobileOpen(false);
            }}
            className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl font-medium text-xs transition-all duration-150 ${
              sidebarCollapsed ? 'justify-center bg-brand-secondary/40 text-brand-softAccent hover:bg-brand-secondary/60' : 'bg-brand-secondary/50 hover:bg-brand-secondary/80 text-white border border-brand-accent/30 shadow-subtle'
            }`}
            title="New Chat"
          >
            <Plus className="w-4 h-4 text-brand-softAccent shrink-0" />
            {!sidebarCollapsed && <span className="font-medium tracking-wide">New Chat</span>}
          </button>
        </div>

        {/* Main Nav Items */}
        <div className="px-3 pb-2 space-y-1">
          {/* Super Admin Portal (Admin Only) */}
          {currentUser?.role === 'super_admin' && (
            <button
              onClick={() => {
                setActiveView('super_admin_dashboard');
                setMobileOpen(false);
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                activeView === 'super_admin_dashboard'
                  ? 'bg-brand-accent text-white font-semibold shadow-subtle'
                  : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
              }`}
              title="Super Admin Portal"
            >
              <Shield className="w-4 h-4 text-brand-accent shrink-0" />
              {!sidebarCollapsed && (
                <div className="flex-1 flex items-center justify-between text-left">
                  <span>Super Admin Portal</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-brand-accent/30 text-white font-mono font-bold">
                    Gov
                  </span>
                </div>
              )}
            </button>
          )}

          {/* Applications Navigation */}
          <button
            onClick={handleGoToApplications}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
              activeView === 'applications_list' || activeView === 'application_detail'
                ? 'bg-brand-secondary/60 text-white font-semibold'
                : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
            }`}
            title="Applications"
          >
            <FileText className="w-4 h-4 text-brand-softAccent shrink-0" />
            {!sidebarCollapsed && (
              <div className="flex-1 flex items-center justify-between text-left">
                <span>{currentUser?.role === 'faculty' ? 'Faculty Inbox' : 'Applications'}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-brand-secondary/40 text-brand-softAccentLight font-mono">
                  {currentUser?.role === 'faculty' ? 'Inbox' : 'Queue'}
                </span>
              </div>
            )}
          </button>

          {/* Application Agent (Student Only) */}
          {currentUser?.role !== 'faculty' && (
            <button
              onClick={handleGoToAppAgent}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                activeView === 'application_agent_chat'
                  ? 'bg-brand-accent/30 text-white font-semibold border border-brand-accent/40'
                  : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
              }`}
              title="Application Agent"
            >
              <Sparkles className="w-4 h-4 text-brand-accent shrink-0" />
              {!sidebarCollapsed && (
                <div className="flex-1 flex items-center justify-between text-left">
                  <span>Application Agent</span>
                  <span className="text-[10px] font-semibold text-brand-softAccent bg-brand-accent/20 px-1.5 py-0.5 rounded">
                    AI
                  </span>
                </div>
              )}
            </button>
          )}

          {/* Faculty Directory */}
          <button
            onClick={() => {
              setActiveView('faculty_directory');
              setMobileOpen(false);
            }}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
              activeView === 'faculty_directory'
                ? 'bg-brand-secondary/60 text-white font-semibold'
                : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
            }`}
            title="Faculty Directory"
          >
            <GraduationCap className="w-4 h-4 text-brand-softAccent shrink-0" />
            {!sidebarCollapsed && <span>Faculty Directory</span>}
          </button>
        </div>

        {/* Recent Chats Section */}
        {!sidebarCollapsed && (
          <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4">
            {/* Quick search past chats */}
            {chats.length > 3 && (
              <div className="relative mb-2">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-brand-darkMuted" />
                <input
                  type="text"
                  placeholder="Search chats..."
                  value={chatSearch}
                  onChange={(e) => setChatSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded-lg text-white placeholder-brand-darkMuted/60 focus:outline-none focus:border-brand-accent/50"
                />
              </div>
            )}

            {/* Chat List Groups */}
            {todayChats.length > 0 && (
              <div>
                <p className="px-2 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-brand-darkMuted/70">
                  Today
                </p>
                <div className="space-y-0.5">
                  {todayChats.map(renderChatRow)}
                </div>
              </div>
            )}

            {yesterdayChats.length > 0 && (
              <div>
                <p className="px-2 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-brand-darkMuted/70">
                  Yesterday
                </p>
                <div className="space-y-0.5">
                  {yesterdayChats.map(renderChatRow)}
                </div>
              </div>
            )}

            {earlierChats.length > 0 && (
              <div>
                <p className="px-2 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-brand-darkMuted/70">
                  Earlier
                </p>
                <div className="space-y-0.5">
                  {earlierChats.map(renderChatRow)}
                </div>
              </div>
            )}

            {filteredChats.length === 0 && (
              <div className="py-6 text-center text-brand-darkMuted text-xs">
                No conversations yet
              </div>
            )}
          </div>
        )}

        {sidebarCollapsed && (
          <div className="flex-1 flex flex-col items-center py-4 space-y-2 overflow-y-auto">
            {chats.slice(0, 6).map((c) => (
              <button
                key={c.id}
                onClick={() => handleSelectChat(c.id)}
                className={`p-2 rounded-xl transition-all ${
                  currentChatId === c.id && activeView === 'chat'
                    ? 'bg-brand-accent text-white shadow-sm'
                    : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
                }`}
                title={c.title}
              >
                <MessageSquare className="w-4 h-4" />
              </button>
            ))}
          </div>
        )}

        {/* User Profile Footer */}
        <div className="p-3 border-t border-[#12544F]/30 bg-[#06181c]">
          <button
            onClick={() => {
              setSelectedFaculty(null);
              setActiveView('profile');
              setMobileOpen(false);
            }}
            className="w-full flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-all text-left group"
            title="View Profile"
          >
            <img
              src={currentUser?.pictureUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80'}
              alt={currentUser?.fullName || 'User'}
              className="w-9 h-9 rounded-xl object-cover border border-white/20 shrink-0 group-hover:border-brand-accent/60 transition-colors"
            />
            {!sidebarCollapsed && (
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-white truncate group-hover:text-brand-softAccent transition-colors">
                    {currentUser?.fullName || 'Guest User'}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`inline-block w-1.5 h-1.5 rounded-full ${currentUser?.role === 'faculty' ? 'bg-amber-400' : 'bg-brand-softAccent'}`} />
                  <p className="text-[10px] text-brand-darkMuted capitalize truncate">
                    {currentUser?.role === 'faculty' ? 'Faculty Member' : 'Student'}
                  </p>
                </div>
              </div>
            )}
          </button>
        </div>
      </aside>
    </>
  );

  function renderChatRow(chat: (typeof filteredChats)[0]) {
    const isSelected = currentChatId === chat.id && activeView === 'chat';
    const isEditing = editingChatId === chat.id;

    if (isEditing) {
      return (
        <div key={chat.id} className="p-1">
          <input
            type="text"
            value={editingTitle}
            onChange={(e) => setEditingTitle(e.target.value)}
            onBlur={() => handleSaveRename(chat.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSaveRename(chat.id);
              if (e.key === 'Escape') setEditingChatId(null);
            }}
            autoFocus
            className="w-full px-2 py-1 text-xs bg-white text-brand-primary rounded border border-brand-accent focus:outline-none"
          />
        </div>
      );
    }

    return (
      <div
        key={chat.id}
        className={`group relative flex items-center justify-between px-2.5 py-2 rounded-xl text-xs transition-colors cursor-pointer ${
          isSelected
            ? 'bg-brand-secondary/60 text-white font-medium'
            : 'text-brand-darkMuted hover:text-white hover:bg-white/5'
        }`}
        onClick={() => handleSelectChat(chat.id)}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70" />
          <span className="truncate">{chat.title}</span>
        </div>

        {/* Options Menu Button */}
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setMenuChatId(menuChatId === chat.id ? null : chat.id);
            }}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-opacity"
            title="Chat options"
          >
            <MoreVertical className="w-3.5 h-3.5" />
          </button>

          {menuChatId === chat.id && (
            <div
              className="absolute right-0 top-6 w-32 bg-white text-brand-primary rounded-xl shadow-float border border-brand-border py-1 z-50 text-xs"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => handleStartRename(chat.id, chat.title)}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-brand-surface text-left"
              >
                <Edit2 className="w-3.5 h-3.5 text-brand-muted" />
                <span>Rename</span>
              </button>
              <button
                onClick={() => {
                  deleteChat(chat.id);
                  setMenuChatId(null);
                }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-rose-50 text-rose-600 text-left"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }
};
