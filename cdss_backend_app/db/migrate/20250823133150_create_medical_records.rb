class CreateMedicalRecords < ActiveRecord::Migration[7.2]
  def change
    create_table :medical_records do |t|
      t.references :patient, null: false, foreign_key: true
      t.references :created_by, null: false, foreign_key: true
      t.string :diagnosis
      t.text :symptoms
      t.text :treatment_plan
      t.text :notes
      t.date :visit_date

      t.timestamps
    end
  end
end
