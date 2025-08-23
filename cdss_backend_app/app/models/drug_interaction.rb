class DrugInteraction < ApplicationRecord
  belongs_to :drug_a, class_name: 'Drug'
  belongs_to :drug_b, class_name: 'Drug'

  validates :interaction_type, presence: true
  validates :severity, inclusion: { in: %w[low moderate high critical] }
  validates :description, presence: true

  scope :by_severity, ->(severity) { where(severity: severity) }
  scope :critical, -> { where(severity: 'critical') }
  scope :high_risk, -> { where(severity: ['high', 'critical']) }

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "clinical_effect", "created_at", "description", "drug_a_id",
      "drug_b_id", "id", "interaction_type", "management_recommendation",
      "mechanism", "severity", "updated_at"
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    ["drug_a", "drug_b"]
  end
end