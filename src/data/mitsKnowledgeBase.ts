export interface KnowledgeChunk {
  id: string;
  url: string;
  title: string;
  category: 'Academics' | 'Departments' | 'Placements' | 'Clubs' | 'Notices' | 'Hostels' | 'Facilities' | 'Administration';
  headingPath: string;
  content: string;
  keywords: string[];
  lastModified: string;
}

export const MITS_KNOWLEDGE_BASE: KnowledgeChunk[] = [
  {
    id: 'kb-1',
    url: 'https://web.mitsgwalior.in/about/overview',
    title: 'MITS Gwalior — Institute Overview & Accreditations',
    category: 'Administration',
    headingPath: 'About MITS > Institute Profile',
    content: `Madhav Institute of Technology & Science (MITS), Gwalior, established in 1957 by His Highness Sir Jiwaji Rao Scindia, is a premier autonomous government-aided technical institution in Madhya Pradesh, India. The institute is accredited with NAAC Grade 'A++' and NBA tier-1 accreditation across major engineering branches. It offers undergraduate (B.Tech), postgraduate (M.Tech, MBA, MCA), and doctoral (Ph.D.) programs affiliated with RGPV Bhopal.`,
    keywords: ['mits gwalior', 'established 1957', 'naac a++', 'autonomous', 'history', 'scindia', 'rgpv', 'ranking', 'about'],
    lastModified: '2026-08-15'
  },
  {
    id: 'kb-2',
    url: 'https://web.mitsgwalior.in/academics/regulations',
    title: 'Academic Regulations, Attendance Policy & Grading System',
    category: 'Academics',
    headingPath: 'Academics > Ordinance & Attendance Rules',
    content: `Under MITS Autonomous CBCS (Choice Based Credit System):
1. Minimum 75% attendance in theory and practical classes is strictly mandatory to appear in End-Semester Examinations.
2. A relaxation of up to 10% may be granted by the Director upon recommendation of HOD only for valid medical reasons or sanctioned college representation.
3. Medical certificates must be submitted to the respective Department Office within 3 working days of resumption of classes.
4. Grading is based on a 10-point scale: O (10), A+ (9), A (8), B+ (7), B (6), C (5), P (4), F (0). SGPA and CGPA are calculated at the end of each semester.`,
    keywords: ['attendance', '75 percent', 'medical leave', 'grading', 'cbcs', 'sgpa', 'cgpa', 'ordinance', 'rules', 'exam eligibility', 'shortage'],
    lastModified: '2026-09-01'
  },
  {
    id: 'kb-3',
    url: 'https://web.mitsgwalior.in/training-and-placement',
    title: 'Training and Placement Cell (T&P) — Drives, Statistics & Recruiter Guidelines',
    category: 'Placements',
    headingPath: 'Placements > Placement Drives & Statistics',
    content: `The Training & Placement Cell of MITS Gwalior coordinates on-campus recruitment drives, industry internships, and soft-skill workshops:
- Placement drives for 2026-27 commence in August for final year (7th semester) students, with pre-placement talks beginning in July.
- Top hiring partners: TCS (Digital & Ninja), Infosys, Wipro, Cognizant, Accenture, Amazon, Zscaler, Persistent Systems, L&T, Schneider Electric, and Crompton Greaves.
- Placement statistics: Highest domestic package offered is 42.5 LPA (Amazon), highest international package is 1.02 Crore; average CTC across CSE & IT is 7.2 LPA.
- Eligibility: Minimum 60% or 6.5 CGPA throughout 10th, 12th, and B.Tech with no active backlogs for marquee and dream tier companies.`,
    keywords: ['placement', 't&p', 'package', 'highest package', 'average package', 'companies', 'recruiters', 'amazon', 'tcs', 'internships', 'eligibility', 'drive dates'],
    lastModified: '2026-10-10'
  },
  {
    id: 'kb-4',
    url: 'https://web.mitsgwalior.in/departments/computer-science-and-engineering',
    title: 'Department of Computer Science & Engineering (CSE)',
    category: 'Departments',
    headingPath: 'Departments > Computer Science & Engineering',
    content: `The Department of Computer Science & Engineering at MITS Gwalior is headed by Dr. Manish Dixit. The department offers B.Tech in CSE, AI & Machine Learning, Data Science, and M.Tech in Information Technology.
- Facilities: High-Performance Computing (HPC) Lab, Cloud Computing & AI Research Centre, NVIDIA GPU workstation clusters, and IoT Innovation Cell.
- Key Faculty: Dr. Manish Dixit (Professor & Head, Cloud & AI), Dr. Akhilesh Tiwari (Professor, Data Mining), Dr. Karuna Markam (Associate Professor, IoT & Distributed Systems), Dr. Jamvant Singh Kumare (Associate Professor, Cyber Security).
- Location: CSE Department Complex, Academic Block B.`,
    keywords: ['cse', 'computer science', 'manish dixit', 'hod cse', 'akhilesh tiwari', 'labs', 'hpc', 'department', 'ai', 'cloud', 'faculty'],
    lastModified: '2026-09-20'
  },
  {
    id: 'kb-5',
    url: 'https://web.mitsgwalior.in/departments/information-technology',
    title: 'Department of Information Technology (IT)',
    category: 'Departments',
    headingPath: 'Departments > Information Technology',
    content: `The Department of Information Technology is headed by Dr. Sanjeev Sharma. The department specializes in Software Engineering, Computer Networks, Mobile Computing, and Distributed Databases.
- Labs: Advanced Web Development Lab, Network Security Lab, and Open Source Software Lab.
- Student activities: ACM Student Chapter, Smart India Hackathon mentoring, and weekly technical colloquiums.
- Location: IT Block, Ground & 1st Floor.`,
    keywords: ['it department', 'information technology', 'sanjeev sharma', 'hod it', 'network lab', 'acm', 'software engineering'],
    lastModified: '2026-09-18'
  },
  {
    id: 'kb-6',
    url: 'https://web.mitsgwalior.in/student-life/clubs',
    title: 'Student Technical & Cultural Clubs at MITS',
    category: 'Clubs',
    headingPath: 'Campus Life > Student Clubs & Societies',
    content: `Active student societies and technical clubs at MITS Gwalior:
1. Coding Club MITS: Conducts hackathons, DSA bootcamps, and annual 'Gwalior Hacks'.
2. Google Developer Student Clubs (GDSC MITS): Focuses on Android, Flutter, Cloud, and Web technologies.
3. IEEE Student Branch MITS: Organizes technical symposiums, research paper writing seminars, and industrial visits.
4. Robotics Club MITS: Autonomous rovers, line-follower competitions, and drone prototyping in the Mechanical & ECE robotics lab.
5. Team Roobaroo (SAE India): Automotive engineering team building BAJA ATVs and Formula Student race cars.
6. Spic Macay & Rotaract Club: Cultural heritage events, blood donation camps, and community service.`,
    keywords: ['clubs', 'coding club', 'gdsc', 'ieee', 'robotics club', 'roobaroo', 'sae', 'rotaract', 'hackathon', 'events', 'activities'],
    lastModified: '2026-09-25'
  },
  {
    id: 'kb-7',
    url: 'https://web.mitsgwalior.in/administration/dean-and-hods',
    title: 'Key Institute Administrators & Dean Contacts',
    category: 'Administration',
    headingPath: 'Administration > Institute Authorities',
    content: `Key administrative officers at MITS Gwalior:
- Director: Dr. R. K. Pandit (Office: Administrative Block)
- Dean Academics: Dr. P. K. Singhal (Handles curriculum, academic disputes, ordinances, and semester schedules)
- Dean Student Welfare (DSW): Dr. C. S. Malvi (Oversees clubs, student activities, discipline, anti-ragging, and hostels)
- Controller of Examination (CoE): Dr. Sanjeev Khanna (End-semester examinations, grade cards, degree certificates)
- Training & Placement Officer: Dr. Vikram Rajput (Campus recruitment drives, internships, corporate MoUs)
- Chief Warden Hostels: Prof. R. R. Singh (Hostel allocations, mess management, outstation leaves).`,
    keywords: ['director', 'pandit', 'dean academics', 'singhal', 'dsw', 'dean student welfare', 'malvi', 'controller of exam', 'tpo', 'contact', 'officials', 'hod'],
    lastModified: '2026-10-01'
  },
  {
    id: 'kb-8',
    url: 'https://web.mitsgwalior.in/student-services/applications-procedure',
    title: 'Official Procedure for Student Applications, NOC & Bonafide Letters',
    category: 'Academics',
    headingPath: 'Student Services > Applications & Certificates',
    content: `Official procedural rules for student requests:
1. Bonafide Certificate: Submit request to Academic Section or through PocketUni Application Agent. Requires mention of purpose (bank loan, passport, scholarship, bus pass). Processing timeline: 2 to 3 working days.
2. No Objection Certificate (NOC) for Internship: Requires offer letter from the hiring company specifying dates and stipend, recommendation of Class Coordinator, and sign-off by HOD & Dean Academics.
3. Event/Lab/Hall Permission: Must specify event name, exact dates/time, venue (Audi 1, SAC, Seminar Hall A), faculty mentor, and estimated number of participants. Submit at least 5 working days in advance to Dean Student Welfare / HOD.
4. Leave Application: Submit to Class Coordinator / HOD with explicit start date, end date, reason, and missed subject names.`,
    keywords: ['bonafide', 'noc', 'leave application', 'permission', 'letter format', 'procedure', 'how to apply', 'academic section', 'documents required'],
    lastModified: '2026-10-05'
  },
  {
    id: 'kb-9',
    url: 'https://web.mitsgwalior.in/campus/hostels-and-amenities',
    title: 'Hostel Facilities, Mess Timings & Outing Regulations',
    category: 'Hostels',
    headingPath: 'Campus Amenities > Hostels & Mess Rules',
    content: `MITS Hostel Guidelines:
- Boys Hostels: Hostel No. 1, 2, 3, and 4.
- Girls Hostels: Kalpana Chawla Bhawan and Mother Teresa Bhawan.
- Gate Timings: In-time for all hostels is strictly 8:00 PM (Winter) and 8:30 PM (Summer).
- Leave passes: Outstation night stay requires digital warden pass and prior verification with registered parents' phone number.
- Amenities: 24/7 Wi-Fi (NKN 1 Gbps lease line), water coolers with RO purification, indoor badminton and table tennis, gym, and 24-hour medical attendant.`,
    keywords: ['hostel', 'gate timing', 'warden', 'girls hostel', 'boys hostel', 'mess', 'outing pass', 'rules', 'facilities', 'wifi'],
    lastModified: '2026-08-30'
  },
  {
    id: 'kb-10',
    url: 'https://web.mitsgwalior.in/facilities/central-library',
    title: 'Central Library — Book Bank, Timings & Digital Resources',
    category: 'Facilities',
    headingPath: 'Facilities > Central Library',
    content: `The MITS Central Library is a 3-storey air-conditioned facility housing over 1,20,000 volumes:
- Hours: Mon-Sat 8:00 AM to 10:00 PM; Reading room open 24/7 during mid-term and end-semester exams.
- Digital Library: 40 terminal setups with access to IEEE Xplore, ScienceDirect, SpringerLink, ASME, and DELNET.
- Book Bank Scheme: SC/ST and economically disadvantaged students receive free textbooks for full semester duration. Standard issue limit: 4 books for 15 days for UG students.`,
    keywords: ['library', 'books', 'book bank', 'ieee xplore', 'timings', 'reading room', 'fine', 'digital library'],
    lastModified: '2026-09-12'
  }
];
