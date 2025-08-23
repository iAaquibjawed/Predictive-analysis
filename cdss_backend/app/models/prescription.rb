class Prescription < ApplicationRecord
  belongs_to :patient
  belongs_to :prescribing_doctor, class_name: 'User'
  has_many :prescription_drugs, dependent: :destroy
  has_many :drugs, through: :prescription_drugs

  enum status: { pending: 0, active: 1, completed: 2, cancelled: 3 }

  validates :prescription_date, presence: true
  validates :status, presence: true

  scope :for_patient, ->(patient_id) { where(patient_id: patient_id) }
  scope :by_doctor, ->(doctor_id) { where(prescribing_doctor_id: doctor_id) }
  scope :recent, -> { where(prescription_date: 30.days.ago..Time.current) }

  def adherence_percentage
    return 0 unless iot_readings.any?

    expected_doses = calculate_expected_doses
    actual_doses = iot_readings.where(event_type: 'dose_taken').count

    return 100 if expected_doses.zero?
    [(actual_doses.to_f / expected_doses * 100).round(2), 100].min
  end

  private

  def calculate_expected_doses
    # Calculate based on prescription duration and frequency
    days_active = (Time.current.to_date - prescription_date.to_date).to_i
    prescription_drugs.sum { |pd| pd.daily_frequency * days_active }
  end
end