class Drug < ApplicationRecord
  has_many :prescription_drugs, dependent: :destroy
  has_many :prescriptions, through: :prescription_drugs
  has_many :drug_interactions_as_a, class_name: 'DrugInteraction', foreign_key: 'drug_a_id'
  has_many :drug_interactions_as_b, class_name: 'DrugInteraction', foreign_key: 'drug_b_id'

  validates :name, presence: true
  validates :generic_name, presence: true
  validates :dosage_form, presence: true
  validates :strength, presence: true

  scope :active, -> { where(active: true) }
  scope :search_by_name, ->(term) { where("name ILIKE ? OR generic_name ILIKE ?", "%#{term}%", "%#{term}%") }

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "active", "contraindications", "created_at", "description",
      "dosage_form", "generic_name", "id", "indications",
      "manufacturer", "name", "side_effects", "strength", "updated_at"
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    [
      "prescription_drugs", "prescriptions",
      "drug_interactions_as_a", "drug_interactions_as_b"
    ]
  end

  def drug_interactions
    DrugInteraction.where("drug_a_id = ? OR drug_b_id = ?", id, id)
  end

  def interaction_warnings(other_drug_ids)
    DrugInteraction.where(
      "(drug_a_id = ? AND drug_b_id IN (?)) OR (drug_b_id = ? AND drug_a_id IN (?))",
      id, other_drug_ids, id, other_drug_ids
    )
  end
end