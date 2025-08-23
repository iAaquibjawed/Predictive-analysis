class Patient < ApplicationRecord
  belongs_to :user
  has_many :medical_records, dependent: :destroy
  has_many :prescriptions, dependent: :destroy
  has_many :iot_readings, dependent: :destroy
  has_many :patient_assignments, dependent: :destroy
  has_many :assigned_doctors, through: :patient_assignments, source: :user

  validates :nhs_number, presence: true, uniqueness: true, length: { is: 10 }
  validates :date_of_birth, presence: true
  validates :gender, inclusion: { in: %w[male female other prefer_not_to_say] }

  scope :by_doctor, ->(doctor_id) { joins(:patient_assignments).where(patient_assignments: { user_id: doctor_id }) }

  def age
    return nil unless date_of_birth
    ((Time.current - date_of_birth.to_time) / 1.year).floor
  end

  def current_medications
    prescriptions.active.includes(:drug)
  end

  def recent_readings(days: 7)
    iot_readings.where(recorded_at: days.days.ago..Time.current)
  end
end