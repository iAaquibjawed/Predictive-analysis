FactoryBot.define do
  factory :io_t_reading do
    patient { nil }
    prescription { nil }
    device_id { "MyString" }
    event_type { "MyString" }
    recorded_at { "2025-08-23 14:31:52" }
    data { "" }
    battery_level { 1 }
  end
end
