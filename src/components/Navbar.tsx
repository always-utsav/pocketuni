import React, { useState } from 'react';
import { Menu, LogOut, Sparkles, Shield, ChevronDown, Check, UserCheck } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { NotificationsDropdown } from './NotificationsDropdown';
import { apiClient } from '../services/apiClient';

interface NavbarProps {
  onOpenMobileSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMobileSidebar }) => {
  const {
    currentUser,
    setCurrentUser,
    logout,
    activeView,
    setActiveView
  } = useApp();

  const [isContextDropdownOpen, setIsContextDropdownOpen] = useState(false);
  const [isSwitchingContext, setIsSwitchingContext] = useState(false);

  const getTitle = () => {
    switch (activeView) {
      case 'chat':
        return 'College Assistant';
      case 'application_agent_chat':
        return 'Application Agent';
      case 'applications_list':
        return currentUser?.role === 'faculty' ? 'Faculty Application Inbox' : 'My Applications';
      case 'application_detail':
        return 'Application Review';
      case 'profile':
        return currentUser?.role === 'faculty' ? 'Faculty Profile' : 'Student Profile & Discovery';
      case 'faculty_directory':
        return 'Official Faculty Directory';
      case 'super_admin_dashboard':
        return 'Institutional Super Admin Portal';
      default:
        return 'PocketUni';
    }
  };

  const handleSwitchContext = async (target: 'SUPER_ADMIN' | 'STUDENT' | 'FACULTY') => {
    if (!currentUser || currentUser.role !== 'super_admin') return;
    setIsSwitchingContext(true);
    try {
      await apiClient.switchAdminContext(target);
      const updatedUser = {
        ...currentUser,
        activeContext: target.toLowerCase() as any
      };
      localStorage.setItem('pocketuni_user', JSON.stringify(updatedUser));
      setCurrentUser(updatedUser);

      // Navigate to matching primary view
      if (target === 'SUPER_ADMIN') {
        setActiveView('super_admin_dashboard');
      } else if (target === 'FACULTY') {
        setActiveView('applications_list');
      } else {
        setActiveView('chat');
      }
    } catch (err) {
      console.error('Failed to switch context:', err);
    } finally {
      setIsSwitchingContext(false);
      setIsContextDropdownOpen(false);
    }
  };

  const activeContextLabel = currentUser?.activeContext
    ? currentUser.activeContext.toUpperCase()
    : currentUser?.role.toUpperCase();

  return (
    <header className="h-16 px-4 lg:px-8 border-b border-brand-border/60 bg-white/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-30 transition-all">
      {/* Left: Mobile Menu + View Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="p-2 -ml-2 rounded-xl text-brand-primary/70 hover:text-brand-primary hover:bg-brand-surface lg:hidden transition-all"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <h1 className="font-heading font-bold text-base lg:text-lg text-brand-primary tracking-tight">
            {getTitle()}
          </h1>
          {activeView === 'application_agent_chat' && (
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-softAccentLight/50 text-brand-secondary border border-brand-softAccent/40">
              <Sparkles className="w-3 h-3 text-brand-accent" />
              Slot-Filling Agent
            </span>
          )}
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Super Admin Controlled Context Switcher */}
        {currentUser?.role === 'super_admin' && (
          <div className="relative">
            <button
              onClick={() => setIsContextDropdownOpen(!isContextDropdownOpen)}
              disabled={isSwitchingContext}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 hover:bg-amber-100/80 border border-amber-200 text-xs font-semibold text-amber-900 transition-all shadow-subtle"
              title="Super Admin Context Switcher"
            >
              <Shield className="w-3.5 h-3.5 text-amber-600" />
              <span className="hidden sm:inline">Active View:</span>
              <span className="font-bold underline decoration-amber-400">
                {activeContextLabel === 'SUPER_ADMIN' ? 'Admin Portal' : activeContextLabel === 'FACULTY' ? 'Faculty Mode' : 'Student Mode'}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-amber-600" />
            </button>

            {isContextDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-stone-200 rounded-xl shadow-elevated py-1.5 z-50 text-xs animate-in fade-in zoom-in-95 duration-150">
                <div className="px-3 py-1.5 border-b border-stone-100 text-[10px] font-bold text-stone-500 uppercase tracking-wider">
                  Admin Context Switch
                </div>

                <button
                  onClick={() => handleSwitchContext('SUPER_ADMIN')}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-stone-50 transition-colors ${
                    activeContextLabel === 'SUPER_ADMIN' ? 'font-bold text-amber-800 bg-amber-50/50' : 'text-stone-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Shield className="w-3.5 h-3.5 text-amber-600" />
                    <span>Super Admin Portal</span>
                  </div>
                  {activeContextLabel === 'SUPER_ADMIN' && <Check className="w-3.5 h-3.5 text-amber-600" />}
                </button>

                <button
                  onClick={() => handleSwitchContext('STUDENT')}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-stone-50 transition-colors ${
                    activeContextLabel === 'STUDENT' ? 'font-bold text-terracotta bg-terracotta-light/30' : 'text-stone-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <UserCheck className="w-3.5 h-3.5 text-terracotta" />
                    <span>Student Experience</span>
                  </div>
                  {activeContextLabel === 'STUDENT' && <Check className="w-3.5 h-3.5 text-terracotta" />}
                </button>

                <button
                  onClick={() => handleSwitchContext('FACULTY')}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-stone-50 transition-colors ${
                    activeContextLabel === 'FACULTY' ? 'font-bold text-slate-700 bg-slate-100/60' : 'text-stone-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="w-3.5 h-3.5 text-slate-600 font-bold text-[10px] flex items-center justify-center">Prof</span>
                    <span>Faculty Experience</span>
                  </div>
                  {activeContextLabel === 'FACULTY' && <Check className="w-3.5 h-3.5 text-slate-600" />}
                </button>
              </div>
            )}
          </div>
        )}

        {/* User Identity Pill */}
        {currentUser && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-surface border border-brand-border/70 text-xs shadow-subtle">
            <span
              className={`w-2 h-2 rounded-full ${
                currentUser.role === 'super_admin' ? 'bg-terracotta' : currentUser.role === 'faculty' ? 'bg-amber-500' : 'bg-brand-accent'
              }`}
            />
            <span className="font-medium text-brand-primary">
              {currentUser.fullName}
            </span>
            <span className="text-brand-muted hidden md:inline text-[11px]">
              {currentUser.role === 'super_admin' ? 'Super Admin' : currentUser.role === 'faculty' ? 'Faculty Member' : 'Student (CAI)'}
            </span>
          </div>
        )}

        {/* Notifications */}
        <NotificationsDropdown />

        {/* Log Out */}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-brand-primary/70 hover:text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-200 transition-all focus:outline-none text-xs font-medium"
          title="Sign Out"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
};
