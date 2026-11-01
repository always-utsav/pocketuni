export type UserRole = 'student' | 'faculty' | 'super_admin';

export interface User {
  id: string;
  googleSub: string;
  email: string;
  role: UserRole;
  activeContext?: UserRole;
  fullName: string;
  pictureUrl: string;
  isActive: boolean;
  lastLoginAt: string;
  // Student specific identity
  rollNumber?: string;
  enrolmentNumber?: string;
  programme?: string;
  branch?: string;
  batch?: string;
  semester?: number;
  section?: string;
  academicYear?: string;
  yearOfStudy?: number;
  graduationYear?: number;
  // Faculty specific
  facultyIdentifier?: string;
  departmentId?: string;
  departmentName?: string;
  centre?: string;
  designation?: string;
  is_demo?: boolean;
}

export interface InstitutionalPortal {
  id: string;
  name: string;
  category: string;
  officialUrl: string;
  domain: string;
  purpose: string;
  servicesDescription?: string;
  authRequired: boolean;
  integrationStatus: string;
  lastVerifiedAt?: string;
}

export interface RosterBatch {
  id: string;
  entity_type: string;
  file_name: string;
  status: string;
  total_records: number;
  successful_records: number;
  failed_records: number;
  created_at?: string;
}

export interface RosterSyncJob {
  id: string;
  entity_type: string;
  user_email: string;
  status: string;
  retry_count: number;
  last_error?: string;
  created_at?: string;
  completed_at?: string;
}

export type SkillProficiency = 'Beginner' | 'Intermediate' | 'Advanced';

export interface StudentSkill {
  id: string;
  name: string;
  proficiency: SkillProficiency;
  category?: string;
}

export interface StudentProject {
  id: string;
  title: string;
  description: string;
  repoUrl?: string;
  liveUrl?: string;
  techNotes: string[];
}

export interface StudentExperience {
  id: string;
  title: string;
  organization: string;
  startDate: string;
  endDate?: string;
  summary: string;
}

export interface StudentCertification {
  id: string;
  name: string;
  issuer: string;
  issuedYear: number;
  credentialUrl?: string;
}

export interface CompetitiveHandles {
  leetcode?: string;
  codeforces?: string;
  codechef?: string;
  github?: string;
}

export interface StudentProfile {
  studentId: string;
  bio: string;
  lookingFor: string;
  openForHackathons: boolean;
  openSourceContributor: boolean;
  competitiveProgramming: boolean;
  competitiveHandles: CompetitiveHandles;
  githubUrl: string;
  linkedinUrl: string;
  portfolioUrl: string;
  resumeFileName?: string;
  resumeFileSize?: string;
  resumeUploadedAt?: string;
  availabilityHoursPerWeek: number;
  availabilityNotes: string;
  preferredRoles: string[];
  clubs: string[];
  skills: StudentSkill[];
  techStack: string[];
  interests: string[];
  domains: string[];
  projects: StudentProject[];
  experiences: StudentExperience[];
  certifications: StudentCertification[];
  profileVisible: boolean;
  completenessScore: number;
  updatedAt: string;
}

export interface FacultyPublication {
  title: string;
  journal: string;
  year: number;
  doi?: string;
}

export interface FacultyProfile {
  facultyId: string;
  name: string;
  designation: string;
  department: string;
  qualification: string;
  researchAreas: string[];
  publications: FacultyPublication[];
  emailPublic: string;
  phonePublic?: string;
  officeLocation: string;
  officeHours: string;
  photoUrl: string;
  bio: string;
  sourceUrl: string;
  contentHash: string;
  lastSyncedAt: string;
  isMentor?: boolean;
  verificationStatus?: string;
}

export type ChatKind = 'general' | 'application_agent';
export type ChatStatus = 'active' | 'completed' | 'archived';

export interface MessageSource {
  title: string;
  category: string;
  url: string;
  snippet: string;
  rank: number;
  score: number;
}

export interface StudentMatchCard {
  studentId: string;
  name: string;
  email: string;
  pictureUrl: string;
  branch: string;
  year: number;
  rollNumber?: string;
  bio: string;
  matchedTags: string[];
  topSkills: string[];
  openForHackathons: boolean;
  preferredRoles: string[];
  githubUrl?: string;
  linkedinUrl?: string;
}

export interface Message {
  id: string;
  chatId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contentType: 'text' | 'application_draft' | 'profile_cards';
  createdAt: string;
  sources?: MessageSource[];
  profileCards?: StudentMatchCard[];
  applicationDraftId?: string;
  feedback?: 1 | -1 | null;
  isIncomplete?: boolean;
}

export interface Chat {
  id: string;
  userId: string;
  title: string;
  kind: ChatKind;
  status: ChatStatus;
  applicationId?: string;
  agentState?: any;
  createdAt: string;
  lastMessageAt: string;
}

export type ApplicationType =
  | 'leave'
  | 'bonafide'
  | 'permission'
  | 'noc'
  | 'fee'
  | 'general';

export type ApplicationStatus = 'draft' | 'sent' | 'approved' | 'rejected';

export interface ApplicationVersion {
  id: string;
  versionNo: number;
  content: string;
  createdBy: 'ai' | 'student';
  createdAt: string;
}

export interface ApplicationStatusHistory {
  id: string;
  fromStatus: ApplicationStatus | 'created';
  toStatus: ApplicationStatus;
  actorUserId: string;
  actorName: string;
  note?: string;
  createdAt: string;
}

export interface Application {
  id: string;
  studentId: string;
  studentName: string;
  studentEmail: string;
  studentRollNumber: string;
  studentBranch: string;
  studentYear: number;
  facultyId?: string;
  facultyName?: string;
  facultyDepartment?: string;
  chatId: string;
  title: string;
  type: ApplicationType;
  status: ApplicationStatus;
  currentVersionId: string;
  content: string;
  versions: ApplicationVersion[];
  statusHistory: ApplicationStatusHistory[];
  createdAt: string;
  sentAt?: string;
  decidedAt?: string;
  decisionNote?: string;
}

export interface NotificationItem {
  id: string;
  userId: string;
  type: 'application_received' | 'application_approved' | 'application_rejected' | 'system';
  title: string;
  body: string;
  readAt?: string | null;
  createdAt: string;
  applicationId?: string;
}
