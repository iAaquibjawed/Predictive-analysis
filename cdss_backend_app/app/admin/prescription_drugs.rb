ActiveAdmin.register PrescriptionDrug do
  menu parent: "Prescription Management", priority: 2

  permit_params :prescription_id, :drug_id, :dosage, :frequency, :duration, :daily_frequency

  # Index
  index do
    selectable_column
    id_column
    column "Prescription" do |pd|
      link_to "Prescription ##{pd.prescription.id}", admin_prescription_path(pd.prescription)
    end
    column "Patient" do |pd|
      pd.prescription.patient.full_name
    end
    column "Drug" do |pd|
      link_to pd.drug.name, admin_drug_path(pd.drug)
    end
    column :dosage
    column :frequency
    column :duration
    column :daily_frequency
    actions
  end
end