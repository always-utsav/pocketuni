import { StudentProfile, User } from '../types';

export interface StudentWithUser {
  user: User;
  profile: StudentProfile;
}

export const INITIAL_STUDENTS: StudentWithUser[] = [
  {
    user: {
      id: 'usr-aarav',
      googleSub: 'google-sub-aarav-001',
      email: 'aarav.sharma@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Aarav Sharma',
      pictureUrl: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-29T09:30:00Z',
      rollNumber: '0901CS231001',
      branch: 'Computer Science & Engineering',
      yearOfStudy: 2,
      graduationYear: 2027
    },
    profile: {
      studentId: 'usr-aarav',
      bio: '2nd-year CSE student at MITS Gwalior. Passionate about building fast web apps and mobile interfaces. Active in hackathons and open-source tooling.',
      lookingFor: 'Teammates for Smart India Hackathon 2026 and AI hackathons (need backend & ML folks).',
      openForHackathons: true,
      openSourceContributor: true,
      competitiveProgramming: true,
      competitiveHandles: {
        leetcode: 'aarav_mits',
        codeforces: 'aarav_codes',
        github: 'aaravsharma-mits'
      },
      githubUrl: 'https://github.com/aaravsharma-mits',
      linkedinUrl: 'https://linkedin.com/in/aarav-sharma-mits',
      portfolioUrl: 'https://aaravsharma.dev',
      resumeFileName: 'Aarav_Sharma_Resume_2026.pdf',
      resumeFileSize: '1.2 MB',
      resumeUploadedAt: '2026-10-15T14:20:00Z',
      availabilityHoursPerWeek: 18,
      availabilityNotes: 'Available weekday evenings (after 5 PM) and full weekends.',
      preferredRoles: ['Frontend Developer', 'Fullstack Developer', 'Mobile Developer'],
      clubs: ['Coding Club MITS', 'GDSC MITS'],
      skills: [
        { id: 'sk-1', name: 'React', proficiency: 'Advanced', category: 'Frontend' },
        { id: 'sk-2', name: 'TypeScript', proficiency: 'Advanced', category: 'Language' },
        { id: 'sk-3', name: 'Flutter', proficiency: 'Intermediate', category: 'Mobile' },
        { id: 'sk-4', name: 'Tailwind CSS', proficiency: 'Advanced', category: 'Frontend' },
        { id: 'sk-5', name: 'Next.js', proficiency: 'Intermediate', category: 'Framework' },
        { id: 'sk-6', name: 'Node.js', proficiency: 'Intermediate', category: 'Backend' }
      ],
      techStack: ['React', 'TypeScript', 'Tailwind CSS', 'Flutter', 'Next.js', 'PostgreSQL', 'Git'],
      interests: ['Web Development', 'Mobile Apps', 'Open Source', 'Hackathons', 'Design Systems'],
      domains: ['Web Development', 'Mobile Development'],
      projects: [
        {
          id: 'proj-1',
          title: 'CampusEase — MITS Lost & Found Portal',
          description: 'A real-time lost and found web app built with React and Supabase for MITS students.',
          repoUrl: 'https://github.com/aaravsharma-mits/campusease',
          liveUrl: 'https://campusease-mits.vercel.app',
          techNotes: ['React', 'Tailwind', 'Supabase', 'TypeScript']
        },
        {
          id: 'proj-2',
          title: 'Gwalior Transit Mobile App',
          description: 'Flutter cross-platform app showing local city bus routes and bus stand timings.',
          repoUrl: 'https://github.com/aaravsharma-mits/gwalior-transit',
          techNotes: ['Flutter', 'Dart', 'Google Maps API']
        }
      ],
      experiences: [
        {
          id: 'exp-1',
          title: 'Frontend Lead',
          organization: 'Coding Club MITS',
          startDate: '2025-08-01',
          summary: 'Organized Gwalior Hacks 2025, mentored 60+ junior students in React and modern CSS.'
        }
      ],
      certifications: [
        {
          id: 'cert-1',
          name: 'Meta Front-End Developer Professional Certificate',
          issuer: 'Coursera / Meta',
          issuedYear: 2025,
          credentialUrl: 'https://coursera.org/verify/meta-frontend'
        }
      ],
      profileVisible: true,
      completenessScore: 92,
      updatedAt: '2026-10-25T11:00:00Z'
    }
  },
  {
    user: {
      id: 'usr-meera',
      googleSub: 'google-sub-meera-002',
      email: 'meera.patel@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Meera Patel',
      pictureUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-29T10:15:00Z',
      rollNumber: '0901CS211045',
      branch: 'Computer Science & Engineering',
      yearOfStudy: 4,
      graduationYear: 2025
    },
    profile: {
      studentId: 'usr-meera',
      bio: 'Final-year CSE student focused on Deep Learning, Computer Vision, and Medical Image Analysis. Author of an IEEE student conference paper on retinal scan segmentation.',
      lookingFor: 'Research collaborators for an upcoming IEEE paper submission & ML engineers for joint projects.',
      openForHackathons: true,
      openSourceContributor: true,
      competitiveProgramming: false,
      competitiveHandles: {
        leetcode: 'meerap_ai',
        github: 'meera-patel-ai'
      },
      githubUrl: 'https://github.com/meera-patel-ai',
      linkedinUrl: 'https://linkedin.com/in/meera-patel-ai',
      portfolioUrl: 'https://meerapatel.ai',
      resumeFileName: 'Meera_Patel_CV.pdf',
      resumeFileSize: '850 KB',
      resumeUploadedAt: '2026-10-20T08:00:00Z',
      availabilityHoursPerWeek: 15,
      availabilityNotes: 'Weekdays after 4 PM; Sunday full day.',
      preferredRoles: ['ML Engineer', 'Research Assistant', 'Data Scientist'],
      clubs: ['IEEE Student Branch MITS'],
      skills: [
        { id: 'sk-m1', name: 'Python', proficiency: 'Advanced', category: 'Language' },
        { id: 'sk-m2', name: 'PyTorch', proficiency: 'Advanced', category: 'Framework' },
        { id: 'sk-m3', name: 'Computer Vision', proficiency: 'Advanced', category: 'Domain' },
        { id: 'sk-m4', name: 'OpenCV', proficiency: 'Intermediate', category: 'Library' },
        { id: 'sk-m5', name: 'Transformers / Hugging Face', proficiency: 'Intermediate', category: 'ML' }
      ],
      techStack: ['Python', 'PyTorch', 'OpenCV', 'FastAPI', 'Docker', 'Git'],
      interests: ['Artificial Intelligence', 'Computer Vision', 'Medical Imaging', 'Research'],
      domains: ['AI/ML', 'Research'],
      projects: [
        {
          id: 'proj-m1',
          title: 'RetinaNet-Segmentation',
          description: 'U-Net architecture with attention gates for automated microaneurysm detection in fundus scans.',
          repoUrl: 'https://github.com/meera-patel-ai/retinanet',
          techNotes: ['PyTorch', 'CUDA', 'OpenCV', 'Albumentations']
        }
      ],
      experiences: [
        {
          id: 'exp-m1',
          title: 'AI Research Intern',
          organization: 'IIT Indore AI Lab',
          startDate: '2025-05-15',
          endDate: '2025-07-30',
          summary: 'Worked on self-supervised contrastive learning for clinical radiographs.'
        }
      ],
      certifications: [
        {
          id: 'cert-m1',
          name: 'Deep Learning Specialization',
          issuer: 'DeepLearning.AI',
          issuedYear: 2024,
          credentialUrl: 'https://coursera.org/verify/deeplearning'
        }
      ],
      profileVisible: true,
      completenessScore: 96,
      updatedAt: '2026-10-26T18:00:00Z'
    }
  },
  {
    user: {
      id: 'usr-rohan',
      googleSub: 'google-sub-rohan-003',
      email: 'rohan.verma@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Rohan Verma',
      pictureUrl: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-28T16:00:00Z',
      rollNumber: '0901IT221088',
      branch: 'Information Technology',
      yearOfStudy: 3,
      graduationYear: 2026
    },
    profile: {
      studentId: 'usr-rohan',
      bio: '3rd-year IT student. Systems and backend engineer. Love Golang, high-performance APIs, Docker, and distributed caching.',
      lookingFor: 'Hackathon team needing solid backend/cloud infra engineer; also looking for open-source mentors.',
      openForHackathons: true,
      openSourceContributor: true,
      competitiveProgramming: true,
      competitiveHandles: {
        codeforces: 'rohan_cf_1780',
        leetcode: 'rohan_verma_99',
        github: 'rohan-verma-cloud'
      },
      githubUrl: 'https://github.com/rohan-verma-cloud',
      linkedinUrl: 'https://linkedin.com/in/rohan-verma-cloud',
      portfolioUrl: 'https://rohanverma.tech',
      resumeFileName: 'Rohan_Verma_Resume.pdf',
      resumeFileSize: '940 KB',
      resumeUploadedAt: '2026-10-18T10:30:00Z',
      availabilityHoursPerWeek: 20,
      availabilityNotes: 'Available 7 days a week after 6 PM.',
      preferredRoles: ['Backend Developer', 'DevOps / Cloud Engineer', 'System Architect'],
      clubs: ['Coding Club MITS'],
      skills: [
        { id: 'sk-r1', name: 'Go (Golang)', proficiency: 'Advanced', category: 'Backend' },
        { id: 'sk-r2', name: 'PostgreSQL', proficiency: 'Advanced', category: 'Database' },
        { id: 'sk-r3', name: 'Docker', proficiency: 'Advanced', category: 'DevOps' },
        { id: 'sk-r4', name: 'Kubernetes', proficiency: 'Intermediate', category: 'DevOps' },
        { id: 'sk-r5', name: 'FastAPI', proficiency: 'Intermediate', category: 'Backend' }
      ],
      techStack: ['Go', 'PostgreSQL', 'Docker', 'Redis', 'Kubernetes', 'FastAPI', 'gRPC'],
      interests: ['Backend Development', 'Cloud/DevOps', 'Distributed Systems', 'Databases'],
      domains: ['Web Development', 'Cloud/DevOps'],
      projects: [
        {
          id: 'proj-r1',
          title: 'Distributed Rate Limiter in Go',
          description: 'Token bucket and sliding window rate limiter backed by Redis clusters, handling 80k req/sec.',
          repoUrl: 'https://github.com/rohan-verma-cloud/go-limiter',
          techNotes: ['Go', 'Redis', 'Docker']
        }
      ],
      experiences: [],
      certifications: [
        {
          id: 'cert-r1',
          name: 'Docker Certified Associate',
          issuer: 'Docker Inc.',
          issuedYear: 2025
        }
      ],
      profileVisible: true,
      completenessScore: 88,
      updatedAt: '2026-10-27T12:00:00Z'
    }
  },
  {
    user: {
      id: 'usr-ananya',
      googleSub: 'google-sub-ananya-004',
      email: 'ananya.deshmukh@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Ananya Deshmukh',
      pictureUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-29T11:00:00Z',
      rollNumber: '0901AI231012',
      branch: 'Artificial Intelligence & Data Science',
      yearOfStudy: 2,
      graduationYear: 2027
    },
    profile: {
      studentId: 'usr-ananya',
      bio: '2nd-year AI & Data Science student. GDSC Lead. Passionate about GenAI, LLM orchestration, and NLP for regional Indian languages.',
      lookingFor: 'Collaborators for AI agents and RAG applications for campus problems.',
      openForHackathons: true,
      openSourceContributor: false,
      competitiveProgramming: false,
      competitiveHandles: {
        github: 'ananya-deshmukh-ai'
      },
      githubUrl: 'https://github.com/ananya-deshmukh-ai',
      linkedinUrl: 'https://linkedin.com/in/ananya-deshmukh-mits',
      portfolioUrl: '',
      availabilityHoursPerWeek: 16,
      availabilityNotes: 'Flexible hours, active in Google DSC lab.',
      preferredRoles: ['ML Engineer', 'Fullstack Developer', 'Product Manager'],
      clubs: ['GDSC MITS'],
      skills: [
        { id: 'sk-a1', name: 'Python', proficiency: 'Advanced', category: 'Language' },
        { id: 'sk-a2', name: 'LangChain & LlamaIndex', proficiency: 'Advanced', category: 'AI' },
        { id: 'sk-a3', name: 'FastAPI', proficiency: 'Intermediate', category: 'Backend' },
        { id: 'sk-a4', name: 'TensorFlow', proficiency: 'Intermediate', category: 'ML' }
      ],
      techStack: ['Python', 'FastAPI', 'LangChain', 'React', 'MongoDB'],
      interests: ['AI/ML', 'NLP', 'GenAI', 'Hackathons'],
      domains: ['AI/ML', 'Web Development'],
      projects: [],
      experiences: [],
      certifications: [],
      profileVisible: true,
      completenessScore: 82,
      updatedAt: '2026-10-28T09:00:00Z'
    }
  },
  {
    user: {
      id: 'usr-priya',
      googleSub: 'google-sub-priya-005',
      email: 'priya.nair@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Priya Nair',
      pictureUrl: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-27T19:00:00Z',
      rollNumber: '0901EC221054',
      branch: 'Electronics & Communication Engineering',
      yearOfStudy: 3,
      graduationYear: 2026
    },
    profile: {
      studentId: 'usr-priya',
      bio: 'Robotics Club Lead at MITS. Embedded systems enthusiast, ROS 2 explorer, PCB designer. Built autonomous terrain rovers for e-Yantra.',
      lookingFor: 'Teammates for national robotics competitions (e-Yantra & Robocon) with C++ and ROS experience.',
      openForHackathons: true,
      openSourceContributor: true,
      competitiveProgramming: false,
      competitiveHandles: {
        github: 'priyanair-robotics'
      },
      githubUrl: 'https://github.com/priyanair-robotics',
      linkedinUrl: 'https://linkedin.com/in/priya-nair-robotics',
      portfolioUrl: '',
      availabilityHoursPerWeek: 25,
      availabilityNotes: 'Daily at the Robotics Lab, SAC building.',
      preferredRoles: ['Hardware Engineer', 'Robotics Engineer', 'Embedded Developer'],
      clubs: ['Robotics Club MITS', 'IEEE Student Branch MITS'],
      skills: [
        { id: 'sk-p1', name: 'Embedded C / C++', proficiency: 'Advanced', category: 'Language' },
        { id: 'sk-p2', name: 'ROS 2', proficiency: 'Advanced', category: 'Robotics' },
        { id: 'sk-p3', name: 'Arduino & STM32', proficiency: 'Advanced', category: 'Hardware' },
        { id: 'sk-p4', name: 'KiCAD (PCB Design)', proficiency: 'Intermediate', category: 'Hardware' }
      ],
      techStack: ['C++', 'ROS 2', 'Python', 'STM32', 'Linux'],
      interests: ['Robotics', 'Hardware/IoT', 'Autonomous Vehicles'],
      domains: ['Robotics', 'Hardware/IoT'],
      projects: [],
      experiences: [],
      certifications: [],
      profileVisible: true,
      completenessScore: 85,
      updatedAt: '2026-10-28T14:30:00Z'
    }
  },
  {
    user: {
      id: 'usr-sneha',
      googleSub: 'google-sub-sneha-006',
      email: 'sneha.gupta@mitsgwl.ac.in',
      role: 'student',
      fullName: 'Sneha Gupta',
      pictureUrl: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=300&q=80',
      isActive: true,
      lastLoginAt: '2026-10-29T12:00:00Z',
      rollNumber: '0901CS231078',
      branch: 'Computer Science & Engineering',
      yearOfStudy: 2,
      graduationYear: 2027
    },
    profile: {
      studentId: 'usr-sneha',
      bio: 'UI/UX Designer and Frontend developer. I obsess over clean typography, smooth 60fps micro-interactions, and accessible web experiences.',
      lookingFor: 'Design collaboration on student-led projects and hackathon teams needing product & UI design.',
      openForHackathons: true,
      openSourceContributor: false,
      competitiveProgramming: false,
      competitiveHandles: {
        github: 'snehagupta-design'
      },
      githubUrl: 'https://github.com/snehagupta-design',
      linkedinUrl: 'https://linkedin.com/in/sneha-gupta-ui',
      portfolioUrl: 'https://snehagupta.design',
      availabilityHoursPerWeek: 15,
      availabilityNotes: 'Evenings and weekends.',
      preferredRoles: ['UI/UX Designer', 'Frontend Developer', 'Product Designer'],
      clubs: ['GDSC MITS'],
      skills: [
        { id: 'sk-s1', name: 'Figma', proficiency: 'Advanced', category: 'Design' },
        { id: 'sk-s2', name: 'React', proficiency: 'Intermediate', category: 'Frontend' },
        { id: 'sk-s3', name: 'Tailwind CSS', proficiency: 'Advanced', category: 'Frontend' },
        { id: 'sk-s4', name: 'User Research', proficiency: 'Intermediate', category: 'Design' }
      ],
      techStack: ['Figma', 'React', 'Tailwind CSS', 'Framer Motion'],
      interests: ['UI/UX Design', 'Web Development', 'Design Systems'],
      domains: ['Web Development', 'Design'],
      projects: [],
      experiences: [],
      certifications: [],
      profileVisible: true,
      completenessScore: 89,
      updatedAt: '2026-10-27T17:00:00Z'
    }
  }
];
