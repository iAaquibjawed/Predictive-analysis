class CreatePrescriptionTable < ActiveRecord::Migration[7.2]
  def change
    create_table :prescriptions do |t|
      t.references :patient, null: false, foreign_key: true
      t.references :prescribing_doctor, null: false, foreign_key: { to_table: :users }
      t.date :prescription_date
      t.integer :status
      t.text :notes

      t.timestamps
    end
  end
end
