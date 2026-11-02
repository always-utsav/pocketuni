import React, { useState, useEffect } from 'react';
import { Search, Mail, Phone, MapPin, ExternalLink, ChevronRight, GraduationCap, Loader2 } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { MITS_FACULTY, searchFaculty } from '../data/facultyData';
import { FacultyProfile } from '../types';
import { apiClient } from '../services/apiClient';

export const FacultyDirectoryView: React.FC = () => {
  const { setSelectedFaculty, setActiveView } = useApp();

  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('All');
  const [facultyList, setFacultyList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const departments = [
    { label: 'All Departments', value: 'All' },
    { label: 'Centre for AI (CAI)', value: 'CAI' },
    { label: 'Computer Science (CSE)', value: 'CSE' },
    { label: 'Internet of Things (IoT)', value: 'IoT' }
  ];

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const deptParam = departmentFilter === 'All' ? undefined : departmentFilter;
    const searchParam = searchQuery.trim() || undefined;

    apiClient.getFacultyDirectory(deptParam, searchParam)
      .then((data) => {
        if (!cancelled && Array.isArray(data) && data.length > 0) {
          const mapped = data.map((d: any) => ({
            facultyId: d.facultyId || d.id,
            name: d.name,
            designation: d.designation,
            department: d.department,
            emailPublic: d.emailPublic || d.email,
            phonePublic: d.phonePublic || '',
            officeLocation: d.officeLocation || 'Academic Block',
            photoUrl: d.photoUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
            qualification: d.qualification || 'Ph.D.',
            researchAreas: d.areasOfExpertise || [],
            professionalHighlights: d.professionalHighlights || [],
            externalLinks: d.externalLinks || {},
            publications: d.publications || []
          }));
          setFacultyList(mapped);
        } else if (!cancelled) {
          // Fallback to local data
          const localList = searchFaculty(
            searchQuery,
            departmentFilter === 'All' ? undefined : departmentFilter
          );
          setFacultyList(localList);
        }
      })
      .catch(() => {
        if (!cancelled) {
          const localList = searchFaculty(
            searchQuery,
            departmentFilter === 'All' ? undefined : departmentFilter
          );
          setFacultyList(localList);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [searchQuery, departmentFilter]);

  const handleSelectFaculty = async (fac: any) => {
    try {
      const full = await apiClient.getFacultyProfile(fac.facultyId);
      if (full) {
        setSelectedFaculty({
          facultyId: full.facultyId || fac.facultyId,
          name: full.name || fac.name,
          designation: full.designation || fac.designation,
          department: full.department || fac.department,
          emailPublic: full.emailPublic || fac.emailPublic,
          phonePublic: full.phonePublic || fac.phonePublic || '',
          officeLocation: full.officeLocation || fac.officeLocation || 'Academic Block',
          officeHours: full.officeHours || 'Mon, Wed, Fri: 03:00 PM - 05:00 PM',
          photoUrl: full.photoUrl || fac.photoUrl,
          qualification: full.qualification || fac.qualification || 'Ph.D.',
          bio: full.bio || `${full.name || fac.name} is a faculty member in ${full.department || fac.department} at MITS Gwalior.`,
          researchAreas: full.areasOfExpertise || fac.researchAreas || [],
          professionalHighlights: full.professionalHighlights || fac.professionalHighlights || [],
          externalLinks: full.externalLinks || fac.externalLinks || {},
          publications: full.publications || [],
          sourceUrl: full.sourceUrl || 'https://web.mitsgwalior.in',
          lastSyncedAt: full.lastSyncedAt || new Date().toISOString()
        });
        setActiveView('profile');
        return;
      }
    } catch (_) {}

    setSelectedFaculty(fac);
    setActiveView('profile');
  };

  return (
    <div className="flex-1 overflow-y-auto bg-brand-surface/40 p-4 sm:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="pb-4 border-b border-brand-border/60">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-brand-accent" />
            <h2 className="font-heading font-bold text-2xl text-brand-primary tracking-tight">
              MITS Faculty Directory
            </h2>
          </div>
          <p className="text-xs text-brand-muted mt-1">
            Official public faculty profiles synchronized with Madhav Institute of Technology & Science, Gwalior (CAI, CSE, IoT).
          </p>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-brand-muted" />
            <input
              type="text"
              placeholder="Search by professor name, designation, research topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl border border-brand-border bg-white shadow-subtle focus:outline-none focus:border-brand-accent"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {departments.map((dept) => (
              <button
                key={dept.value}
                onClick={() => setDepartmentFilter(dept.value)}
                className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  departmentFilter === dept.value
                    ? 'bg-brand-primary text-white shadow-subtle'
                    : 'bg-white border border-brand-border text-brand-muted hover:text-brand-primary'
                }`}
              >
                {dept.label}
              </button>
            ))}
          </div>
        </div>

        {/* Faculty Grid */}
        {loading ? (
          <div className="p-12 flex flex-col items-center justify-center text-center">
            <Loader2 className="w-8 h-8 text-brand-accent animate-spin mb-3" />
            <p className="text-xs text-brand-muted">Loading verified faculty records...</p>
          </div>
        ) : facultyList.length === 0 ? (
          <div className="p-12 rounded-2xl bg-white border border-brand-border text-center space-y-2">
            <p className="text-sm font-semibold text-brand-primary">No faculty members found</p>
            <p className="text-xs text-brand-muted">Try adjusting your search query or department filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {facultyList.map((fac) => (
              <div
                key={fac.facultyId}
                onClick={() => handleSelectFaculty(fac)}
                className="bg-white rounded-2xl border border-brand-border p-5 shadow-subtle hover:shadow-card hover:border-brand-accent/50 transition-all cursor-pointer group text-left flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start gap-4">
                    <img
                      src={fac.photoUrl}
                      alt={fac.name}
                      className="w-14 h-14 rounded-2xl object-cover border border-brand-borderSubtle shadow-sm shrink-0"
                    />
                    <div className="space-y-0.5 min-w-0 flex-1">
                      <h3 className="font-heading font-bold text-sm text-brand-primary group-hover:text-brand-accent transition-colors truncate">
                        {fac.name}
                      </h3>
                      <p className="text-xs font-medium text-brand-secondary truncate">
                        {fac.designation}
                      </p>
                      <p className="text-[11px] text-brand-muted truncate">
                        {fac.department}
                      </p>
                    </div>
                  </div>

                  {/* Highlights / Research tags */}
                  {fac.professionalHighlights && fac.professionalHighlights.length > 0 ? (
                    <div className="mt-3.5 pt-3 border-t border-brand-borderSubtle text-[11px] text-brand-muted">
                      <p className="line-clamp-2">
                        ⭐ {fac.professionalHighlights[0]}
                      </p>
                    </div>
                  ) : fac.researchAreas && fac.researchAreas.length > 0 ? (
                    <div className="mt-3.5 pt-3 border-t border-brand-borderSubtle flex flex-wrap gap-1">
                      {fac.researchAreas.slice(0, 3).map((area: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-brand-surface text-brand-muted border border-brand-border"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>

                <div className="mt-4 pt-3 border-t border-brand-borderSubtle flex items-center justify-between text-[11px]">
                  <span className="text-brand-muted flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-brand-accent" />
                    {fac.officeLocation}
                  </span>
                  <span className="text-brand-accent font-semibold flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
                    View Profile
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
