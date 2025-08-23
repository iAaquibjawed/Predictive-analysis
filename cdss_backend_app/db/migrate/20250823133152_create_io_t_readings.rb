class CreateIoTReadings < ActiveRecord::Migration[7.2]
  def change
    create_table :io_t_readings do |t|
      t.references :patient, null: false, foreign_key: true
      t.references :prescription, null: false, foreign_key: true
      t.string :device_id
      t.string :event_type
      t.datetime :recorded_at
      t.json :data
      t.integer :battery_level

      t.timestamps
    end
  end
end
