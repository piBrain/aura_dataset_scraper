class AddValidatedColumn < ActiveRecord::Migration[5.0]
  def change
    change_table :RequestData do |t|
      t.boolean :validated, null: false, default: false
    end
  end
end
