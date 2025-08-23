FactoryBot.define do
  factory :patient_assignment do
    patient { nil }
    user { nil }
    assigned_at { "2025-08-23 14:31:44" }
    active { false }
  end
end
