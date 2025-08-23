FactoryBot.define do
  factory :prescription_drug do
    prescription { nil }
    drug { nil }
    dosage { "MyString" }
    frequency { "MyString" }
    duration { "MyString" }
    daily_frequency { 1 }
  end
end
