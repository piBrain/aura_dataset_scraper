module Pibrain
  module DatasetValidation
    class Importer

      def initialize(s3_bucket)
        @validator ||= Validator.new
        @s3_bucket ||= s3_bucket
      end

      def process_files
        s3_bucket.objects(prefix: 'datasets').each do |obj|
          obj.get.body.each do |data_row|
            import(JSON.parse(data_row)) if validator.validate(JSON.parse(data_row))
          end
        end
        Rails.logger.info(
          "Number Valid Rows: #{validator.valid_count}
          Number Invalid Rows: #{validator.invalid_count}"
        )
      end

      private
      attr_reader :validator, :s3_bucket
      def import(row)
        RequestDatum.new(
          parsed_request: row['parsed_request'],
          method: row['method'],
          data: row['arguments']['data'],
          form: row['arguments']['form'],
          createdAt: DateTime.now,
          updatedAt: DateTime.now
        ).save!
      end
    end
  end
end
