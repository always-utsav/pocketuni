import React, { useState, useRef, useEffect } from 'react';
import { Bell, Check, ExternalLink, ShieldCheck, Mail, AlertCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const NotificationsDropdown: React.FC = () => {
  const {
    notifications,
    unreadNotificationCount,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    setSelectedApplicationId,
    setActiveView
  } = useApp();

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleNotificationClick = (id: string, appId?: string) => {
    markNotificationAsRead(id);
    if (appId) {
      setSelectedApplicationId(appId);
      setActiveView('application_detail');
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open notifications"
        className="relative p-2 rounded-xl text-brand-primary/70 hover:text-brand-primary hover:bg-brand-primary/5 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-brand-accent/30"
      >
        <Bell className="w-5 h-5" />
        {unreadNotificationCount > 0 && (
          <span className="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-brand-accent text-[10px] font-bold text-white shadow-sm animate-pulse-subtle">
            {unreadNotificationCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white border border-brand-border/60 shadow-float z-50 overflow-hidden animate-fade-in">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-brand-surface border-b border-brand-border/40">
            <div className="flex items-center gap-2">
              <span className="font-heading font-semibold text-sm text-brand-primary">Notifications</span>
              {unreadNotificationCount > 0 && (
                <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-brand-accent/15 text-brand-accent">
                  {unreadNotificationCount} new
                </span>
              )}
            </div>
            {unreadNotificationCount > 0 && (
              <button
                onClick={markAllNotificationsAsRead}
                className="text-xs text-brand-secondary hover:text-brand-accent font-medium transition-colors"
              >
                Mark all read
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-[380px] overflow-y-auto divide-y divide-brand-borderSubtle">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-brand-muted text-sm">
                No notifications right now
              </div>
            ) : (
              notifications.map((item) => {
                const isUnread = !item.readAt;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleNotificationClick(item.id, item.applicationId)}
                    className={`p-3.5 flex gap-3 transition-colors cursor-pointer text-left hover:bg-brand-surface/70 ${
                      isUnread ? 'bg-brand-softAccentLight/20' : 'bg-white'
                    }`}
                  >
                    <div className="mt-0.5 shrink-0">
                      {item.type === 'application_approved' ? (
                        <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                          <Check className="w-4 h-4" />
                        </div>
                      ) : item.type === 'application_rejected' ? (
                        <div className="w-7 h-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
                          <AlertCircle className="w-4 h-4" />
                        </div>
                      ) : item.type === 'application_received' ? (
                        <div className="w-7 h-7 rounded-lg bg-blue-50 text-brand-secondary flex items-center justify-center">
                          <Mail className="w-4 h-4" />
                        </div>
                      ) : (
                        <div className="w-7 h-7 rounded-lg bg-brand-surface text-brand-primary flex items-center justify-center">
                          <ShieldCheck className="w-4 h-4" />
                        </div>
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1 mb-0.5">
                        <p className={`text-xs ${isUnread ? 'font-semibold text-brand-primary' : 'font-medium text-brand-primary/80'}`}>
                          {item.title}
                        </p>
                        <span className="text-[10px] text-brand-muted shrink-0">
                          {new Date(item.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        </span>
                      </div>
                      <p className="text-xs text-brand-muted line-clamp-2 leading-relaxed">
                        {item.body}
                      </p>
                      {item.applicationId && (
                        <span className="inline-flex items-center gap-1 text-[11px] text-brand-accent font-medium mt-1">
                          View details <ExternalLink className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};
