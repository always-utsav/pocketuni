import { INITIAL_STUDENTS, StudentWithUser } from '../data/studentData';
import { StudentMatchCard } from '../types';

export interface DiscoveryResult {
  naturalAnswer: string;
  cards: StudentMatchCard[];
  matchedCount: number;
}

export function searchStudents(query: string, currentUserId: string, allStudents: StudentWithUser[] = INITIAL_STUDENTS): DiscoveryResult {
  const q = query.toLowerCase();

  // Extract query intents & criteria
  const isHackathonQuery = /hackathon|compete|contest|event|sih|team/i.test(q);
  const isAI = /ai|ml|machine\s+learning|deep\s+learning|computer\s+vision|nlp|vision|pytorch/i.test(q);
  const isFlutter = /flutter|mobile|dart|android|ios/i.test(q);
  const isBackend = /backend|server|golang|go|docker|database|sql|api|cloud|devops/i.test(q);
  const isFrontend = /frontend|react|ui|ux|web|design|tailwind|css/i.test(q);
  const isRobotics = /robotics|robot|iot|embedded|hardware|ros|arduino/i.test(q);
  const isCP = /competitive|dsa|leetcode|codeforces|cp/i.test(q);

  // Filter candidates: visible, active, and not current user
  const candidates = allStudents.filter(s => s.user.isActive && s.profile.profileVisible && s.user.id !== currentUserId);

  const scored: { student: StudentWithUser; score: number; matchReasons: string[]; matchedTags: string[] }[] = [];

  for (const c of candidates) {
    let score = 0;
    const matchReasons: string[] = [];
    const matchedTags: string[] = [];

    const allSkills = c.profile.skills.map(s => s.name.toLowerCase());
    const allInterests = [...c.profile.interests, ...c.profile.domains, ...c.profile.techStack].map(t => t.toLowerCase());

    // Hackathon criteria
    if (isHackathonQuery && c.profile.openForHackathons) {
      score += 5;
      matchedTags.push('Open for Hackathons');
    }

    // AI / ML match
    if (isAI) {
      if (allSkills.some(s => ['python', 'pytorch', 'tensorflow', 'langchain', 'computer vision'].includes(s)) ||
          allInterests.some(i => i.includes('ai') || i.includes('machine learning') || i.includes('computer vision'))) {
        score += 8;
        matchedTags.push('AI/ML', 'PyTorch/Vision');
        matchReasons.push('Strong background in machine learning and computer vision');
      }
    }

    // Flutter / Mobile match
    if (isFlutter) {
      if (allSkills.includes('flutter') || allInterests.some(i => i.includes('mobile'))) {
        score += 8;
        matchedTags.push('Flutter', 'Mobile Dev');
        matchReasons.push('Cross-platform mobile development experience in Flutter');
      }
    }

    // Backend match
    if (isBackend) {
      if (allSkills.some(s => ['go (golang)', 'postgresql', 'docker', 'kubernetes', 'fastapi', 'node.js'].includes(s)) ||
          c.profile.preferredRoles.some(r => r.toLowerCase().includes('backend'))) {
        score += 8;
        matchedTags.push('Backend', 'Go / Cloud');
        matchReasons.push('Experienced in scalable backend architectures and Docker');
      }
    }

    // Frontend / UI match
    if (isFrontend) {
      if (allSkills.some(s => ['react', 'tailwind css', 'figma', 'typescript', 'next.js'].includes(s)) ||
          c.profile.preferredRoles.some(r => r.toLowerCase().includes('frontend') || r.toLowerCase().includes('design'))) {
        score += 7;
        matchedTags.push('Frontend', 'React / UI');
        matchReasons.push('Skilled in React, Tailwind CSS, and user interface craft');
      }
    }

    // Robotics match
    if (isRobotics) {
      if (allSkills.some(s => ['ros 2', 'embedded c / c++', 'arduino & stm32'].includes(s)) ||
          allInterests.some(i => i.includes('robotics') || i.includes('hardware'))) {
        score += 10;
        matchedTags.push('Robotics', 'ROS 2 / Embedded');
        matchReasons.push('Leadership experience in Robotics Club and autonomous systems');
      }
    }

    // Competitive Programming match
    if (isCP && c.profile.competitiveProgramming) {
      score += 7;
      matchedTags.push('Competitive Programming');
      matchReasons.push('Active on LeetCode/Codeforces with strong problem-solving skills');
    }

    // General keyword match in bio or lookingFor
    const bioText = (c.profile.bio + ' ' + c.profile.lookingFor).toLowerCase();
    const words = q.split(/\s+/).filter(w => w.length > 3);
    for (const w of words) {
      if (bioText.includes(w)) {
        score += 2;
        if (!matchedTags.includes(w)) matchedTags.push(w);
      }
    }

    // Base profile completeness weight
    score += (c.profile.completenessScore / 25);

    if (score > 2) {
      scored.push({
        student: c,
        score,
        matchReasons,
        matchedTags: Array.from(new Set(matchedTags))
      });
    }
  }

  // Sort descending by match score
  scored.sort((a, b) => b.score - a.score);

  if (scored.length === 0) {
    return {
      naturalAnswer: `I couldn't find any student profiles matching those specific criteria right now. You might try broadening your keywords (e.g. "React", "Python", "hackathons", or "backend") or checking back as more MITS peers update their profiles.`,
      cards: [],
      matchedCount: 0
    };
  }

  const topMatches = scored.slice(0, 4);

  // Generate natural language summary explaining each candidate
  let naturalAnswer = `I found **${topMatches.length} student${topMatches.length > 1 ? 's' : ''}** at MITS who fit what you're looking for:\n\n`;

  topMatches.forEach((item, index) => {
    const s = item.student;
    const skillsList = s.profile.skills.slice(0, 3).map(sk => sk.name).join(', ');
    naturalAnswer += `**${index + 1}. ${s.user.fullName}** (${s.user.branch}, Year ${s.user.yearOfStudy})\n` +
      `• **Key Skills**: ${skillsList}\n` +
      `• **Why they fit**: ${item.matchReasons.length > 0 ? item.matchReasons.join('. ') : s.profile.bio.substring(0, 90) + '...'}\n` +
      (s.profile.lookingFor ? `• *Looking for: "${s.profile.lookingFor}"*\n\n` : '\n');
  });

  const cards: StudentMatchCard[] = topMatches.map(item => {
    const s = item.student;
    return {
      studentId: s.user.id,
      name: s.user.fullName,
      email: s.user.email,
      pictureUrl: s.user.pictureUrl,
      branch: s.user.branch || 'Engineering',
      year: s.user.yearOfStudy || 2,
      rollNumber: s.user.rollNumber,
      bio: s.profile.bio,
      matchedTags: item.matchedTags.length > 0 ? item.matchedTags : s.profile.techStack.slice(0, 3),
      topSkills: s.profile.skills.slice(0, 4).map(sk => sk.name),
      openForHackathons: s.profile.openForHackathons,
      preferredRoles: s.profile.preferredRoles,
      githubUrl: s.profile.githubUrl,
      linkedinUrl: s.profile.linkedinUrl
    };
  });

  return {
    naturalAnswer,
    cards,
    matchedCount: topMatches.length
  };
}
