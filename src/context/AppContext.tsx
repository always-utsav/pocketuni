import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  User,
  StudentProfile,
  Chat,
  Message,
  Application,
  NotificationItem,
  FacultyProfile,
  StudentMatchCard
} from '../types';
import { INITIAL_STUDENTS } from '../data/studentData';
import { MITS_FACULTY } from '../data/facultyData';
import { executeRAGQuery } from '../services/ragEngine';
import { searchStudents } from '../services/discoveryEngine';
import { processAgentInput, ApplicationSlots } from '../services/applicationAgentEngine';
import { apiClient } from '../services/apiClient';

export type ActiveView =
  | 'landing'
  | 'chat'
  | 'application_agent_chat'
  | 'applications_list'
  | 'application_detail'
  | 'profile'
  | 'faculty_directory'
  | 'super_admin_dashboard';

interface AppContextType {
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;
  currentStudentProfile: StudentProfile | null;
  setCurrentStudentProfile: (profile: StudentProfile | null) => void;
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;
  // Auth
  loginAs: (userEmail: string) => boolean;
  logout: () => void;
  authError: string | null;
  clearAuthError: () => void;
  // Navigation & layout
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (v: boolean | ((prev: boolean) => boolean)) => void;
  // Chats
  chats: Chat[];
  currentChatId: string | null;
  setCurrentChatId: (id: string | null) => void;
  chatMessages: Message[];
  isStreaming: boolean;
  stopStreaming: () => void;
  sendMessage: (text: string) => void;
  createNewChat: (kind?: 'general' | 'application_agent') => string;
  deleteChat: (id: string) => void;
  renameChat: (id: string, newTitle: string) => void;
  setMessageFeedback: (messageId: string, feedback: 1 | -1) => void;
  // Applications
  applications: Application[];
  selectedApplicationId: string | null;
  setSelectedApplicationId: (id: string | null) => void;
  currentDraftApplication: Application | null;
  updateApplicationContent: (appId: string, newContent: string) => void;
  shareApplicationToProfessor: (appId: string, facultyId: string) => boolean;
  decideApplication: (appId: string, decision: 'approved' | 'rejected', note?: string) => boolean;
  deleteDraftApplication: (appId: string) => void;
  // Profile
  updateStudentProfile: (updates: Partial<StudentProfile>) => void;
  profileSaveIndicator: boolean;
  // Notifications
  notifications: NotificationItem[];
  unreadNotificationCount: number;
  markNotificationAsRead: (id: string) => void;
  markAllNotificationsAsRead: () => void;
  // Faculty
  facultyList: FacultyProfile[];
  selectedFaculty: FacultyProfile | null;
  setSelectedFaculty: (fac: FacultyProfile | null) => void;
  // Modals & previews
  previewStudentCard: StudentMatchCard | null;
  setPreviewStudentCard: (card: StudentMatchCard | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Initial default user: Aarav Sharma (Student)
const DEFAULT_USER = INITIAL_STUDENTS[0].user;
const DEFAULT_PROFILE = INITIAL_STUDENTS[0].profile;

// Initial applications
const INITIAL_APPLICATIONS: Application[] = [];

const INITIAL_CHATS: Chat[] = [];

const INITIAL_MESSAGES: Record<string, Message[]> = {};

const INITIAL_NOTIFICATIONS: NotificationItem[] = [];

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Current user state (defaults to null if not logged in)
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('pocketuni_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [currentStudentProfile, setCurrentStudentProfile] = useState<StudentProfile | null>(() => {
    const saved = localStorage.getItem('pocketuni_profile');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeView, setActiveView] = useState<ActiveView>(() => {
    const saved = localStorage.getItem('pocketuni_user');
    return saved ? 'chat' : 'landing';
  });

  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    return localStorage.getItem('pocketuni_sidebar_collapsed') === 'true';
  });

  const [chats, setChats] = useState<Chat[]>(() => {
    const saved = localStorage.getItem('pocketuni_chats');
    return saved ? JSON.parse(saved) : INITIAL_CHATS;
  });

  const [currentChatId, setCurrentChatId] = useState<string | null>(() => {
    return chats.length > 0 ? chats[0].id : null;
  });

  const [messagesMap, setMessagesMap] = useState<Record<string, Message[]>>(() => {
    const saved = localStorage.getItem('pocketuni_messages');
    return saved ? JSON.parse(saved) : INITIAL_MESSAGES;
  });

  const [applications, setApplications] = useState<Application[]>(() => {
    const saved = localStorage.getItem('pocketuni_applications');
    return saved ? JSON.parse(saved) : INITIAL_APPLICATIONS;
  });

  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [currentDraftApplication, setCurrentDraftApplication] = useState<Application | null>(null);

  const [notifications, setNotifications] = useState<NotificationItem[]>(() => {
    const saved = localStorage.getItem('pocketuni_notifications');
    return saved ? JSON.parse(saved) : INITIAL_NOTIFICATIONS;
  });

  const [authError, setAuthError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [profileSaveIndicator, setProfileSaveIndicator] = useState<boolean>(false);

  const [selectedFaculty, setSelectedFaculty] = useState<FacultyProfile | null>(null);
  const [previewStudentCard, setPreviewStudentCard] = useState<StudentMatchCard | null>(null);

  // Sync to localStorage
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('pocketuni_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('pocketuni_user');
    }
  }, [currentUser]);

  useEffect(() => {
    if (currentStudentProfile) {
      localStorage.setItem('pocketuni_profile', JSON.stringify(currentStudentProfile));
    }
  }, [currentStudentProfile]);

  useEffect(() => {
    localStorage.setItem('pocketuni_sidebar_collapsed', String(sidebarCollapsed));
  }, [sidebarCollapsed]);

  useEffect(() => {
    localStorage.setItem('pocketuni_chats', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem('pocketuni_messages', JSON.stringify(messagesMap));
  }, [messagesMap]);

  useEffect(() => {
    localStorage.setItem('pocketuni_applications', JSON.stringify(applications));
  }, [applications]);

  useEffect(() => {
    localStorage.setItem('pocketuni_notifications', JSON.stringify(notifications));
  }, [notifications]);

  // Auth methods
  const loginAs = (emailInput: string): boolean => {
    setAuthError(null);
    const email = emailInput.trim().toLowerCase();

    // 1. Initial Super Admin check
    if (email === 'utsavkumawat05@gmail.com') {
      const adminUser: User = {
        id: 'usr-admin-utsav',
        googleSub: 'google-sub-utsav-admin',
        email: 'utsavkumawat05@gmail.com',
        role: 'super_admin',
        fullName: 'Utsav Kumawat',
        pictureUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80',
        isActive: true,
        lastLoginAt: new Date().toISOString(),
        designation: 'Lead Platform Architect & Super Administrator',
        departmentName: 'Centre for Artificial Intelligence'
      };
      setCurrentUser(adminUser);
      setCurrentStudentProfile(null);
      setActiveView('super_admin_dashboard');
      apiClient.devLogin(email).catch(() => {});
      return true;
    }

    // 2. Student Domain Check (@mitsgwl.ac.in or synthetic @example.invalid)
    if (email.endsWith('@mitsgwl.ac.in') || email.endsWith('@example.invalid')) {
      const foundStudent = INITIAL_STUDENTS.find(s => s.user.email.toLowerCase() === email);
      if (foundStudent) {
        setCurrentUser(foundStudent.user);
        setCurrentStudentProfile(foundStudent.profile);
      } else {
        const namePart = email.split('@')[0].replace('.', ' ');
        const newUser: User = {
          id: `usr-${Date.now()}`,
          googleSub: `sub-${Date.now()}`,
          email,
          role: 'student',
          fullName: namePart.charAt(0).toUpperCase() + namePart.slice(1),
          pictureUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
          isActive: true,
          lastLoginAt: new Date().toISOString(),
          branch: 'Centre for Artificial Intelligence',
          yearOfStudy: 2,
          graduationYear: 2027
        };
        setCurrentUser(newUser);
        setCurrentStudentProfile({
          studentId: newUser.id,
          bio: 'Centre for AI Student at MITS Gwalior',
          lookingFor: 'Collaborators for AI & Hackathons',
          openForHackathons: true,
          openSourceContributor: true,
          competitiveProgramming: true,
          competitiveHandles: {},
          githubUrl: '',
          linkedinUrl: '',
          portfolioUrl: '',
          availabilityHoursPerWeek: 15,
          availabilityNotes: '',
          preferredRoles: ['AI Engineer', 'Software Developer'],
          clubs: ['Coding Club MITS'],
          skills: [{ id: 'sk-init', name: 'Python', proficiency: 'Intermediate' }],
          techStack: ['Python', 'FastAPI'],
          interests: ['Artificial Intelligence'],
          domains: ['AI & Robotics'],
          projects: [],
          experiences: [],
          certifications: [],
          profileVisible: true,
          completenessScore: 75,
          updatedAt: new Date().toISOString()
        });
      }
      setActiveView('chat');
      apiClient.devLogin(email).catch(() => {});
      return true;
    } else if (email.endsWith('@mitsgwalior.in')) {
      // 3. Faculty role (@mitsgwalior.in)
      const matchedFac = MITS_FACULTY.find(f => f.emailPublic.toLowerCase() === email) || {
        facultyId: 'fac-cai-mentor',
        name: 'Dr. Mausam Chouksey',
        designation: 'Assistant Professor (Designated Mentor)',
        department: 'Centre for Artificial Intelligence & ECE',
        emailPublic: 'dr.mausam.chouksey@mitsgwalior.in',
        photoUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80'
      };

      const facultyUser: User = {
        id: matchedFac.facultyId,
        googleSub: `sub-fac-${matchedFac.facultyId}`,
        email: matchedFac.emailPublic,
        role: 'faculty',
        fullName: matchedFac.name,
        pictureUrl: matchedFac.photoUrl,
        isActive: true,
        lastLoginAt: new Date().toISOString(),
        departmentName: matchedFac.department,
        designation: matchedFac.designation
      };
      setCurrentUser(facultyUser);
      setCurrentStudentProfile(null);
      setActiveView('chat');
      apiClient.devLogin(email).catch(() => {});
      return true;
    } else {
      setAuthError('PocketUni is available only for MITS Gwalior accounts (@mitsgwl.ac.in for students, @mitsgwalior.in for faculty, or configured admin).');
      return false;
    }
  };

  const logout = () => {
    apiClient.logout().catch(() => {});
    setCurrentUser(null);
    setCurrentStudentProfile(null);
    setActiveView('landing');
  };

  const clearAuthError = () => setAuthError(null);

  // Chat handling
  const createNewChat = (kind: 'general' | 'application_agent' = 'general'): string => {
    const newChatId = `chat-${Date.now()}`;
    const newChat: Chat = {
      id: newChatId,
      userId: currentUser?.id || 'usr-guest',
      title: kind === 'application_agent' ? 'Application Draft Assistant' : 'New Conversation',
      kind,
      status: 'active',
      createdAt: new Date().toISOString(),
      lastMessageAt: new Date().toISOString()
    };
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChatId);
    setMessagesMap(prev => ({
      ...prev,
      [newChatId]: []
    }));

    if (kind === 'application_agent') {
      setActiveView('application_agent_chat');
      // Send initial welcoming agent message
      const greetingMsg: Message = {
        id: `msg-${Date.now()}`,
        chatId: newChatId,
        role: 'assistant',
        content: `Hello ${currentUser?.fullName ? currentUser.fullName.split(' ')[0] : 'there'}! I am your **Application Agent**.\n\nI can draft formal, college-standard letters for:\n• **Leave of Absence** (sick leave, family events)\n• **Bonafide / Character Certificate** (for loans, passport, bus pass)\n• **No Objection Certificate (NOC)** (for corporate/research internships)\n• **Event & Venue Permission** (seminar hall, auditorium, lab access)\n\nWhat type of application would you like me to write today?`,
        contentType: 'text',
        createdAt: new Date().toISOString()
      };
      setMessagesMap(prev => ({
        ...prev,
        [newChatId]: [greetingMsg]
      }));
    } else {
      setActiveView('chat');
    }

    return newChatId;
  };

  const deleteChat = (id: string) => {
    setChats(prev => prev.filter(c => c.id !== id));
    setMessagesMap(prev => {
      const copy = { ...prev };
      delete copy[id];
      return copy;
    });
    if (currentChatId === id) {
      const remaining = chats.filter(c => c.id !== id);
      setCurrentChatId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const renameChat = (id: string, newTitle: string) => {
    setChats(prev => prev.map(c => c.id === id ? { ...c, title: newTitle } : c));
  };

  const setMessageFeedback = (messageId: string, feedback: 1 | -1) => {
    if (!currentChatId) return;
    setMessagesMap(prev => {
      const list = prev[currentChatId] || [];
      return {
        ...prev,
        [currentChatId]: list.map(m => m.id === messageId ? { ...m, feedback } : m)
      };
    });
  };

  let streamingAbort = false;

  const stopStreaming = () => {
    streamingAbort = true;
    setIsStreaming(false);
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || !currentChatId || isStreaming) return;

    const activeChat = chats.find(c => c.id === currentChatId);
    const isAppAgent = activeChat?.kind === 'application_agent';

    const userMessageId = `msg-${Date.now()}`;
    const userMsg: Message = {
      id: userMessageId,
      chatId: currentChatId,
      role: 'user',
      content: text.trim(),
      contentType: 'text',
      createdAt: new Date().toISOString()
    };

    // Update title if first user message
    const currentList = messagesMap[currentChatId] || [];
    if (currentList.filter(m => m.role === 'user').length === 0) {
      const autoTitle = text.length > 38 ? text.substring(0, 35) + '...' : text;
      renameChat(currentChatId, autoTitle);
    }

    // Add user message to UI immediately
    setMessagesMap(prev => ({
      ...prev,
      [currentChatId]: [...(prev[currentChatId] || []), userMsg]
    }));

    setIsStreaming(true);
    streamingAbort = false;

    try {
      if (isAppAgent && currentUser) {
        // Application Agent workflow
        const agentState = activeChat?.agentState as { slots?: ApplicationSlots; state?: string } | undefined;
        let result: any = null;
        try {
          result = await apiClient.applicationAgentChat({
            message: text,
            conversationHistory: (messagesMap[currentChatId] || []).map(m => ({ role: m.role, content: m.content })),
            currentSlots: agentState?.slots
          });
        } catch (_) {
          result = processAgentInput(
            text,
            agentState?.slots,
            agentState?.state || 'COLLECTING',
            currentUser
          );
        }

        if (result.is_draft_ready && result.draft_content) {
          const draftAppId = result.application_id || `app-draft-${Date.now()}`;
          const newDraft: Application = {
            id: draftAppId,
            studentId: currentUser.id,
            studentName: currentUser.fullName,
            studentEmail: currentUser.email,
            studentRollNumber: currentUser.rollNumber || '0901CS231001',
            studentBranch: currentUser.branch || 'Artificial Intelligence',
            studentYear: currentUser.yearOfStudy || 2,
            chatId: currentChatId,
            title: `Application - ${currentUser.fullName}`,
            type: (result.slots?.type as any) || 'leave',
            status: 'draft',
            currentVersionId: `v-${Date.now()}`,
            content: result.draft_content,
            versions: [
              {
                id: `v-${Date.now()}`,
                versionNo: 1,
                content: result.draft_content,
                createdBy: 'ai',
                createdAt: new Date().toISOString()
              }
            ],
            statusHistory: [
              {
                id: `sh-${Date.now()}`,
                fromStatus: 'created',
                toStatus: 'draft',
                actorUserId: currentUser.id,
                actorName: currentUser.fullName,
                note: 'Draft generated by AI agent',
                createdAt: new Date().toISOString()
              }
            ],
            createdAt: new Date().toISOString()
          };

          setCurrentDraftApplication(newDraft);
          setApplications(prev => [newDraft, ...prev.filter(a => a.id !== draftAppId)]);

          const assistantMsg: Message = {
            id: `msg-asst-${Date.now()}`,
            chatId: currentChatId,
            role: 'assistant',
            content: `${result.reply}\n\n\`\`\`text\n${result.draft_content}\n\`\`\``,
            contentType: 'application_draft',
            createdAt: new Date().toISOString(),
            applicationDraftId: draftAppId
          };

          setMessagesMap(prev => ({
            ...prev,
            [currentChatId]: [...(prev[currentChatId] || []), assistantMsg]
          }));
          setIsStreaming(false);
          return;
        }

        const assistantMsg: Message = {
          id: `msg-asst-${Date.now()}`,
          chatId: currentChatId,
          role: 'assistant',
          content: result.reply || result.message || "Please provide the requested details.",
          contentType: 'text',
          createdAt: new Date().toISOString()
        };

        setMessagesMap(prev => ({
          ...prev,
          [currentChatId]: [...(prev[currentChatId] || []), assistantMsg]
        }));
        setIsStreaming(false);

      } else {
        const isDiscovery = /suggest\s+students|find\s+teammates|show\s+students|skilled\s+in|hackathons|developers|collaborators/i.test(text);

        if (isDiscovery && currentUser) {
          let discoveryCards: any[] = [];
          try {
            discoveryCards = await apiClient.getStudentDiscovery(text);
          } catch (_) {
            const localRes = searchStudents(text, currentUser.id);
            discoveryCards = localRes.cards;
          }

          const assistantMsg: Message = {
            id: `msg-asst-${Date.now()}`,
            chatId: currentChatId,
            role: 'assistant',
            content: `I found **${discoveryCards.length} student${discoveryCards.length === 1 ? '' : 's'}** matching your criteria:`,
            contentType: discoveryCards.length > 0 ? 'profile_cards' : 'text',
            createdAt: new Date().toISOString(),
            profileCards: discoveryCards
          };

          setMessagesMap(prev => ({
            ...prev,
            [currentChatId]: [...(prev[currentChatId] || []), assistantMsg]
          }));
          setIsStreaming(false);
        } else {
          try {
            let convId = currentChatId;
            if (convId.startsWith('chat-')) {
              const newConv = await apiClient.createConversation(activeChat?.title || 'New Conversation', 'general');
              convId = newConv.id;
            }
            const res = await apiClient.sendChatMessageV1(convId, text);
            const asst = res.assistantMessage;

            const assistantMsg: Message = {
              id: asst.id,
              chatId: currentChatId,
              role: 'assistant',
              content: asst.content,
              contentType: 'text',
              createdAt: asst.createdAt || new Date().toISOString(),
              sources: asst.sources || [],
              widget: asst.widget || undefined
            };

            setMessagesMap(prev => ({
              ...prev,
              [currentChatId]: [...(prev[currentChatId] || []), assistantMsg]
            }));
          } catch (backendErr) {
            const ragRes = executeRAGQuery(text);
            const assistantMsg: Message = {
              id: `msg-asst-${Date.now()}`,
              chatId: currentChatId,
              role: 'assistant',
              content: ragRes.answer,
              contentType: 'text',
              createdAt: new Date().toISOString(),
              sources: ragRes.sources
            };

            setMessagesMap(prev => ({
              ...prev,
              [currentChatId]: [...(prev[currentChatId] || []), assistantMsg]
            }));
          }
          setIsStreaming(false);
        }
      }
    } catch (err: any) {
      console.error('Chat error:', err);
      setIsStreaming(false);
    }
  };

  // Application Actions
  const updateApplicationContent = (appId: string, newContent: string) => {
    setApplications(prev => prev.map(a => {
      if (a.id === appId && a.status === 'draft') {
        const newVer = {
          id: `v-${Date.now()}`,
          versionNo: a.versions.length + 1,
          content: newContent,
          createdBy: 'student' as const,
          createdAt: new Date().toISOString()
        };
        return {
          ...a,
          content: newContent,
          currentVersionId: newVer.id,
          versions: [...a.versions, newVer]
        };
      }
      return a;
    }));

    if (currentDraftApplication?.id === appId) {
      setCurrentDraftApplication(prev => prev ? { ...prev, content: newContent } : null);
    }
  };

  const shareApplicationToProfessor = (appId: string, facultyId: string): boolean => {
    const prof = MITS_FACULTY.find(f => f.facultyId === facultyId);
    if (!prof) return false;

    setApplications(prev => prev.map(a => {
      if (a.id === appId) {
        return {
          ...a,
          facultyId: prof.facultyId,
          facultyName: prof.name,
          facultyDepartment: prof.department,
          status: 'sent',
          sentAt: new Date().toISOString(),
          statusHistory: [
            ...a.statusHistory,
            {
              id: `sh-${Date.now()}`,
              fromStatus: 'draft',
              toStatus: 'sent',
              actorUserId: currentUser?.id || 'usr-student',
              actorName: currentUser?.fullName || 'Student',
              note: `Sent to ${prof.name} (${prof.department})`,
              createdAt: new Date().toISOString()
            }
          ]
        };
      }
      return a;
    }));

    // Create notification for professor
    const newNotif: NotificationItem = {
      id: `notif-${Date.now()}`,
      userId: prof.facultyId,
      type: 'application_received',
      title: 'New Application Received',
      body: `${currentUser?.fullName || 'A student'} shared a new application: "${currentDraftApplication?.title || 'Formal Request'}".`,
      readAt: null,
      createdAt: new Date().toISOString(),
      applicationId: appId
    };
    setNotifications(prev => [newNotif, ...prev]);

    // Mark application chat as completed
    if (currentChatId) {
      setChats(prev => prev.map(c => c.id === currentChatId ? { ...c, status: 'completed' } : c));
    }

    setCurrentDraftApplication(null);
    return true;
  };

  const decideApplication = (appId: string, decision: 'approved' | 'rejected', note?: string): boolean => {
    const targetApp = applications.find(a => a.id === appId);
    if (!targetApp) return false;
    if (targetApp.status === 'approved' || targetApp.status === 'rejected') {
      return false; // Immutable once decided
    }

    setApplications(prev => prev.map(a => {
      if (a.id === appId) {
        return {
          ...a,
          status: decision,
          decidedAt: new Date().toISOString(),
          decisionNote: note || (decision === 'approved' ? 'Approved as requested.' : 'Declined as per academic policy.'),
          statusHistory: [
            ...a.statusHistory,
            {
              id: `sh-${Date.now()}`,
              fromStatus: a.status,
              toStatus: decision,
              actorUserId: currentUser?.id || 'usr-fac',
              actorName: currentUser?.fullName || 'Faculty Reviewer',
              note: note || `Application ${decision}`,
              createdAt: new Date().toISOString()
            }
          ]
        };
      }
      return a;
    }));

    // Create notification for student
    const studentNotif: NotificationItem = {
      id: `notif-dec-${Date.now()}`,
      userId: targetApp.studentId,
      type: decision === 'approved' ? 'application_approved' : 'application_rejected',
      title: decision === 'approved' ? 'Application Approved' : 'Application Rejected',
      body: `${currentUser?.fullName || 'Faculty'} has ${decision} your application: "${targetApp.title}".${note ? ` Note: "${note}"` : ''}`,
      readAt: null,
      createdAt: new Date().toISOString(),
      applicationId: appId
    };
    setNotifications(prev => [studentNotif, ...prev]);

    return true;
  };

  const deleteDraftApplication = (appId: string) => {
    setApplications(prev => prev.filter(a => a.id !== appId || a.status !== 'draft'));
  };

  // Student Profile Updates
  const updateStudentProfile = (updates: Partial<StudentProfile>) => {
    if (!currentStudentProfile) return;

    const updated = {
      ...currentStudentProfile,
      ...updates,
      updatedAt: new Date().toISOString()
    };

    // Recalculate completeness score
    let score = 30; // base for identity
    if (updated.bio && updated.bio.length > 20) score += 15;
    if (updated.skills && updated.skills.length >= 3) score += 15;
    if (updated.lookingFor) score += 10;
    if (updated.projects && updated.projects.length > 0) score += 15;
    if (updated.githubUrl || updated.linkedinUrl) score += 10;
    if (updated.resumeFileName) score += 5;

    updated.completenessScore = Math.min(100, score);

    setCurrentStudentProfile(updated);
    setProfileSaveIndicator(true);
    setTimeout(() => setProfileSaveIndicator(false), 2000);
  };

  // Notifications
  const markNotificationAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, readAt: new Date().toISOString() } : n));
  };

  const markAllNotificationsAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, readAt: new Date().toISOString() })));
  };

  const unreadNotificationCount = notifications.filter(n => !n.readAt && (currentUser ? n.userId === currentUser.id || currentUser.role === 'faculty' : false)).length;

  const chatMessages = currentChatId ? messagesMap[currentChatId] || [] : [];

  return (
    <AppContext.Provider
      value={{
        currentUser,
        setCurrentUser,
        currentStudentProfile,
        setCurrentStudentProfile,
        activeView,
        setActiveView,
        loginAs,
        logout,
        authError,
        clearAuthError,
        sidebarCollapsed,
        setSidebarCollapsed,
        chats,
        currentChatId,
        setCurrentChatId,
        chatMessages,
        isStreaming,
        stopStreaming,
        sendMessage,
        createNewChat,
        deleteChat,
        renameChat,
        setMessageFeedback,
        applications,
        selectedApplicationId,
        setSelectedApplicationId,
        currentDraftApplication,
        updateApplicationContent,
        shareApplicationToProfessor,
        decideApplication,
        deleteDraftApplication,
        updateStudentProfile,
        profileSaveIndicator,
        notifications,
        unreadNotificationCount,
        markNotificationAsRead,
        markAllNotificationsAsRead,
        facultyList: MITS_FACULTY,
        selectedFaculty,
        setSelectedFaculty,
        previewStudentCard,
        setPreviewStudentCard
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
