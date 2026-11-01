import { FacultyProfile } from '../types';

export const MITS_FACULTY: FacultyProfile[] = [
  {
    facultyId: 'fac-1',
    name: 'Dr. Manish Dixit',
    designation: 'Professor & Head of Department',
    department: 'Computer Science & Engineering',
    qualification: 'Ph.D. (Computer Engineering), M.Tech (CSE), B.E. (CSE)',
    researchAreas: ['Cloud Computing', 'Artificial Intelligence', 'Machine Learning', 'Big Data Analytics'],
    publications: [
      {
        title: 'Optimized Resource Scheduling in Hybrid Cloud Architectures using Metaheuristic Algorithms',
        journal: 'IEEE Transactions on Cloud Computing',
        year: 2024,
        doi: '10.1109/TCC.2024.3129841'
      },
      {
        title: 'Deep Transfer Learning Framework for Edge IoT Health Monitoring',
        journal: 'ACM Transactions on Internet of Things',
        year: 2023,
        doi: '10.1145/3547219'
      },
      {
        title: 'Fault-Tolerant Distributed Storage in Decentralized Systems',
        journal: 'Journal of Systems and Software, Elsevier',
        year: 2022
      }
    ],
    emailPublic: 'manish.dixit@mitsgwalior.in',
    phonePublic: '+91-751-2409391',
    officeLocation: 'Room 102, Ground Floor, Department of CSE, Academic Block B',
    officeHours: 'Monday – Friday, 3:00 PM – 5:00 PM',
    photoUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
    bio: 'Dr. Manish Dixit brings over 22 years of academic and administrative experience. He serves as HOD Computer Science & Engineering and has guided 9 Ph.D. scholars in cloud workload allocation, federated learning, and scalable systems.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/manish-dixit',
    contentHash: 'hash_cse_md_09871',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  },
  {
    facultyId: 'fac-2',
    name: 'Dr. Akhilesh Tiwari',
    designation: 'Professor',
    department: 'Computer Science & Engineering',
    qualification: 'Ph.D. (CSE), M.E. (CSE), B.E. (CSE)',
    researchAreas: ['Data Mining', 'Machine Learning', 'Web Mining', 'Predictive Analytics'],
    publications: [
      {
        title: 'Sequential Pattern Mining on High-Dimensional Temporal Datasets',
        journal: 'Data & Knowledge Engineering, Elsevier',
        year: 2024
      },
      {
        title: 'Privacy Preserving Association Rule Mining in Distributed Environments',
        journal: 'Springer Knowledge and Information Systems',
        year: 2023
      }
    ],
    emailPublic: 'akhilesh.tiwari@mitsgwalior.in',
    phonePublic: '+91-751-2409395',
    officeLocation: 'Room 205, First Floor, CSE Building',
    officeHours: 'Tuesday & Thursday, 2:00 PM – 4:00 PM',
    photoUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80',
    bio: 'Senior professor with extensive research in data algorithms, knowledge extraction, and predictive models. Chief Coordinator for National Knowledge Network (NKN) at MITS.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/akhilesh-tiwari',
    contentHash: 'hash_cse_at_09872',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  },
  {
    facultyId: 'fac-3',
    name: 'Dr. Karuna Markam',
    designation: 'Associate Professor',
    department: 'Computer Science & Engineering',
    qualification: 'Ph.D. (Computer Science), M.Tech (CSE)',
    researchAreas: ['Internet of Things (IoT)', 'Distributed Systems', 'Wireless Sensor Networks'],
    publications: [
      {
        title: 'Energy Efficient Clustering Protocol for Smart Agriculture WSNs',
        journal: 'IEEE Sensors Journal',
        year: 2024
      },
      {
        title: 'Blockchain Enabled Trust Verification in Heterogeneous IoT Networks',
        journal: 'Computers & Security',
        year: 2023
      }
    ],
    emailPublic: 'karuna.markam@mitsgwalior.in',
    phonePublic: '+91-751-2409398',
    officeLocation: 'Room 208, First Floor, CSE Building',
    officeHours: 'Wednesday & Friday, 11:00 AM – 1:00 PM',
    photoUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80',
    bio: 'Associate Professor passionate about distributed sensor architectures, embedded computing, and mentoring student projects in smart campus IoT implementations.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/karuna-markam',
    contentHash: 'hash_cse_km_09873',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  },
  {
    facultyId: 'fac-4',
    name: 'Dr. Sanjeev Sharma',
    designation: 'Professor & Head of Department',
    department: 'Information Technology',
    qualification: 'Ph.D. (IT), M.Tech (IT), B.E. (Computer Engineering)',
    researchAreas: ['Network Security', 'Mobile Ad-hoc Networks', 'Cryptography', 'Cloud Forensics'],
    publications: [
      {
        title: 'Zero-Knowledge Proof Authentication for Decentralized Identity Schemes',
        journal: 'IEEE Transactions on Dependable and Secure Computing',
        year: 2024
      }
    ],
    emailPublic: 'sanjeev.sharma@mitsgwalior.in',
    phonePublic: '+91-751-2409380',
    officeLocation: 'IT Block, Room 101, Ground Floor',
    officeHours: 'Monday to Thursday, 2:30 PM – 4:30 PM',
    photoUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80',
    bio: 'Head of Information Technology. Author of three textbooks on Network Security and Cryptography. Faculty advisor for ACM Student Chapter.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/sanjeev-sharma',
    contentHash: 'hash_it_ss_09874',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  },
  {
    facultyId: 'fac-5',
    name: 'Prof. Vikas Sejwar',
    designation: 'Assistant Professor',
    department: 'Computer Science & Engineering',
    qualification: 'M.Tech (CSE), B.E. (CSE)',
    researchAreas: ['Full Stack Web Technologies', 'Cross-Platform Mobile Apps (Flutter)', 'Software Engineering'],
    publications: [
      {
        title: 'Microservices vs Monoliths: Benchmarking Web Performance in High-Concurrency Indian E-Governance',
        journal: 'Springer Lecture Notes in Computer Science',
        year: 2023
      }
    ],
    emailPublic: 'vikas.sejwar@mitsgwalior.in',
    phonePublic: '+91-751-2409399',
    officeLocation: 'Room 304, Second Floor, Software Development Lab',
    officeHours: 'Daily 4:00 PM – 5:30 PM',
    photoUrl: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80',
    bio: 'Faculty lead for Coding Club MITS and mentor for Smart India Hackathon finalist teams. Teaches Full Stack Development, Flutter, and Database Management.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/vikas-sejwar',
    contentHash: 'hash_cse_vs_09875',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  },
  {
    facultyId: 'fac-6',
    name: 'Dr. P. K. Singhal',
    designation: 'Dean Academics & Senior Professor',
    department: 'Electronics & Communication Engineering',
    qualification: 'Ph.D. (ECE), M.E. (Microwave Engg)',
    researchAreas: ['Microwave Engineering', 'Antenna Design', 'Wireless Communication', 'Optical Systems'],
    publications: [
      {
        title: 'Metamaterial Inspired Ultra-Wideband Antenna for Satellite Subsystems',
        journal: 'IEEE Antennas and Wireless Propagation Letters',
        year: 2024
      }
    ],
    emailPublic: 'dean.academics@mitsgwalior.in',
    phonePublic: '+91-751-2409302',
    officeLocation: 'Dean Office, Administrative Wing, Ground Floor',
    officeHours: 'Monday – Friday, 11:30 AM – 1:30 PM',
    photoUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80',
    bio: 'Dean Academics at MITS Gwalior. Oversees academic ordinances, curriculum formulation, and NOC approvals for internships and research exchange programs.',
    sourceUrl: 'https://web.mitsgwalior.in/faculty/pk-singhal',
    contentHash: 'hash_ece_pks_09876',
    lastSyncedAt: '2026-10-28T02:00:00Z'
  }
];

export function searchFaculty(query: string, department?: string): FacultyProfile[] {
  const q = query.trim().toLowerCase();
  return MITS_FACULTY.filter(fac => {
    const matchesDept = !department || department === 'All' || fac.department.toLowerCase().includes(department.toLowerCase());
    if (!matchesDept) return false;
    if (!q) return true;
    return (
      fac.name.toLowerCase().includes(q) ||
      fac.designation.toLowerCase().includes(q) ||
      fac.department.toLowerCase().includes(q) ||
      fac.researchAreas.some(area => area.toLowerCase().includes(q))
    );
  });
}
