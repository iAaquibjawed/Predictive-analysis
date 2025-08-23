class User < ApplicationRecord
  devise :database_authenticatable, :registerable, :validatable,
         :jwt_authenticatable, jwt_revocation_strategy: Devise::JWT::RevocationStrategies::Null

  enum role: { patient: 0, doctor: 1, pharmacist: 2, admin: 3 }

  has_many :patient_assignments, dependent: :destroy
  has_many :assigned_patients, through: :patient_assignments, source: :patient
  has_many :audit_logs, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :role, presence: true
  validates :first_name, :last_name, presence: true

  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }

  def full_name
    "#{first_name} #{last_name}"
  end

  def can_access_patient?(patient)
    return true if admin?
    return patient.user_id == id if patient?
    assigned_patients.include?(patient) if doctor? || pharmacist?
  end
end