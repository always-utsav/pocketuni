import React, { useState } from 'react';
import { Search, Mail, Phone, MapPin, ExternalLink, ChevronRight, GraduationCap } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { MITS_FACULTY, searchFaculty } from '../data/facultyData';
import { FacultyProfile } from '../types';

export const FacultyDirectoryView: React.FC = () => {
  const { setSelectedFaculty, setActiveView } = useApp();

  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('All');

  const departments = [
    'All',
    'Computer Science & Engineering',
    'Information Technology',
    'Electronics & Communication Engineering'
  ];

  const facultyList = searchFaculty(
    searchQuery,
    departmentFilter === 'All' ? undefined : departmentFilter
  );

  const handleSelectFaculty = (fac: FacultyProfile) => {
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
            Official public faculty profiles synchronized with Madhav Institute of Technology & Science, Gwalior.
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
                key={dept}
                onClick={() => setDepartmentFilter(dept)}
                className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  departmentFilter === dept
                    ? 'bg-brand-primary text-white shadow-subtle'
                    : 'bg-white border border-brand-border text-brand-muted hover:text-brand-primary'
                }`}
              >
                {dept === 'All' ? 'All Departments' : dept.replace(' Engineering', '')}
              </button>
            ))}
          </div>
        </div>

        {/* Faculty Grid */}
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
                  <div className="min-w-0 flex-1">
                    <h3 className="font-heading font-semibold text-sm text-brand-primary group-hover:text-brand-accent transition-colors truncate">
                      {fac.name}
                    </h3>
                    <p className="text-xs font-medium text-brand-secondary mt-0.5">
                      {fac.designation}
                    </p>
                    <p className="text-[11px] text-brand-muted truncate">
                      {fac.department}
                    </p>
                  </div>
                </div>

                {/* Research Areas */}
                <div className="flex flex-wrap gap-1 mt-3">
                  {fac.researchAreas.slice(0, 3).map((area, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded text-[10px] font-medium bg-brand-surface border border-brand-borderSubtle text-brand-primary"
                    >
                      {area}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-4 pt-3 border-t border-brand-borderSubtle flex items-center justify-between text-[11px] text-brand-muted">
                <span className="truncate max-w-[200px]">{fac.emailPublic}</span>
                <span className="inline-flex items-center gap-1 font-semibold text-brand-secondary group-hover:text-brand-accent">
                  View Profile <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
