module Pibrain
  module DatasetValidation
    class Validator

      INVALID_ROW = 'Row: %s, Error: %s'

      def initialize
        @valid_count = 0
        @invalid_count = 0
      end

      attr_reader :valid_count,:invalid_count,:invalid_requests

      def validate(row)
        begin
          Grammar.parse(row['parsed_request'])
          @valid_count+=1
          true
        rescue Citrus::ParseError => e
          @invalid_count+=1
          Rails.logger.error(format(INVALID_ROW, row, e))
          false
        end
      end
    end
  end
end
