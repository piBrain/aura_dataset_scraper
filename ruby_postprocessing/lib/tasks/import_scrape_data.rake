namespace :pibrain do
  task :import_scrape_data => :environment do
    Pibrain::DatasetValidation::Importer
      .new(Aws::S3::Resource.new.bucket('pibrain.dev.general'))
      .process_files
  end
end
