ActiveAdmin.register Drug do
  menu parent: "Drug Database", priority: 1

  permit_params :name, :generic_name, :dosage_form, :strength, :manufacturer,
                :description, :indications, :contraindications, :side_effects, :active

  # Filters
  filter :name
  filter :generic_name
  filter :dosage_form, as: :select, collection: ['tablet', 'capsule', 'injection', 'syrup', 'cream', 'inhaler']
  filter :manufacturer
  filter :active

  # Scopes
  scope :all
  scope :active, default: true
  scope("High Interaction Risk") { |scope| scope.joins(:drug_interactions_as_a, :drug_interactions_as_b).distinct }

  # Index
  index do
    selectable_column
    id_column
    column :name do |drug|
      link_to drug.name, admin_drug_path(drug)
    end
    column :generic_name
    column :dosage_form
    column :strength
    column :manufacturer
    column "Interactions" do |drug|
      drug.drug_interactions.count
    end
    column :active do |drug|
      status_tag drug.active? ? "Active" : "Inactive"
    end
    column :created_at
    actions
  end

  # Show
  show do
    attributes_table do
      row :name
      row :generic_name
      row :dosage_form
      row :strength
      row :manufacturer
      row :description
      row :indications
      row :contraindications
      row :side_effects
      row :active do |drug|
        status_tag drug.active? ? "Active" : "Inactive"
      end
      row :created_at
    end

    # Drug Interactions Panel
    panel "Known Drug Interactions" do
      table_for resource.drug_interactions.limit(10) do
        column "Interacting Drug" do |interaction|
          other_drug = interaction.drug_a_id == resource.id ? interaction.drug_b : interaction.drug_a
          link_to other_drug.name, admin_drug_path(other_drug)
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
      end
    end

    # Prescriptions Panel
    panel "Recent Prescriptions" do
      prescriptions = PrescriptionDrug.joins(:prescription, :drug)
                                      .where(drug: resource)
                                      .includes(prescription: [:patient, :prescribing_doctor])
                                      .limit(10)
                                      .order(created_at: :desc)

      table_for prescriptions do
        column "Date" do |pd|
          pd.prescription.prescription_date
        end
        column "Patient" do |pd|
          link_to pd.prescription.patient.full_name, admin_patient_path(pd.prescription.patient)
        end
        column "Doctor" do |pd|
          pd.prescription.prescribing_doctor.full_name
        end
        column :dosage
        column :frequency
      end
    end
  end

  # Form
  form do |f|
    f.inputs "Drug Information" do
      f.input :name
      f.input :generic_name
      f.input :dosage_form, as: :select, collection: ['tablet', 'capsule', 'injection', 'syrup', 'cream', 'inhaler']
      f.input :strength
      f.input :manufacturer
      f.input :active
    end

    f.inputs "Clinical Information" do
      f.input :description, as: :text
      f.input :indications, as: :text, hint: "What conditions this drug treats"
      f.input :contraindications, as: :text, hint: "When this drug should not be used"
      f.input :side_effects, as: :text, hint: "Known side effects"
    end

    f.actions
  end

  # CSV export
  csv do
    column :name
    column :generic_name
    column :dosage_form
    column :strength
    column :manufacturer
    column :active
    column("Interaction Count") { |drug| drug.drug_interactions.count }
    column("Prescription Count") { |drug| drug.prescription_drugs.count }
  end
end