describe Pibrain::DatasetValidation::Importer do
  let(:object) { described_class.new(Aws::S3::Resource.new) }
  subject { object }

  let(:data_dir) { 'fake/path' }

  let(:valid_dummy_data) do
    JSON.unparse({
      'arguments' => {
        'data' => '{"user_stuff": foobar}',
        'form' => 'userStuff=foobar'
      },
      'method' => 'PUT',
      'url' => 'https://www.example.com',
      'parsed_request' => 'PUT https://www.example.com/<user_insert>/<user_insert>'
    })
  end

  let(:invalid_dummy_data) do
    JSON.unparse({
      'arguments' => {
        'data' => 'PURE_GARBAGE',
        'form' => 'PURE_GARBAGE'
      },
      'method' => 'ALP',
      'url' => 'https://www.example.com',
      'parsed_request' => 'ALP https://www.example.com/<user_insert>/<user_insert>'
    })
  end

  let(:dummy_dataset) {[invalid_dummy_data,valid_dummy_data]}
  let(:dummy_resource) { double(:dummy_resource, bucket: dummy_bucket) }
  let(:dummy_bucket) { double(:dummy_bucket, objects: dummy_objects) }
  let(:dummy_object_summary) { double(:dummy_object, get: dummy_full_object) }
  let(:dummy_objects) { [dummy_object_summary] }
  let(:dummy_full_object) { double(:dummy_full_object, body:dummy_dataset) }

  before { expect(Aws::S3::Resource).to receive(:new).and_return(dummy_resource) }

  it 'persists valid data to the database' do
    expect{subject.process_files}.to change(RequestDatum,:count).from(0).to(1)
  end
end
