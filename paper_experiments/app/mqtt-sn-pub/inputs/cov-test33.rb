$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_topic_name_too_long
    fake_server do |fs|
      @cmd_result = run_cmd(
        'mqtt-sn-pub-cov',
        ['-t', 'x' * 255,
        '-m', 'message',
        '-p', fs.port,
        '-h', fs.address]
      ) do |cmd|
        wait_for_output_then_kill(cmd)
      end
    end
    assert_match(/ERROR Topic name is too long/, @cmd_result[0])
  end
end