class CreateRequestData < ActiveRecord::Migration[5.0]
  def change
    change_table :RequestData do |t|
      t.primary_key :id
    end
  end
end
