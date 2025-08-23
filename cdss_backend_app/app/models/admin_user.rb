class AdminUser < ApplicationRecord
  devise :database_authenticatable,
         :recoverable, :rememberable, :validatable

  validates :email, presence: true, uniqueness: true

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    ["created_at", "email", "id", "updated_at"]
    # EXCLUDE: encrypted_password, reset_password_token, etc.
  end

  def self.ransackable_associations(auth_object = nil)
    []
  end
end