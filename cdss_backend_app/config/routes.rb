Rails.application.routes.draw do
  # ActiveAdmin routes (web interface)
  devise_for :admin_users, ActiveAdmin::Devise.config
  ActiveAdmin.routes(self)

  # API routes with DeviseTokenAuth
  namespace :api do
    namespace :v1 do
      # DeviseTokenAuth routes
      mount_devise_token_auth_for 'User', at: 'auth'

      # API endpoints
      resources :patients do
        member do
          get :compliance_report
          get :drug_interactions
        end
      end

      resources :drugs do
        collection do
          post :interaction_check
          get :search
        end
      end

      resources :prescriptions do
        member do
          patch :update_status
          get :adherence_data
        end
      end

      # Health check for API
      get :health, to: 'health#index'
    end
  end

  # General health check
  get '/health', to: 'health#index'

  # Root route to ActiveAdmin
  root to: "admin/dashboard#index"
end