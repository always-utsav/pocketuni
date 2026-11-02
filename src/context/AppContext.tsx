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
import { realtimeClient } from '../services/realtimeClient';

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
  sandboxLogin: (role: 'SUPER_ADMIN' | 'STUDENT' | 'FACULTY') => Promise<boolean>;
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
  decideApplication: (appId: string, decision: 'approved' | 'rejected' | 'revision_requested', note?: string) => boolean;
  resubmitApplication: (appId: string, updatedContent: string) => boolean;
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
    const savedUser = localStorage.getItem('pocketuni_user');
    const u = savedUser ? JSON.parse(savedUser) : null;
    if (u?.id) {
      const saved = localStorage.getItem(`pocketuni_chats_${u.id}`);
      return saved ? JSON.parse(saved) : INITIAL_CHATS;
    }
    return INITIAL_CHATS;
  });

  const [currentChatId, setCurrentChatId] = useState<string | null>(() => {
    return chats.length > 0 ? chats[0].id : null;
  });

  const [messagesMap, setMessagesMap] = useState<Record<string, Message[]>>(() => {
    const savedUser = localStorage.getItem('pocketuni_user');
    const u = savedUser ? JSON.parse(savedUser) : null;
    if (u?.id) {
      const saved = localStorage.getItem(`pocketuni_messages_${u.id}`);
      return saved ? JSON.parse(saved) : INITIAL_MESSAGES;
    }
    return INITIAL_MESSAGES;
  });

  const [applications, setApplications] = useState<Application[]>(() => {
    const savedUser = localStorage.getItem('pocketuni_user');
    const u = savedUser ? JSON.parse(savedUser) : null;
    if (u?.id) {
      const saved = localStorage.getItem(`pocketuni_applications_${u.id}`);
      return saved ? JSON.parse(saved) : INITIAL_APPLICATIONS;
    }
    return INITIAL_APPLICATIONS;
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

  const abortStreamingRef = React.useRef<(() => void) | null>(null);

  // Sync to user-scoped localStorage & live WebSockets
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('pocketuni_user', JSON.stringify(currentUser));
      const token = apiClient.getToken();
      if (token) {
        realtimeClient.connect(token);
      }
    } else {
      localStorage.removeItem('pocketuni_user');
      realtimeClient.disconnect();
    }
  }, [currentUser]);

  // Load user-scoped conversations and applications upon login/switch
  useEffect(() => {
    if (!currentUser?.id) {
      setChats([]);
      setCurrentChatId(null);
      setMessagesMap({});
      setApplications([]);
      return;
    }

    const userChatKey = `pocketuni_chats_${currentUser.id}`;
    const userMsgKey = `pocketuni_messages_${currentUser.id}`;
    const userAppKey = `pocketuni_applications_${currentUser.id}`;

    const savedChats = localStorage.getItem(userChatKey);
    const parsedChats: Chat[] = savedChats ? JSON.parse(savedChats) : [];
    setChats(parsedChats);
    setCurrentChatId(parsedChats.length > 0 ? parsedChats[0].id : null);

    const savedMsgs = localStorage.getItem(userMsgKey);
    setMessagesMap(savedMsgs ? JSON.parse(savedMsgs) : {});

    const savedApps = localStorage.getItem(userAppKey);
    setApplications(savedApps ? JSON.parse(savedApps) : []);

    // Sync conversations from backend
    apiClient.getConversations().then(backendConvs => {
      if (backendConvs && Array.isArray(backendConvs) && backendConvs.length > 0) {
        const mappedChats: Chat[] = backendConvs.map(c => ({
          id: c.id,
          userId: currentUser.id,
          title: c.title,
          kind: (c.kind as any) || 'general',
          status: (c.status as any) || 'active',
          createdAt: c.createdAt,
          lastMessageAt: c.lastMessageAt || c.createdAt
        }));
        setChats(mappedChats);
        setCurrentChatId(prev => prev || mappedChats[0].id);
      }
    }).catch(() => {});

    // Sync applications from backend
    apiClient.listApplications().then(backendApps => {
      if (backendApps && Array.isArray(backendApps)) {
        setApplications(backendApps);
      }
    }).catch(() => {});

    // Subscribe to live WebSocket updates
    const refreshApps = () => {
      apiClient.listApplications().then(fresh => {
        if (fresh && Array.isArray(fresh)) setApplications(fresh);
      }).catch(() => {});
    };

    const unsubAppStatus = realtimeClient.subscribe('application_status_changed', (payload) => {
      console.log('[Realtime] Application status changed:', payload);
      refreshApps();
    });

    const unsubAppReceived = realtimeClient.subscribe('application_received', (payload) => {
      console.log('[Realtime] Application received:', payload);
      refreshApps();
    });

    const unsubAppDecision = realtimeClient.subscribe('application_decision_made', (payload) => {
      console.log('[Realtime] Application decision made:', payload);
      refreshApps();
    });

    const unsubStudentProfile = realtimeClient.subscribe('student_profile_updated', (payload) => {
      console.log('[Realtime] Student profile updated:', payload);
      if (payload && (payload.userId === currentUser?.id || payload.studentId === currentStudentProfile?.studentId)) {
        setCurrentUser(prev => prev ? {
          ...prev,
          fullName: payload.fullName || prev.fullName,
          branch: payload.branch || prev.branch,
          pictureUrl: payload.pictureUrl || prev.pictureUrl
        } : prev);
        setCurrentStudentProfile(prev => prev ? {
          ...prev,
          bio: payload.bio || prev.bio,
          updatedAt: new Date().toISOString()
        } : prev);
      }
    });

    const unsubFac = realtimeClient.subscribe('faculty_profile_updated', (payload) => {
      console.log('[Realtime] Faculty profile updated:', payload);
      if (payload && payload.userId === currentUser?.id) {
        setCurrentUser(prev => prev ? {
          ...prev,
          fullName: payload.name || prev.fullName,
          designation: payload.designation || prev.designation,
          departmentName: payload.department || prev.departmentName
        } : prev);
      }
    });

    return () => {
      unsubAppStatus();
      unsubAppReceived();
      unsubAppDecision();
      unsubStudentProfile();
      unsubFac();
    };
  }, [currentUser?.id]);

  // Load conversation messages from backend on chat switch
  useEffect(() => {
    if (!currentChatId || currentChatId.startsWith('chat-')) return;
    if (!messagesMap[currentChatId] || messagesMap[currentChatId].length === 0) {
      apiClient.getConversation(currentChatId).then(conv => {
        if (conv && conv.messages) {
          const loadedMsgs: Message[] = conv.messages.map((m: any) => ({
            id: m.id,
            chatId: conv.id,
            role: m.role,
            content: m.content,
            contentType: m.contentType || 'text',
            sources: m.sources || [],
            profileCards: m.profileCards || undefined,
            feedback: m.feedback || undefined,
            createdAt: m.createdAt
          }));
          setMessagesMap(prev => ({
            ...prev,
            [conv.id]: loadedMsgs
          }));
        }
      }).catch(() => {});
    }
  }, [currentChatId]);

  useEffect(() => {
    if (currentStudentProfile) {
      localStorage.setItem('pocketuni_profile', JSON.stringify(currentStudentProfile));
    }
  }, [currentStudentProfile]);

  useEffect(() => {
    localStorage.setItem('pocketuni_sidebar_collapsed', String(sidebarCollapsed));
  }, [sidebarCollapsed]);

  useEffect(() => {
    if (currentUser?.id) {
      localStorage.setItem(`pocketuni_chats_${currentUser.id}`, JSON.stringify(chats));
    }
  }, [chats, currentUser?.id]);

  useEffect(() => {
    if (currentUser?.id) {
      localStorage.setItem(`pocketuni_messages_${currentUser.id}`, JSON.stringify(messagesMap));
    }
  }, [messagesMap, currentUser?.id]);

  useEffect(() => {
    if (currentUser?.id) {
      localStorage.setItem(`pocketuni_applications_${currentUser.id}`, JSON.stringify(applications));
    }
  }, [applications, currentUser?.id]);

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

  const sandboxLogin = async (role: 'SUPER_ADMIN' | 'STUDENT' | 'FACULTY'): Promise<boolean> => {
    setAuthError(null);
    try {
      const res = await apiClient.sandboxLogin(role);
      const user = res.user;
      const appUser: User = {
        id: user.id,
        googleSub: `sandbox-sub-${user.id}`,
        email: user.email,
        role: user.role === 'SUPER_ADMIN' ? 'super_admin' : (user.role === 'FACULTY' ? 'faculty' : 'student'),
        fullName: user.full_name,
        pictureUrl: user.picture_url,
        isActive: true,
        lastLoginAt: new Date().toISOString(),
        branch: user.branch,
        departmentName: user.department_name,
        designation: user.designation,
        yearOfStudy: user.year_of_study
      };
      setCurrentUser(appUser);
      if (appUser.role === 'student') {
        const profRes = await apiClient.getMyStudentProfile().catch(() => null);
        if (profRes) setCurrentStudentProfile(profRes);
        setActiveView('chat');
      } else if (appUser.role === 'faculty') {
        setCurrentStudentProfile(null);
        setActiveView('chat');
      } else {
        setCurrentStudentProfile(null);
        setActiveView('super_admin_dashboard');
      }
      return true;
    } catch (err: any) {
      setAuthError(err.message || 'Sandbox login failed.');
      return false;
    }
  };

  const logout = () => {
    realtimeClient.disconnect();
    apiClient.logout().catch(() => {});
    setCurrentUser(null);
    setCurrentStudentProfile(null);
    setChats([]);
    setCurrentChatId(null);
    setMessagesMap({});
    setApplications([]);
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

    if (currentUser) {
      apiClient.createConversation(newChat.title, kind).then(res => {
        if (res?.id) {
          setChats(prev => prev.map(c => c.id === newChatId ? { ...c, id: res.id } : c));
          setCurrentChatId(res.id);
          setMessagesMap(prev => {
            const copy = { ...prev };
            copy[res.id] = copy[newChatId] || [];
            delete copy[newChatId];
            return copy;
          });
        }
      }).catch(() => {});
    }

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
    if (!id.startsWith('chat-')) {
      apiClient.deleteConversation(id).catch(() => {});
    }
  };

  const renameChat = (id: string, newTitle: string) => {
    setChats(prev => prev.map(c => c.id === id ? { ...c, title: newTitle } : c));
    if (!id.startsWith('chat-')) {
      apiClient.renameConversation(id, newTitle).catch(() => {});
    }
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
    apiClient.submitMessageFeedbackV1(messageId, feedback).catch(() => {});
  };

  const stopStreaming = () => {
    if (abortStreamingRef.current) {
      abortStreamingRef.current();
      abortStreamingRef.current = null;
    }
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
              try {
                const newConv = await apiClient.createConversation(activeChat?.title || 'New Conversation', 'general');
                convId = newConv.id;
                setChats(prev => prev.map(c => c.id === currentChatId ? { ...c, id: newConv.id } : c));
                setCurrentChatId(newConv.id);
              } catch (_) {}
            }

            const asstMsgId = `msg-asst-${Date.now()}`;
            const initialAsstMsg: Message = {
              id: asstMsgId,
              chatId: convId,
              role: 'assistant',
              content: '',
              contentType: 'text',
              createdAt: new Date().toISOString(),
              sources: []
            };

            setMessagesMap(prev => ({
              ...prev,
              [convId]: [...(prev[convId] || []), initialAsstMsg]
            }));

            let streamedText = '';
            const abortSSE = apiClient.streamChatMessage(convId, text, {
              onCitations: (citations) => {
                setMessagesMap(prev => {
                  const msgs = prev[convId] || [];
                  return {
                    ...prev,
                    [convId]: msgs.map(m => m.id === asstMsgId ? { ...m, sources: citations } : m)
                  };
                });
              },
              onWidget: (widget) => {
                setMessagesMap(prev => {
                  const msgs = prev[convId] || [];
                  return {
                    ...prev,
                    [convId]: msgs.map(m => m.id === asstMsgId ? { ...m, widget } : m)
                  };
                });
              },
              onDelta: (deltaToken) => {
                streamedText += deltaToken;
                setMessagesMap(prev => {
                  const msgs = prev[convId] || [];
                  return {
                    ...prev,
                    [convId]: msgs.map(m => m.id === asstMsgId ? { ...m, content: streamedText } : m)
                  };
                });
              },
              onDone: (info) => {
                if (info?.messageId) {
                  setMessagesMap(prev => {
                    const msgs = prev[convId] || [];
                    return {
                      ...prev,
                      [convId]: msgs.map(m => m.id === asstMsgId ? { ...m, id: info.messageId } : m)
                    };
                  });
                }
                setIsStreaming(false);
              },
              onError: async (err) => {
                console.warn('SSE stream fallback to REST:', err);
                try {
                  const res = await apiClient.sendChatMessageV1(convId, text);
                  const asst = res.assistantMessage;
                  setMessagesMap(prev => {
                    const msgs = prev[convId] || [];
                    return {
                      ...prev,
                      [convId]: msgs.map(m => m.id === asstMsgId ? {
                        ...m,
                        id: asst.id,
                        content: asst.content,
                        sources: asst.sources || [],
                        widget: asst.widget || undefined
                      } : m)
                    };
                  });
                } catch (restErr) {
                  const ragRes = executeRAGQuery(text);
                  setMessagesMap(prev => {
                    const msgs = prev[convId] || [];
                    return {
                      ...prev,
                      [convId]: msgs.map(m => m.id === asstMsgId ? {
                        ...m,
                        content: ragRes.answer,
                        sources: ragRes.sources
                      } : m)
                    };
                  });
                } finally {
                  setIsStreaming(false);
                }
              }
            });
            abortStreamingRef.current = abortSSE;
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
            setIsStreaming(false);
          }
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
    const prof = MITS_FACULTY.find(f => f.facultyId === facultyId) || {
      facultyId,
      name: 'Faculty Member',
      department: 'Centre for Artificial Intelligence & ECE'
    };

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

    // Trigger backend share
    (async () => {
      try {
        let targetId = appId;
        if (appId.startsWith('app-draft-')) {
          const app = applications.find(a => a.id === appId);
          if (app) {
            const created = await apiClient.createApplication({
              title: app.title,
              type: app.type,
              content: app.content,
              facultyId
            });
            targetId = created.id;
          }
        }
        await apiClient.shareApplication(targetId, facultyId);
      } catch (e) {
        console.warn('Backend shareApplication sync:', e);
      }
    })();

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

  const decideApplication = (appId: string, decision: 'approved' | 'rejected' | 'revision_requested', note?: string): boolean => {
    const targetApp = applications.find(a => a.id === appId);
    if (!targetApp) return false;
    if (targetApp.status === 'approved' || targetApp.status === 'rejected') {
      return false; // Immutable once finalized
    }

    setApplications(prev => prev.map(a => {
      if (a.id === appId) {
        return {
          ...a,
          status: decision,
          decidedAt: new Date().toISOString(),
          decisionNote: note || (
            decision === 'approved'
              ? 'Approved as requested.'
              : decision === 'rejected'
              ? 'Declined as per academic policy.'
              : 'Corrections requested. Please update and resubmit.'
          ),
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

    apiClient.decideApplication(appId, decision, note).catch((e) => {
      console.warn('Backend decideApplication sync:', e);
    });

    // Create notification for student
    const notifType = decision === 'approved' ? 'application_approved' : decision === 'rejected' ? 'application_rejected' : 'application_revision_requested';
    const notifTitle = decision === 'approved' ? 'Application Approved' : decision === 'rejected' ? 'Application Rejected' : 'Revision Requested';

    const studentNotif: NotificationItem = {
      id: `notif-dec-${Date.now()}`,
      userId: targetApp.studentId,
      type: notifType,
      title: notifTitle,
      body: `${currentUser?.fullName || 'Faculty'} has ${decision.replace('_', ' ')} your application: "${targetApp.title}".${note ? ` Note: "${note}"` : ''}`,
      readAt: null,
      createdAt: new Date().toISOString(),
      applicationId: appId
    };
    setNotifications(prev => [studentNotif, ...prev]);

    return true;
  };

  const resubmitApplication = (appId: string, updatedContent: string): boolean => {
    const targetApp = applications.find(a => a.id === appId);
    if (!targetApp) return false;

    const newVersion = {
      id: `v-${Date.now()}`,
      versionNo: targetApp.versions.length + 1,
      content: updatedContent,
      createdBy: 'student' as const,
      createdAt: new Date().toISOString()
    };

    setApplications(prev => prev.map(a => {
      if (a.id === appId) {
        return {
          ...a,
          content: updatedContent,
          status: 'sent',
          versions: [...a.versions, newVersion],
          sentAt: new Date().toISOString(),
          statusHistory: [
            ...a.statusHistory,
            {
              id: `sh-${Date.now()}`,
              fromStatus: 'revision_requested',
              toStatus: 'sent',
              actorUserId: currentUser?.id || 'usr-student',
              actorName: currentUser?.fullName || 'Student',
              note: 'Resubmitted with requested revisions',
              createdAt: new Date().toISOString()
            }
          ]
        };
      }
      return a;
    }));

    // Share to backend
    if (targetApp.facultyId) {
      apiClient.shareApplication(appId, targetApp.facultyId, 'Resubmitted with requested revisions').catch(() => {});
    }

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
        sandboxLogin,
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
        resubmitApplication,
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
