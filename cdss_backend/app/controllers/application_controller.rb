class ApplicationController < ActionController::API
  include DeviseTokenAuth::Concerns::SetUserByToken

  before_action :authenticate_user!
  before_action :log_request

  rescue_from CanCan::AccessDenied, with: :access_denied
  rescue_from ActiveRecord::RecordNotFound, with: :not_found
  rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity

  private

  def current_ability
    @current_ability ||= Ability.new(current_user)
  end

  def log_request
    AuditLog.create(
      user: current_user,
      action: "#{controller_name}##{action_name}",
      resource_type: controller_name.classify,
      ip_address: request.remote_ip,
      user_agent: request.user_agent,
      performed_at: Time.current
    )
  end

  def access_denied
    render json: { error: 'Access denied' }, status: :forbidden
  end

  def not_found
    render json: { error: 'Resource not found' }, status: :not_found
  end

  def unprocessable_entity(exception)
    render json: {
      error: 'Validation failed',
      details: exception.record.errors.full_messages
    }, status: :unprocessable_entity
  end
end