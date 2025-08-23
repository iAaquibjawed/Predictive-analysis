ActiveAdmin.register IoTReading do
  menu parent: "Clinical Management", priority: 4

  permit_params :patient_id, :prescription_id, :device_id, :event_type,
                :recorded_at, :battery_level

  # Filters
  filter :patient
  filter :prescription
  filter :device_id
  filter :event_type, as: :select, collection: IoTReading.event_types
  filter :recorded_at
  filter :battery_level

  # Scopes
  scope :all, default: true
  scope :recent
  scope("Low Battery") { |scope| scope.where("battery_level < ?", 20) }
  scope("Dose Taken") { |scope| scope.where(event_type: :dose_taken) }
  scope("Device Offline") { |scope| scope.where(event_type: :device_offline) }

  # Index
  index do
    selectable_column
    id_column
    column "Patient" do |reading|
      link_to reading.patient.full_name, admin_patient_path(reading.patient)
    end
    column :device_id
    column :event_type do |reading|
      status_tag reading.event_type.humanize, class: reading.event_type
    end
    column :recorded_at
    column :battery_level do |reading|
      if reading.battery_level
        color = reading.battery_level > 50 ? :ok : reading.battery_level > 20 ? :warning : :error
        status_tag "#{reading.battery_level}%", color
      end
    end
    actions
  end
end