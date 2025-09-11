class User < ApplicationRecord
  extend Devise::Models
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :trackable

  include DeviseTokenAuth::Concerns::User

  enum role: { patient: 0, doctor: 1, pharmacist: 2, admin: 3 }

  # Associations
  has_one :patient, dependent: :destroy
  has_many :patient_assignments, dependent: :destroy
  has_many :assigned_patients, through: :patient_assignments, source: :patient
  has_many :prescribed_prescriptions, class_name: 'Prescription', foreign_key: 'prescribing_doctor_id'
  has_many :created_medical_records, class_name: 'MedicalRecord', foreign_key: 'created_by_id'
  has_many :audit_logs, dependent: :destroy

  validates :first_name, :last_name, presence: true

  # DeviseTokenAuth validations
  validates :provider, presence: true, unless: :email_required?
  validates :uid, presence: true, unless: :email_required?
  validates :email, presence: true, if: :email_required?

  # DeviseTokenAuth callbacks
  before_validation :set_uid, on: :create
  before_validation :set_provider, on: :create

  # Auto-confirm users created through ActiveAdmin
  before_create :confirm_user_if_admin_created

  # Custom setter to handle string role values from forms
  def role=(value)
    if value.is_a?(String) && value.match?(/^\d+$/)
      # Convert string number to symbol
      role_mapping = { '0' => :patient, '1' => :doctor, '2' => :pharmacist, '3' => :admin }
      mapped_role = role_mapping[value]
      if mapped_role
        super(mapped_role)
      else
        super(value)
      end
    elsif value.is_a?(String) && !value.match?(/^\d+$/)
      # Handle string role names (e.g., "patient", "doctor")
      super(value.to_sym)
    else
      super(value)
    end
  end

  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }
  scope :doctors, -> { where(role: :doctor) }
  scope :patients, -> { where(role: :patient) }

  # Ransack searchable attributes - EXCLUDE sensitive data
  def self.ransackable_attributes(auth_object = nil)
    [
      "active", "created_at", "email", "first_name", "id",
      "last_name", "license_number", "phone_number", "role",
      "specialization", "updated_at"
    # EXCLUDE: encrypted_password, reset_password_token, confirmation_token, tokens, etc.
    ]
  end

  # Ransack searchable associations
  def self.ransackable_associations(auth_object = nil)
    [
      "patient", "patient_assignments", "assigned_patients",
      "prescribed_prescriptions", "created_medical_records"
    ]
  end

  def full_name
    "#{first_name} #{last_name}"
  end

  def can_access_patient?(patient)
    return true if admin?
    return patient.user_id == id if patient?
    assigned_patients.include?(patient) if doctor? || pharmacist?
  end

  def token_validation_response
    {
      id: id,
      email: email,
      first_name: first_name,
      last_name: last_name,
      role: role,
      active: active
    }
  end

  private

  def email_required?
    provider == 'email'
  end

  def set_uid
    self.uid = email if uid.blank? && email.present?
  end

  def set_provider
    self.provider = 'email' if provider.blank?
  end

  def confirm_user_if_admin_created
    # Auto-confirm users created through ActiveAdmin
    if defined?(ActiveAdmin) && Thread.current[:active_admin_creating_user]
      self.confirmed_at = Time.current
    end
  end
end