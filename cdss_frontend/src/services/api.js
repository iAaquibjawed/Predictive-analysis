import axios from 'axios';
import { toast } from 'react-hot-toast';

// Create axios instance for Rails backend
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for ML service
const mlApi = axios.create({
  baseURL: process.env.REACT_APP_ML_API_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for Rails API
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Request interceptor for ML API
mlApi.interceptors.request.use(
  (config) => {
    const token = process.env.REACT_APP_ML_API_TOKEN;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for Rails API
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }

    if (error.response?.status === 422) {
      const errors = error.response.data.errors;
      if (errors) {
        Object.keys(errors).forEach(key => {
          if (Array.isArray(errors[key])) {
            errors[key].forEach(errorMsg => {
              toast.error(`${key}: ${errorMsg}`);
            });
          }
        });
      }
    }

    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Response interceptor for ML API
mlApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status >= 500) {
      toast.error('ML service unavailable. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Rails API endpoints
export const railsApi = {
  // Authentication
  auth: {
    signIn: (credentials) => api.post('/api/v1/auth/sign_in', credentials),
    signOut: () => api.delete('/api/v1/auth/sign_out'),
    validateToken: () => api.get('/api/v1/auth/validate_token'),
    updateProfile: (userData) => api.put('/api/v1/auth', userData),
  },

  // Patients
  patients: {
    list: (params) => api.get('/api/v1/patients', { params }),
    get: (id) => api.get(`/api/v1/patients/${id}`),
    create: (data) => api.post('/api/v1/patients', data),
    update: (id, data) => api.put(`/api/v1/patients/${id}`, data),
    delete: (id) => api.delete(`/api/v1/patients/${id}`),
    complianceReport: (id) => api.get(`/api/v1/patients/${id}/compliance_report`),
    drugInteractions: (id) => api.get(`/api/v1/patients/${id}/drug_interactions`),
  },

  // Drugs
  drugs: {
    list: (params) => api.get('/api/v1/drugs', { params }),
    get: (id) => api.get(`/api/v1/drugs/${id}`),
    create: (data) => api.post('/api/v1/drugs', data),
    update: (id, data) => api.put(`/api/v1/drugs/${id}`, data),
    delete: (id) => api.delete(`/api/v1/drugs/${id}`),
    search: (query) => api.get('/api/v1/drugs/search', { params: { q: query } }),
    interactionCheck: (drugIds) => api.post('/api/v1/drugs/interaction_check', { drug_ids: drugIds }),
  },

  // Prescriptions
  prescriptions: {
    list: (params) => api.get('/api/v1/prescriptions', { params }),
    get: (id) => api.get(`/api/v1/prescriptions/${id}`),
    create: (data) => api.post('/api/v1/prescriptions', data),
    update: (id, data) => api.put(`/api/v1/prescriptions/${id}`, data),
    delete: (id) => api.delete(`/api/v1/prescriptions/${id}`),
    updateStatus: (id, status) => api.patch(`/api/v1/prescriptions/${id}/update_status`, { status }),
    adherenceData: (id) => api.get(`/api/v1/prescriptions/${id}/adherence_data`),
  },

  // Health check
  health: () => api.get('/api/v1/health'),
};

// ML API endpoints
export const mlApi = {
  // Symptoms analysis
  symptoms: {
    analyze: (data) => mlApi.post('/api/v1/symptoms/analyze_symptoms', data),
    search: (query, limit = 10) => mlApi.get('/api/v1/symptoms/search', { params: { query, limit } }),
    autocomplete: (prefix, limit = 5) => mlApi.get('/api/v1/symptoms/autocomplete', { params: { prefix, limit } }),
  },

  // Drug interactions
  drugInteractions: {
    check: (data) => mlApi.post('/api/v1/drug_interactions', data),
    getDrug: (drugId) => mlApi.get(`/api/v1/drug_interactions/${drugId}`),
    batchCheck: (data) => mlApi.post('/api/v1/drug_interactions/batch', data),
    contraindicated: (condition) => mlApi.get('/api/v1/drug_interactions/contraindicated', { params: { condition } }),
  },

  // Patient compliance
  compliance: {
    report: (patientId) => mlApi.get(`/api/v1/compliance/${patientId}`),
    medication: (patientId, medicationId) => mlApi.get(`/api/v1/compliance/${patientId}/medication/${medicationId}`),
    iotReading: (data) => mlApi.post('/api/v1/compliance/iot_reading', data),
    trends: (patientId) => mlApi.get(`/api/v1/compliance/${patientId}/trends`),
    alerts: (patientId) => mlApi.get(`/api/v1/compliance/${patientId}/alerts`),
  },

  // Demand forecasting
  forecasting: {
    demand: (data) => mlApi.post('/api/v1/forecast/demand', data),
    drug: (drugId) => mlApi.get(`/api/v1/forecast/${drugId}`),
    supplyChain: (data) => mlApi.post('/api/v1/forecast/supply_chain', data),
    seasonality: (drugId) => mlApi.get(`/api/v1/forecast/${drugId}/seasonality`),
    externalFactors: (drugId) => mlApi.get(`/api/v1/forecast/${drugId}/external_factors`),
    accuracy: (drugId) => mlApi.get(`/api/v1/forecast/${drugId}/accuracy`),
  },

  // Treatment recommendations
  recommendations: {
    generate: (data) => mlApi.post('/api/v1/recommendations', data),
    history: (patientId) => mlApi.get(`/api/v1/recommendations/history/${patientId}`),
    feedback: (data) => mlApi.post('/api/v1/recommendations/feedback', data),
    guidelines: (condition) => mlApi.get('/api/v1/recommendations/guidelines', { params: { condition } }),
    validate: (data) => mlApi.post('/api/v1/recommendations/validate', data),
    evidence: (treatment) => mlApi.get('/api/v1/recommendations/evidence', { params: { treatment } }),
    compare: (data) => mlApi.post('/api/v1/recommendations/compare', data),
  },

  // Health check
  health: () => mlApi.get('/health'),
};

// Utility functions
export const apiUtils = {
  // Handle API errors
  handleError: (error, customMessage = null) => {
    const message = customMessage ||
                   error.response?.data?.error ||
                   error.response?.data?.message ||
                   error.message ||
                   'An error occurred';

    toast.error(message);
    return { success: false, error: message };
  },

  // Handle API success
  handleSuccess: (message = 'Operation completed successfully') => {
    toast.success(message);
    return { success: true, message };
  },

  // Format API response
  formatResponse: (response) => {
    return {
      success: true,
      data: response.data,
      status: response.status,
    };
  },

  // Create query parameters
  createParams: (params) => {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    return queryParams.toString();
  },
};

export default api;







