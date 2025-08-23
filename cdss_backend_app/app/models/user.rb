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
end