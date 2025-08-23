class CreatePatientAssignments < ActiveRecord::Migration[7.2]
  def change
    create_table :patient_assignments do |t|
      t.references :patient, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true
      t.datetime :assigned_at
      t.boolean :active

      t.timestamps
    end
  end
end
