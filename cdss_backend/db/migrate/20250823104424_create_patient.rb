class CreatePatient < ActiveRecord::Migration[7.2]
  def change
    create_table :patients do |t|
      t.references :user, null: false, foreign_key: true
      t.string :nhs_number, null: false
      t.date :date_of_birth, null: false
      t.string :gender, null: false
      t.text :address
      t.string :phone_number
      t.text :emergency_contact
      t.text :medical_history
      t.text :allergies
      t.timestamps
    end

    add_index :patients, :nhs_number, unique: true
  end
end
