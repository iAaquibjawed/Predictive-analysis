FactoryBot.define do
  factory :drug_interaction do
    drug_a { nil }
    drug_b { nil }
    interaction_type { "MyString" }
    severity { "MyString" }
    description { "MyText" }
    mechanism { "MyText" }
    clinical_effect { "MyText" }
    management_recommendation { "MyText" }
  end
end
