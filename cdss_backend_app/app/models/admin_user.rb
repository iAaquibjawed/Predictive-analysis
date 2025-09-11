class AdminUser < ApplicationRecord
  devise :database_authenticatable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :trackable

  validates :email, presence: true, uniqueness: true

  # Auto-confirm admin users created through ActiveAdmin
  before_create :confirm_admin_user_if_admin_created

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    # ["created_at", "email", "id", "updated_at"]
    ["created_at", "email", "id", "updated_at", "reset_password_token_cont", "reset_password_token_eq", "reset_password_token_start"]

    # EXCLUDE: encrypted_password, reset_password_token, etc.
  end

  def self.ransackable_associations(auth_object = nil)
    []
  end

  private

  def confirm_admin_user_if_admin_created
    # Auto-confirm admin users created through ActiveAdmin or in development
    if (defined?(ActiveAdmin) && Thread.current[:active_admin_creating_admin_user]) || Rails.env.development?
      self.confirmed_at = Time.current
    end
  end

  # Skip email confirmation requirement in development
  def confirmation_required?
    !Rails.env.development?
  end
end