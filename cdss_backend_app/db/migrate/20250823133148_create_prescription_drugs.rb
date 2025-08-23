class CreatePrescriptionDrugs < ActiveRecord::Migration[7.2]
  def change
    create_table :prescription_drugs do |t|
      t.references :prescription, null: false, foreign_key: true
      t.references :drug, null: false, foreign_key: true
      t.string :dosage
      t.string :frequency
      t.string :duration
      t.integer :daily_frequency

      t.timestamps
    end
  end
end
