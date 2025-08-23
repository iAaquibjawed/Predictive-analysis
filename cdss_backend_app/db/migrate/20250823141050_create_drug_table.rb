class CreateDrugTable < ActiveRecord::Migration[7.2]
  def change
    create_table :drugs do |t|
      t.string :name
      t.string :generic_name
      t.string :dosage_form
      t.string :strength
      t.string :manufacturer
      t.text :description
      t.text :indications
      t.text :contraindications
      t.text :side_effects
      t.boolean :active

      t.timestamps
    end
  end
end
