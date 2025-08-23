FactoryBot.define do
  factory :medical_record do
    patient { nil }
    created_by { nil }
    diagnosis { "MyString" }
    symptoms { "MyText" }
    treatment_plan { "MyText" }
    notes { "MyText" }
    visit_date { "2025-08-23" }
  end
end
