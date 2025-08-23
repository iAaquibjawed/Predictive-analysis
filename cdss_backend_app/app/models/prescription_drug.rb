class PrescriptionDrug < ApplicationRecord
  belongs_to :prescription
  belongs_to :drug

  validates :dosage, presence: true
  validates :frequency, presence: true
  validates :duration, presence: true

  before_save :calculate_daily_frequency

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "created_at", "daily_frequency", "dosage", "drug_id",
      "duration", "frequency", "id", "prescription_id", "updated_at"
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    ["prescription", "drug"]
  end

  private

  def calculate_daily_frequency
    case frequency&.downcase
    when /once.*day|daily/
      self.daily_frequency = 1
    when /twice.*day|bid/
      self.daily_frequency = 2
    when /three.*day|tid/
      self.daily_frequency = 3
    when /four.*day|qid/
      self.daily_frequency = 4
    else
      self.daily_frequency = 1
    end
  end
end