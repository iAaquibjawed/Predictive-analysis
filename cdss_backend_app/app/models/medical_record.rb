class MedicalRecord < ApplicationRecord
  belongs_to :patient
  belongs_to :created_by, class_name: 'User'

  validates :visit_date, presence: true
  validates :created_by, inclusion: { in: proc { User.where(role: [:doctor, :admin]) } }

  scope :recent, -> { where(visit_date: 3.months.ago..Time.current) }
  scope :by_doctor, ->(doctor_id) { where(created_by_id: doctor_id) }

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "created_at", "created_by_id", "diagnosis", "id",
      "notes", "patient_id", "symptoms", "treatment_plan",
      "updated_at", "visit_date"
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    ["patient", "created_by"]
  end
end
