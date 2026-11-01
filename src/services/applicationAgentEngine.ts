import { ApplicationType, User } from '../types';

export interface ApplicationSlots {
  type: ApplicationType;
  // Common
  dates?: string;
  reason?: string;
  subjectMissed?: string;
  purpose?: string;
  copies?: string;
  deadline?: string;
  eventName?: string;
  venue?: string;
  participants?: string;
  organization?: string;
  details?: string;
}

export interface AgentStepResult {
  message: string;
  state: 'COLLECTING' | 'READY_TO_GENERATE' | 'GENERATED' | 'COMPLETED';
  slots: ApplicationSlots;
  generatedContent?: string;
  applicationTitle?: string;
}

export function detectApplicationType(input: string): ApplicationType {
  const text = input.toLowerCase();
  if (/leave|absence|sick|fever|medical|wedding|absent|home/i.test(text)) return 'leave';
  if (/bonafide|certificate|character|proof\s+of\s+study/i.test(text)) return 'bonafide';
  if (/noc|no\s+objection|internship|off-campus/i.test(text)) return 'noc';
  if (/permission|event|workshop|hackathon|hall|auditorium|sac|trip/i.test(text)) return 'permission';
  if (/fee|scholarship|concession|installment/i.test(text)) return 'fee';
  return 'general';
}

export function processAgentInput(
  userInput: string,
  currentSlots: ApplicationSlots | undefined,
  currentState: string,
  user: User
): AgentStepResult {
  const slots: ApplicationSlots = currentSlots ? { ...currentSlots } : { type: detectApplicationType(userInput) };

  // If newly starting
  if (!currentSlots || currentState === 'COLLECTING' && Object.keys(currentSlots).length <= 1) {
    const type = detectApplicationType(userInput);
    slots.type = type;

    // Check if initial user message already contained dates/reasons
    if (type === 'leave') {
      const dateMatch = userInput.match(/(\d+\s*(?:day|days|nov|dec|oct|jan|feb|mar|apr|may|to|\-))/i);
      if (dateMatch) slots.dates = dateMatch[0];
      if (/sick|fever|illness/i.test(userInput)) slots.reason = 'Viral fever & medical rest';
      if (/sister|brother|wedding|marriage/i.test(userInput)) slots.reason = "Attending sibling's wedding ceremony";
      if (/family/i.test(userInput)) slots.reason = 'Family emergency at hometown';

      if (!slots.dates) {
        return {
          message: `I'll help you draft a formal **Leave Application** for ${user.fullName} (${user.branch || 'CSE'}, Year ${user.yearOfStudy || 2}, Roll: ${user.rollNumber || '0901CS231001'}).\n\nCould you specify the **exact dates or duration** of your leave (e.g., Nov 3 to Nov 6), and the **primary reason**?`,
          state: 'COLLECTING',
          slots
        };
      } else if (!slots.reason) {
        return {
          message: `Got the dates: **${slots.dates}**. What is the **specific reason** for the leave (e.g., medical reasons, family function, or personal emergency)? Also mention if you'll miss any specific lab or exam.`,
          state: 'COLLECTING',
          slots
        };
      }
    } else if (type === 'bonafide') {
      if (/loan/i.test(userInput)) slots.purpose = 'Education Loan sanction';
      if (/passport/i.test(userInput)) slots.purpose = 'Passport Application verification';
      if (/scholarship/i.test(userInput)) slots.purpose = 'National / State Scholarship application';

      if (!slots.purpose) {
        return {
          message: `I'll draft a formal **Bonafide / Character Certificate Application** for ${user.fullName} (Roll: ${user.rollNumber || '0901CS231001'}).\n\nWhat is the **intended purpose** for this certificate (e.g. Education Loan, Passport, Scholarship, or Bus Pass)?`,
          state: 'COLLECTING',
          slots
        };
      }
    } else if (type === 'noc') {
      return {
        message: `I will prepare a formal **NOC (No Objection Certificate)** request for an internship.\n\nCould you share the **Company or Organization name**, the **duration/dates**, and any specific submission deadline?`,
        state: 'COLLECTING',
        slots
      };
    } else if (type === 'permission') {
      return {
        message: `Let's draft a **Campus Permission Letter**.\n\nWhat is the **name of the event or activity**, the **proposed date/time**, and the **venue** you require (e.g., Auditorium, Seminar Hall A, or SAC)?`,
        state: 'COLLECTING',
        slots
      };
    } else {
      return {
        message: `I'll help you prepare a formal academic application.\n\nWhat is the **main subject** and what specific request or outcome do you wish to present to the faculty authority?`,
        state: 'COLLECTING',
        slots
      };
    }
  }

  // Ongoing slot filling
  const text = userInput.trim();

  // Extract slots based on type
  if (slots.type === 'leave') {
    if (!slots.dates) {
      slots.dates = text;
      return {
        message: `Recorded dates: **${text}**.\n\nCould you please explain the **reason for leave** and note any specific subjects, labs, or class coordinators we should mention?`,
        state: 'COLLECTING',
        slots
      };
    } else if (!slots.reason) {
      slots.reason = text;
      // Now all required slots filled!
      return generateFormalLetter(slots, user);
    }
  } else if (slots.type === 'bonafide') {
    if (!slots.purpose) {
      slots.purpose = text;
      return {
        message: `Noted purpose: **${text}**.\n\nHow many copies do you need, and is there an urgent submission deadline?`,
        state: 'COLLECTING',
        slots
      };
    } else {
      slots.copies = text;
      return generateFormalLetter(slots, user);
    }
  } else if (slots.type === 'noc') {
    if (!slots.organization) {
      slots.organization = text;
      return {
        message: `Noted organization: **${text}**.\n\nWhat are the proposed start & end dates for this internship, and have you already received the formal offer letter?`,
        state: 'COLLECTING',
        slots
      };
    } else {
      slots.details = text;
      return generateFormalLetter(slots, user);
    }
  } else if (slots.type === 'permission') {
    if (!slots.eventName) {
      slots.eventName = text;
      return {
        message: `Event: **${text}**.\n\nWhat is the expected date, time, and venue (e.g., Seminar Hall, SAC Ground), and approximately how many students will participate?`,
        state: 'COLLECTING',
        slots
      };
    } else {
      slots.venue = text;
      return generateFormalLetter(slots, user);
    }
  }

  // Handle conversational revisions ("make it shorter", "add that I will submit medical cert")
  if (currentState === 'GENERATED' || currentState === 'READY_TO_GENERATE') {
    if (/short|brief|concise/i.test(text)) {
      return generateFormalLetter(slots, user, 'concise');
    }
    if (/medical|doctor|certificate/i.test(text)) {
      slots.reason = (slots.reason || '') + ' (Medical certificate and prescription attached)';
      return generateFormalLetter(slots, user, 'medical');
    }
    if (/date|reschedule|change/i.test(text)) {
      slots.dates = text;
      return generateFormalLetter(slots, user);
    }
    // Default revision
    slots.details = (slots.details ? slots.details + '. ' : '') + text;
    return generateFormalLetter(slots, user);
  }

  return generateFormalLetter(slots, user);
}

export function generateFormalLetter(
  slots: ApplicationSlots,
  user: User,
  variant?: 'concise' | 'medical' | 'default'
): AgentStepResult {
  const today = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  const studentName = user.fullName;
  const rollNumber = user.rollNumber || '0901CS231001';
  const branch = user.branch || 'Computer Science & Engineering';
  const year = user.yearOfStudy ? `${user.yearOfStudy}${getOrdinal(user.yearOfStudy)} Year` : '2nd Year';

  let subject = '';
  let body = '';
  let title = '';

  if (slots.type === 'leave') {
    title = `Leave Application (${slots.dates || 'Upcoming Days'})`;
    subject = `Subject: Application for Grant of Leave — Reg.`;
    const reasonText = slots.reason || 'unavoidable family circumstances';
    const datesText = slots.dates || 'the specified dates';

    if (variant === 'concise') {
      body = `Respected Sir/Madam,

I am writing to respectfully request leave of absence from ${datesText} owing to ${reasonText}.

I assure you that I will consult my peers to complete all classwork, lecture notes, and practical assignments missed during this period. I kindly request you to sanction my leave and excuse my absence.`;
    } else {
      body = `Respected Sir/Madam,

I am writing to formally bring to your kind notice that I will be unable to attend regular academic classes and laboratory sessions from ${datesText} due to ${reasonText}.

I have informed my class representative and fellow classmates regarding the schedule, and I undertake full responsibility to cover the missed curriculum, assignments, and practical experiments immediately upon my return. ${
        variant === 'medical' ? '\n\nI have enclosed the doctor\'s medical fitness certificate and prescription for your verification.' : ''
      }

Therefore, I earnestly request your good self to kindly sanction my leave for the aforementioned duration and grant attendance condonation as per institutional guidelines.`;
    }
  } else if (slots.type === 'bonafide') {
    title = `Bonafide Certificate Request (${slots.purpose || 'General Purpose'})`;
    subject = `Subject: Application for Issuance of Bonafide Certificate — Reg.`;
    const purposeText = slots.purpose || 'official administrative documentation';

    body = `Respected Sir/Madam,

I am a bona fide student of Madhav Institute of Technology & Science, Gwalior, currently pursuing my B.Tech degree in ${branch} (${year}).

I require an official Bonafide Certificate from the institution for the purpose of ${purposeText}. All my institutional dues and semester fee clearance are up to date with the Accounts section.

I kindly request your office to issue the certificate at your earliest convenience to facilitate my application process.`;
  } else if (slots.type === 'noc') {
    title = `NOC Request for Internship (${slots.organization || 'Corporate Internship'})`;
    subject = `Subject: Request for Issuance of No Objection Certificate (NOC) for Internship — Reg.`;
    const org = slots.organization || 'the designated corporate partner';

    body = `Respected Sir/Madam,

I am pleased to inform you that I have been offered a technical internship opportunity at ${org}.

To formalize my onboarding and comply with organization policies, I require a No Objection Certificate (NOC) from MITS Gwalior affirming that the institute has no objection to my participation during the internship period.

I will ensure that my academic deliverables, mid-semester assessments, and practical requirements are fulfilled without disruption. I request you to kindly issue the NOC.`;
  } else if (slots.type === 'permission') {
    title = `Permission Request: ${slots.eventName || 'Campus Activity'}`;
    subject = `Subject: Permission for Conducting ${slots.eventName || 'Technical Workshop'} — Reg.`;
    const venue = slots.venue || 'Campus Auditorium / Seminar Hall';

    body = `Respected Sir/Madam,

On behalf of our student group, I am writing to seek your kind permission to organize '${slots.eventName || 'Technical Workshop'}' at ${venue}.

The proposed session aims to impart practical exposure and industry skills to participating students. We will ensure discipline, adherence to campus protocols, and proper maintenance of institutional property throughout the program.

We humbly request your approval and sanction for the required venue and logistical support.`;
  } else {
    title = `Application regarding ${slots.details || 'Academic Request'}`;
    subject = `Subject: Application regarding Academic Matters — Reg.`;
    body = `Respected Sir/Madam,

I am writing to formally submit my request regarding ${slots.details || 'my academic schedule and departmental records'}.

I request your kind consideration and appropriate guidance on this matter. Thank you for your continued support.`;
  }

  const generatedContent = `Date: ${today}

To,
The Head of Department,
Department of ${branch},
Madhav Institute of Technology & Science (MITS),
Gwalior (M.P.) - 474005

${subject}

${body}

Thanking you.

Yours faithfully,

${studentName}
Roll Number: ${rollNumber}
Branch: ${branch}
Year of Study: ${year}
Madhav Institute of Technology & Science, Gwalior`;

  return {
    message: `I have generated your formal application below following MITS academic standards.\n\nYou can review it, click **Edit Application** to customize the wording, or click **Share to Professor** to send it directly to your faculty advisor for review.`,
    state: 'GENERATED',
    slots,
    generatedContent,
    applicationTitle: title
  };
}

function getOrdinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
}
