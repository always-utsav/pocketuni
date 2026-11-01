import React, { useState } from 'react';
import { useApp } from './context/AppContext';
import { LandingPage } from './components/LandingPage';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { ChatView } from './components/ChatView';
import { ApplicationAgentChat } from './components/ApplicationAgentChat';
import { ApplicationListView } from './components/ApplicationListView';
import { ApplicationDetailView } from './components/ApplicationDetailView';
import { StudentProfileView } from './components/StudentProfileView';
import { FacultyProfileView } from './components/FacultyProfileView';
import { FacultyDirectoryView } from './components/FacultyDirectoryView';
import { StudentPreviewModal } from './components/StudentPreviewModal';
import { SuperAdminDashboardView } from './components/SuperAdminDashboardView';

export const App: React.FC = () => {
  const {
    currentUser,
    activeView,
    previewStudentCard,
    setPreviewStudentCard
  } = useApp();

  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // If no user is logged in or activeView is landing, show the Landing Page
  if (!currentUser || activeView === 'landing') {
    return <LandingPage />;
  }

  const renderActiveView = () => {
    switch (activeView) {
      case 'chat':
        return <ChatView />;
      case 'application_agent_chat':
        return <ApplicationAgentChat />;
      case 'applications_list':
        return <ApplicationListView />;
      case 'application_detail':
        return <ApplicationDetailView />;
      case 'profile':
        return currentUser.role === 'faculty' ? <FacultyProfileView /> : <StudentProfileView />;
      case 'faculty_directory':
        return <FacultyDirectoryView />;
      case 'super_admin_dashboard':
        return <SuperAdminDashboardView />;
      default:
        return <ChatView />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-brand-surface font-sans text-brand-primary">
      {/* Collapsible Role-Gated Sidebar */}
      <Sidebar
        mobileOpen={mobileSidebarOpen}
        setMobileOpen={setMobileSidebarOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden">
        {/* Sticky Header Navbar */}
        <Navbar onOpenMobileSidebar={() => setMobileSidebarOpen(true)} />

        {/* Dynamic Screen View */}
        <main className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
          {renderActiveView()}
        </main>
      </div>

      {/* Campus Student Preview Modal */}
      {previewStudentCard && (
        <StudentPreviewModal
          card={previewStudentCard}
          onClose={() => setPreviewStudentCard(null)}
        />
      )}
    </div>
  );
};

export default App;
