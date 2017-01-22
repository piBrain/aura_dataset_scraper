class CreateRequestData < ActiveRecord::Migration[5.0]
  def change
    create_table :request_data do |t|
      t.timestamps
      t.string :parsed_request
      t.integer :method
      t.json :data
      t.json :form
    end
  end
end
