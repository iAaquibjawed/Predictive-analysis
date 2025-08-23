Rails.application.routes.draw do
  devise_for :users, path: '', path_names: {
    sign_in: 'login',
    sign_out: 'logout',
    registration: 'signup'
  }, controllers: {
    sessions: 'users/sessions',
    registrations: 'users/registrations'
  }

  namespace :api do
    namespace :v1 do
      # Patient management
      resources :patients do
        resources :medical_records
        resources :prescriptions
        resources :iot_readings
        member do
          get :compliance_report
          get :drug_interactions
        end
      end

      # Clinical decision support
      resources :symptoms, only: [:create] do
        collection do
          post :analyze
          post :recommendations
        end
      end

      # Drug management
      resources :drugs do
        collection do
          post :interaction_check
          get :search
        end
      end

      # Prescription management
      resources :prescriptions do
        member do
          patch :update_status
          get :adherence_data
        end
      end

      # Supply chain & forecasting
      resources :inventory do
        collection do
          get :forecast
          get :alerts
          post :reorder_suggestions
        end
      end

      # Audit & compliance
      resources :audit_logs, only: [:index, :show]

      # Admin routes
      namespace :admin do
        resources :users
        resources :system_health, only: [:index]
        resources :ml_models, only: [:index, :show]
      end

      # External ML API integration
      namespace :ml do
        post :clinical_analysis
        post :drug_interactions
        post :demand_forecast
        get :model_status
      end
    end
  end

  # Health check
  get '/health', to: 'health#index'

  # Sidekiq web interface (admin only)
  require 'sidekiq/web'
  mount Sidekiq::Web => '/sidekiq'
end