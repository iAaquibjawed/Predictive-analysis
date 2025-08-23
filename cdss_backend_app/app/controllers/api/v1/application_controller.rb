class Api::ApplicationController < ActionController::API
  include DeviseTokenAuth::Concerns::SetUserByToken

  before_action :authenticate_user!
  before_action :log_api_request

  rescue_from CanCan::AccessDenied, with: :access_denied
  rescue_from ActiveRecord::RecordNotFound, with: :not_found
  rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity

  private

  def current_ability
    @current_ability ||= Ability.new(current_user)
  end

  def log_api_request
    return unless current_user.present?
    return if controller_name == 'health' # Skip health checks

    # Get resource if available
    resource = nil
    if params[:id] && respond_to?(:resource_class) && resource_class.respond_to?(:find)
      begin
        resource = resource_class.find(params[:id])
      rescue => e
        # Resource might not exist or be accessible, that's ok
      end
    end

    AuditLog.log_action(
      user: current_user,
      action: "API::#{controller_name.camelize}##{action_name}",
      resource: resource,
      ip_address: request.remote_ip,
      user_agent: request.user_agent
    )
  rescue => e
    Rails.logger.error "Failed to log API audit trail: #{e.message}"
  end

  def access_denied(exception)
    render json: { error: 'Access denied' }, status: :forbidden
  end

  def not_found(exception)
    render json: { error: 'Resource not found' }, status: :not_found
  end

  def unprocessable_entity(exception)
    render json: {
      error: 'Validation failed',
      details: exception.record.errors.full_messages
    }, status: :unprocessable_entity
  end
end