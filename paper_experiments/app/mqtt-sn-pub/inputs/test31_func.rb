$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_file_doesnt_exist
    fake_server do |fs|
      @cmd_result = run_cmd_func(
        'mqtt-sn-pub',
        '-t' => 'topic_name',
        '-f' => '/doesnt/exist',
        '-p' => fs.port,
        '-h' => fs.address
      ) do |cmd|
        wait_for_output_then_kill(cmd)
      end
    end
    assert_match(/Failed to open message file/, @cmd_result[0])
  end
end