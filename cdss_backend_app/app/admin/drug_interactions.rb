ActiveAdmin.register DrugInteraction do
  menu parent: "Drug Database", priority: 2

  permit_params :drug_a_id, :drug_b_id, :interaction_type, :severity, :description,
                :mechanism, :clinical_effect, :management_recommendation

  # Filters
  filter :drug_a, label: "Drug A"
  filter :drug_b, label: "Drug B"
  filter :severity, as: :select, collection: ['low', 'moderate', 'high', 'critical']
  filter :interaction_type

  # Scopes
  scope :all, default: true
  scope :critical
  scope :high_risk

  # Index
  index do
    selectable_column
    id_column
    column "Drug A" do |interaction|
      link_to interaction.drug_a.name, admin_drug_path(interaction.drug_a)
    end
    column "Drug B" do |interaction|
      link_to interaction.drug_b.name, admin_drug_path(interaction.drug_b)
    end
    column :severity do |interaction|
      color = case interaction.severity
              when 'low' then :ok
              when 'moderate' then :warning
              when 'high' then :error
              when 'critical' then :error
              end
      status_tag interaction.severity.humanize, color
    end
    column :interaction_type
    column :description do |interaction|
      truncate(interaction.description, length: 100)
    end
    actions
  end

  # Form
  form do |f|
    f.inputs "Drug Interaction" do
      f.input :drug_a, as: :select, collection: Drug.active.map { |d| [d.name, d.id] }
      f.input :drug_b, as: :select, collection: Drug.active.map { |d| [d.name, d.id] }
      f.input :severity, as: :select, collection: ['low', 'moderate', 'high', 'critical']
      f.input :interaction_type
      f.input :description, as: :text
      f.input :mechanism, as: :text
      f.input :clinical_effect, as: :text
      f.input :management_recommendation, as: :text
    end
    f.actions
  end
end