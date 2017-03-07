namespace :pibrain do
  desc 'Download flat files from s3, validate and import into database.'
  task :import_scrape_data => :environment do
    Pibrain::DatasetValidation::Importer
      .new(Aws::S3::Resource.new.bucket('pibrain.dev.general'))
      .process_files
  end
end
