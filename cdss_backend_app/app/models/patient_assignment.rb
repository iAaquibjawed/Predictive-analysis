class PatientAssignment < ApplicationRecord
  belongs_to :patient
  belongs_to :user

  def self.ransackable_attributes(auth_object = nil)
    [
      "assigned_at", "active", "created_at", "updated_at",
      "patient_id", "user_id"
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    [
      "patient", "user"
    ]
  end

  scope :active, -> { where(active: true) }
  scope :by_patient, ->(patient_id) { where(patient_id: patient_id) }
  scope :by_user, ->(user_id) { where(user_id: user_id) }

  def active?
    active
  end

  def assign_time
    assigned_at || created_at
  end
end
