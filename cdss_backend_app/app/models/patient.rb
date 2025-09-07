class Patient < ApplicationRecord
  belongs_to :user
  has_many :patient_assignments, dependent: :destroy
  has_many :assigned_doctors, through: :patient_assignments, source: :user
  has_many :medical_records, dependent: :destroy
  has_many :prescriptions, dependent: :destroy
  has_many :iot_readings, dependent: :destroy
  belongs_to :doctor, optional: true

  validates :nhs_number, presence: true, uniqueness: true, length: { is: 10 }
  validates :date_of_birth, presence: true
  validates :gender, inclusion: { in: %w[male female other prefer_not_to_say] }

  scope :by_doctor, ->(doctor_id) { joins(:patient_assignments).where(patient_assignments: { user_id: doctor_id }) }

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "address", "allergies", "created_at", "date_of_birth",
      "emergency_contact", "gender", "id", "medical_history",
      "nhs_number", "phone_number", "updated_at", "user_id"
    ]
  end

  # Ransack searchable associations
  def self.ransackable_associations(auth_object = nil)
    [
      "user", "patient_assignments", "assigned_doctors",
      "medical_records", "prescriptions", "iot_readings"
    ]
  end

  def age
    return nil unless date_of_birth
    ((Time.current - date_of_birth.to_time) / 1.year).floor
  end

  def full_name
    user.full_name
  end

  def current_medications
    prescriptions.active.includes(:prescription_drugs, :drugs)
  end

  def recent_readings(days: 7)
    iot_readings.where(recorded_at: days.days.ago..Time.current)
  end
end