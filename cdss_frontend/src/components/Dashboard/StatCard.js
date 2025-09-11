import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, change, changeType, icon: Icon, color, delay = 0 }) => {
  const getColorClasses = (color) => {
    const colorMap = {
      primary: {
        bg: 'bg-primary-100',
        text: 'text-primary-600',
        iconBg: 'bg-primary-100',
        iconText: 'text-primary-600',
      },
      secondary: {
        bg: 'bg-secondary-100',
        text: 'text-secondary-600',
        iconBg: 'bg-secondary-100',
        iconText: 'text-secondary-600',
      },
      success: {
        bg: 'bg-success-100',
        text: 'text-success-600',
        iconBg: 'bg-success-100',
        iconText: 'text-success-600',
      },
      warning: {
        bg: 'bg-warning-100',
        text: 'text-warning-600',
        iconBg: 'bg-warning-100',
        iconText: 'text-warning-600',
      },
      danger: {
        bg: 'bg-danger-100',
        text: 'text-danger-600',
        iconBg: 'bg-danger-100',
        iconText: 'text-danger-600',
      },
      neutral: {
        bg: 'bg-neutral-100',
        text: 'text-neutral-600',
        iconBg: 'bg-neutral-100',
        iconText: 'text-neutral-600',
      },
    };

    return colorMap[color] || colorMap.primary;
  };

  const colors = getColorClasses(color);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="stat-card"
    >
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-lg ${colors.iconBg}`}>
          <Icon className={`h-6 w-6 ${colors.iconText}`} />
        </div>
        <div className="ml-4 flex-1">
          <p className="stat-label">{title}</p>
          <p className="stat-value">{value}</p>
        </div>
      </div>

      {change && (
        <div className="mt-4 flex items-center">
          <span
            className={`stat-change ${
              changeType === 'positive' ? 'stat-change-positive' : 'stat-change-negative'
            }`}
          >
            {change}
          </span>
          <span className="text-xs text-neutral-500 ml-2">from last month</span>
        </div>
      )}
    </motion.div>
  );
};

export default StatCard;







