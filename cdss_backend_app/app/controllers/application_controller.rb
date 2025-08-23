class ApplicationController < ActionController::Base
  allow_browser versions: :modern
  protect_from_forgery with: :exception

  before_action :log_request

  rescue_from CanCan::AccessDenied, with: :access_denied
  rescue_from ActiveRecord::RecordNotFound, with: :not_found
  rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity

  private

  def current_ability
    if respond_to?(:current_admin_user) && current_admin_user
      @current_ability ||= AdminAbility.new(current_admin_user)
    elsif respond_to?(:current_user) && current_user
      @current_ability ||= Ability.new(current_user)
    else
      @current_ability ||= Ability.new(nil)
    end
  end

  def log_request
    # Only log API requests, not ActiveAdmin pages
    return unless request.format.json?
    return unless respond_to?(:current_user) && current_user.present?
    return if controller_name == 'health' # Skip health checks

    AuditLog.log_action(
      user: current_user,
      action: "#{controller_name}##{action_name}",
      ip_address: request.remote_ip,
      user_agent: request.user_agent
    )
  rescue => e
    Rails.logger.error "Failed to log audit trail: #{e.message}"
  end

  def access_denied(exception)
    if request.format.json?
      render json: { error: 'Access denied' }, status: :forbidden
    else
      if request.path.start_with?('/admin')
        redirect_to new_admin_user_session_path, alert: 'Access denied'
      else
        redirect_to root_path, alert: 'Access denied'
      end
    end
  end

  def not_found(exception)
    if request.format.json?
      render json: { error: 'Resource not found' }, status: :not_found
    else
      if request.path.start_with?('/admin')
        redirect_to admin_root_path, alert: 'Resource not found'
      else
        redirect_to root_path, alert: 'Resource not found'
      end
    end
  end

  def unprocessable_entity(exception)
    if request.format.json?
      render json: {
        error: 'Validation failed',
        details: exception.record.errors.full_messages
      }, status: :unprocessable_entity
    else
      if request.path.start_with?('/admin')
        redirect_to admin_root_path, alert: 'Validation failed'
      else
        redirect_to root_path, alert: 'Validation failed'
      end
    end
  end
end