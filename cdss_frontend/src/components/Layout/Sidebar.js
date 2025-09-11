import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  UserGroupIcon,
  PillIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserIcon,
  XMarkIcon,
  BuildingOfficeIcon,
  BeakerIcon,
  HeartIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const Sidebar = ({ isOpen, onClose, user }) => {
  const location = useLocation();
  const { logout } = useAuth();

  const navigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: HomeIcon,
      roles: ['admin', 'doctor', 'pharmacist', 'patient'],
    },
    {
      name: 'Patients',
      href: '/patients',
      icon: UserGroupIcon,
      roles: ['admin', 'doctor'],
    },
    {
      name: 'Drugs',
      href: '/drugs',
      icon: PillIcon,
      roles: ['admin', 'pharmacist'],
    },
    {
      name: 'Prescriptions',
      href: '/prescriptions',
      icon: ClipboardDocumentListIcon,
      roles: ['admin', 'doctor', 'pharmacist'],
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: ChartBarIcon,
      roles: ['admin', 'doctor', 'pharmacist'],
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Cog6ToothIcon,
      roles: ['admin'],
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: UserIcon,
      roles: ['admin', 'doctor', 'pharmacist', 'patient'],
    },
  ];

  const mlFeatures = [
    {
      name: 'Symptom Analysis',
      href: '/symptoms',
      icon: BeakerIcon,
      roles: ['admin', 'doctor'],
      description: 'AI-powered symptom analysis',
    },
    {
      name: 'Drug Interactions',
      href: '/drug-interactions',
      icon: ExclamationTriangleIcon,
      roles: ['admin', 'doctor', 'pharmacist'],
      description: 'Check drug interactions',
    },
    {
      name: 'Compliance Monitoring',
      href: '/compliance',
      icon: HeartIcon,
      roles: ['admin', 'doctor', 'pharmacist'],
      description: 'Patient medication adherence',
    },
    {
      name: 'Demand Forecasting',
      href: '/forecasting',
      icon: ChartBarIcon,
      roles: ['admin', 'pharmacist'],
      description: 'Drug demand predictions',
    },
  ];

  const filteredNavigation = navigation.filter(item =>
    item.roles.includes(user?.role)
  );

  const filteredMLFeatures = mlFeatures.filter(item =>
    item.roles.includes(user?.role)
  );

  const handleLogout = async () => {
    await logout();
  };

  const sidebarVariants = {
    open: { x: 0 },
    closed: { x: '-100%' },
  };

  return (
    <>
      {/* Mobile sidebar */}
      <motion.div
        className="lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-strong"
        variants={sidebarVariants}
        initial="closed"
        animate={isOpen ? "open" : "closed"}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-neutral-200">
            <div className="flex items-center">
              <BuildingOfficeIcon className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-neutral-900">CDSS</span>
            </div>
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-lg text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {/* Main Navigation */}
            <div className="mb-6">
              <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                Main Navigation
              </h3>
              <div className="space-y-1">
                {filteredNavigation.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      onClick={onClose}
                      className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                    >
                      <item.icon className="h-5 w-5 mr-3" />
                      {item.name}
                    </NavLink>
                  );
                })}
              </div>
            </div>

            {/* ML Features */}
            {filteredMLFeatures.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                  AI Features
                </h3>
                <div className="space-y-1">
                  {filteredMLFeatures.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <NavLink
                        key={item.name}
                        to={item.href}
                        onClick={onClose}
                        className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                        title={item.description}
                      >
                        <item.icon className="h-5 w-5 mr-3" />
                        {item.name}
                      </NavLink>
                    );
                  })}
                </div>
              </div>
            )}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-neutral-200">
            <div className="flex items-center mb-3">
              <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                <UserIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-neutral-900">{user?.name || 'User'}</p>
                <p className="text-xs text-neutral-500 capitalize">{user?.role || 'Unknown'}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 text-sm font-medium text-neutral-600 rounded-lg hover:bg-neutral-100 hover:text-neutral-900 transition-colors duration-150"
            >
              Sign out
            </button>
          </div>
        </div>
      </motion.div>

      {/* Desktop sidebar */}
      <div className="hidden lg:block fixed inset-y-0 left-0 z-40 w-64 bg-white shadow-strong">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center p-6 border-b border-neutral-200">
            <BuildingOfficeIcon className="h-8 w-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-neutral-900">CDSS</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {/* Main Navigation */}
            <div className="mb-6">
              <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                Main Navigation
              </h3>
              <div className="space-y-1">
                {filteredNavigation.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                    >
                      <item.icon className="h-5 w-5 mr-3" />
                      {item.name}
                    </NavLink>
                  );
                })}
              </div>
            </div>

            {/* ML Features */}
            {filteredMLFeatures.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                  AI Features
                </h3>
                <div className="space-y-1">
                  {filteredMLFeatures.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <NavLink
                        key={item.name}
                        to={item.href}
                        className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                        title={item.description}
                      >
                        <item.icon className="h-5 w-5 mr-3" />
                        {item.name}
                      </NavLink>
                    );
                  })}
                </div>
              </div>
            )}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-neutral-200">
            <div className="flex items-center mb-3">
              <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                <UserIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-neutral-900">{user?.name || 'User'}</p>
                <p className="text-xs text-neutral-500 capitalize">{user?.role || 'Unknown'}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 text-sm font-medium text-neutral-600 rounded-lg hover:bg-neutral-100 hover:text-neutral-900 transition-colors duration-150"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;







