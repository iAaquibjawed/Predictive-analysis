class CreateDrugInteractions < ActiveRecord::Migration[7.2]
  def change
    create_table :drug_interactions do |t|
      t.references :drug_a, null: false, foreign_key: true
      t.references :drug_b, null: false, foreign_key: true
      t.string :interaction_type
      t.string :severity
      t.text :description
      t.text :mechanism
      t.text :clinical_effect
      t.text :management_recommendation

      t.timestamps
    end
  end
end
