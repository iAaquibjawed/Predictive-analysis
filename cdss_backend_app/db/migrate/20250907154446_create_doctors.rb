class CreateDoctors < ActiveRecord::Migration[7.2]
  def change
    create_table :doctors do |t|
      t.string :name, null: false
      t.string :specialty
      t.string :phone_number
      t.string :email, null: false, index: { unique: true }
      t.text :address

      t.timestamps
    end
  end
end
