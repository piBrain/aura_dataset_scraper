module Pibrain
  module DatasetValidation
    extend ActiveSupport::Autoload
    autoload :Importer
    autoload :Validator
    GRAMMAR_FILE = File.expand_path('../dataset_validation/grammar.citrus', __FILE__)
    Citrus.load(GRAMMAR_FILE) unless self.const_defined?(:Grammar)
  end
end
