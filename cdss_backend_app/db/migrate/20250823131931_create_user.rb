class CreateUser < ActiveRecord::Migration[7.2]
  def change
    create_table :users do |t|
      t.string :email,              null: false, default: ""
      t.string :encrypted_password, null: false, default: ""
      t.string :first_name,         null: false
      t.string :last_name,          null: false
      t.integer :role,              null: false, default: 0
      t.boolean :active,            null: false, default: true
      t.string :phone_number
      t.text :specialization
      t.string :license_number
      t.timestamps null: false
    end

    add_index :users, :email,                unique: true
    add_index :users, :role
    add_index :users, :active
  end
end
