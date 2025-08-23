class IoTReading < ApplicationRecord
  belongs_to :patient
  belongs_to :prescription, optional: true

  validates :device_id, presence: true
  validates :event_type, presence: true
  validates :recorded_at, presence: true

  enum event_type: {
    dose_taken: 0,
    dose_missed: 1,
    device_opened: 2,
    device_closed: 3,
    low_battery: 4,
    device_offline: 5
  }

  scope :recent, -> { where(recorded_at: 7.days.ago..Time.current) }
  scope :for_device, ->(device_id) { where(device_id: device_id) }

  # Ransack searchable attributes
  def self.ransackable_attributes(auth_object = nil)
    [
      "battery_level", "created_at", "device_id", "event_type",
      "id", "patient_id", "prescription_id", "recorded_at", "updated_at"
    # EXCLUDE: data (might contain sensitive info)
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    ["patient", "prescription"]
  end
end