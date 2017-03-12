class RequestFoundAt < ActiveRecord::Migration[5.0]
  def change
    change_table :RequestData do |t|
      t.string :found_at, null: true
    end
  end
end
