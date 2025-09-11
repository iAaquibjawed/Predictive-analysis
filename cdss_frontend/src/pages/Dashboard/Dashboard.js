import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { railsApi, mlApi } from '../../services/api';
import {
  UserGroupIcon,
  PillIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CurrencyPoundIcon,
} from '@heroicons/react/24/outline';
import StatCard from '../../components/Dashboard/StatCard';
import QuickActions from '../../components/Dashboard/QuickActions';
import RecentActivity from '../../components/Dashboard/RecentActivity';
import AlertsPanel from '../../components/Dashboard/AlertsPanel';
import ChartWidget from '../../components/Dashboard/ChartWidget';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [recentActivity, setRecentActivity] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);

        // Fetch role-specific data
        const promises = [];

        if (user?.role === 'admin' || user?.role === 'doctor') {
          promises.push(
            railsApi.patients.list({ limit: 5 }),
            railsApi.prescriptions.list({ limit: 5 })
          );
        }

        if (user?.role === 'admin' || user?.role === 'pharmacist') {
          promises.push(
            railsApi.drugs.list({ limit: 5 }),
            mlApi.forecasting.demand({ drugs: [] })
          );
        }

        if (user?.role === 'admin') {
          promises.push(
            railsApi.health(),
            mlApi.health()
          );
        }

        const results = await Promise.allSettled(promises);

        // Process results and set state
        const newStats = {};
        const newRecentActivity = [];
        const newAlerts = [];

        results.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            const data = result.value.data;

            if (index === 0 && (user?.role === 'admin' || user?.role === 'doctor')) {
              // Patients data
              newStats.totalPatients = data.total || data.length || 0;
              newRecentActivity.push(...(data.patients || data || []).slice(0, 3));
            }

            if (index === 1 && (user?.role === 'admin' || user?.role === 'doctor')) {
              // Prescriptions data
              newStats.totalPrescriptions = data.total || data.length || 0;
              newRecentActivity.push(...(data.prescriptions || data || []).slice(0, 3));
            }

            if (index === 2 && (user?.role === 'admin' || user?.role === 'pharmacist')) {
              // Drugs data
              newStats.totalDrugs = data.total || data.length || 0;
            }

            if (index === 3 && (user?.role === 'admin' || user?.role === 'pharmacist')) {
              // Forecasting data
              newStats.forecastAccuracy = data.accuracy || 0;
            }
          }
        });

        // Mock data for demo purposes
        if (Object.keys(newStats).length === 0) {
          newStats.totalPatients = 1247;
          newStats.totalPrescriptions = 8923;
          newStats.totalDrugs = 456;
          newStats.forecastAccuracy = 94.2;
          newStats.complianceRate = 87.5;
          newStats.criticalAlerts = 3;
        }

        setStats(newStats);
        setRecentActivity(newRecentActivity);
        setAlerts([
          {
            id: 1,
            type: 'warning',
            title: 'Low Stock Alert',
            message: 'Metformin 500mg tablets running low',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          },
          {
            id: 2,
            type: 'danger',
            title: 'Drug Interaction Warning',
            message: 'Potential interaction detected for Patient #1234',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
          },
          {
            id: 3,
            type: 'info',
            title: 'ML Model Update',
            message: 'Symptom analysis model updated successfully',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
          },
        ]);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [user?.role]);

  const getRoleSpecificStats = () => {
    const baseStats = [
      {
        title: 'Total Patients',
        value: stats.totalPatients || 0,
        change: '+12%',
        changeType: 'positive',
        icon: UserGroupIcon,
        color: 'primary',
      },
      {
        title: 'Total Prescriptions',
        value: stats.totalPrescriptions || 0,
        change: '+8%',
        changeType: 'positive',
        icon: ClipboardDocumentListIcon,
        color: 'secondary',
      },
    ];

    if (user?.role === 'admin' || user?.role === 'pharmacist') {
      baseStats.push(
        {
          title: 'Total Drugs',
          value: stats.totalDrugs || 0,
          change: '+5%',
          changeType: 'positive',
          icon: PillIcon,
          color: 'success',
        },
        {
          title: 'Forecast Accuracy',
          value: `${stats.forecastAccuracy || 0}%`,
          change: '+2.1%',
          changeType: 'positive',
          icon: ChartBarIcon,
          color: 'warning',
        }
      );
    }

    if (user?.role === 'admin') {
      baseStats.push(
        {
          title: 'Compliance Rate',
          value: `${stats.complianceRate || 0}%`,
          change: '+1.5%',
          changeType: 'positive',
          icon: CheckCircleIcon,
          color: 'success',
        },
        {
          title: 'Critical Alerts',
          value: stats.criticalAlerts || 0,
          change: '-2',
          changeType: 'negative',
          icon: ExclamationTriangleIcon,
          color: 'danger',
        }
      );
    }

    return baseStats;
  };

  const getRoleSpecificQuickActions = () => {
    const actions = [];

    if (user?.role === 'admin' || user?.role === 'doctor') {
      actions.push(
        { name: 'Add Patient', href: '/patients/new', icon: UserGroupIcon, color: 'primary' },
        { name: 'Create Prescription', href: '/prescriptions/new', icon: ClipboardDocumentListIcon, color: 'secondary' },
        { name: 'Analyze Symptoms', href: '/symptoms', icon: ChartBarIcon, color: 'success' }
      );
    }

    if (user?.role === 'admin' || user?.role === 'pharmacist') {
      actions.push(
        { name: 'Add Drug', href: '/drugs/new', icon: PillIcon, color: 'success' },
        { name: 'Check Interactions', href: '/drug-interactions', icon: ExclamationTriangleIcon, color: 'warning' },
        { name: 'View Forecasts', href: '/forecasting', icon: ChartBarIcon, color: 'info' }
      );
    }

    if (user?.role === 'admin') {
      actions.push(
        { name: 'System Settings', href: '/settings', icon: Cog6ToothIcon, color: 'neutral' },
        { name: 'User Management', href: '/users', icon: UserGroupIcon, color: 'primary' }
      );
    }

    return actions;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner h-12 w-12"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl p-6 text-white"
      >
        <h1 className="text-2xl font-bold mb-2">
          Welcome back, {user?.name || 'User'}!
        </h1>
        <p className="text-primary-100">
          Here's what's happening in your {user?.role || 'clinical'} dashboard today.
        </p>
      </motion.div>

      {/* Statistics Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {getRoleSpecificStats().map((stat, index) => (
          <StatCard key={stat.title} {...stat} delay={index * 0.1} />
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <QuickActions actions={getRoleSpecificQuickActions()} />
          </motion.div>

          {/* Chart Widget */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <ChartWidget userRole={user?.role} />
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Alerts Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <AlertsPanel alerts={alerts} />
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <RecentActivity activities={recentActivity} />
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;







