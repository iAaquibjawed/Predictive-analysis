import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const QuickActions = ({ actions }) => {
  const getColorClasses = (color) => {
    const colorMap = {
      primary: {
        bg: 'bg-primary-600 hover:bg-primary-700',
        text: 'text-white',
        border: 'border-primary-600',
      },
      secondary: {
        bg: 'bg-secondary-600 hover:bg-secondary-700',
        text: 'text-white',
        border: 'border-secondary-600',
      },
      success: {
        bg: 'bg-success-600 hover:bg-success-700',
        text: 'text-white',
        border: 'border-success-600',
      },
      warning: {
        bg: 'bg-warning-600 hover:bg-warning-700',
        text: 'text-white',
        border: 'border-warning-600',
      },
      danger: {
        bg: 'bg-danger-600 hover:bg-danger-700',
        text: 'text-white',
        border: 'border-danger-600',
      },
      info: {
        bg: 'bg-blue-600 hover:bg-blue-700',
        text: 'text-white',
        border: 'border-blue-600',
      },
      neutral: {
        bg: 'bg-neutral-600 hover:bg-neutral-700',
        text: 'text-white',
        border: 'border-neutral-600',
      },
    };

    return colorMap[color] || colorMap.primary;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-neutral-900">Quick Actions</h3>
        <p className="text-sm text-neutral-500">Common tasks and shortcuts</p>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {actions.map((action, index) => {
            const colors = getColorClasses(action.color);

            return (
              <motion.div
                key={action.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Link
                  to={action.href}
                  className={`block p-4 rounded-lg border-2 ${colors.border} ${colors.bg} ${colors.text} text-center transition-all duration-200 hover:shadow-medium`}
                >
                  <action.icon className="h-8 w-8 mx-auto mb-3" />
                  <span className="font-medium">{action.name}</span>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default QuickActions;







