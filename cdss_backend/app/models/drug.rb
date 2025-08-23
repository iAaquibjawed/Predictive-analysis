class Drug < ApplicationRecord
  has_many :prescription_drugs, dependent: :destroy
  has_many :prescriptions, through: :prescription_drugs
  has_many :drug_interactions, dependent: :destroy

  validates :name, presence: true
  validates :generic_name, presence: true
  validates :dosage_form, presence: true
  validates :strength, presence: true

  scope :active, -> { where(active: true) }
  scope :search_by_name, ->(term) { where("name ILIKE ? OR generic_name ILIKE ?", "%#{term}%", "%#{term}%") }

  def interaction_warnings(other_drugs)
    DrugInteraction.where(
      "(drug_a_id = ? AND drug_b_id IN (?)) OR (drug_b_id = ? AND drug_a_id IN (?))",
      id, other_drugs.pluck(:id), id, other_drugs.pluck(:id)
    )
  end
end