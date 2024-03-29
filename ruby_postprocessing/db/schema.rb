# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20170315014343) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "RequestData", force: :cascade do |t|
    t.time     "created_at"
    t.time     "updated_at"
    t.string   "parsed_request", limit: 255
    t.json     "data"
    t.json     "form",                       default: {},    null: false
    t.datetime "createdAt",                                  null: false
    t.datetime "updatedAt",                                  null: false
    t.boolean  "validated",                  default: false, null: false
    t.string   "found_at",                   default: "",    null: false
    t.string   "method",                                     null: false
  end

  create_table "SequelizeMeta", primary_key: "name", id: :string, limit: 255, force: :cascade do |t|
  end

end
