$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_invalid_qos
    @cmd_result = run_cmd(
      'mqtt-sn-pub',
      '-q' => '2',
      '-t' => 'topic',
      '-m' => 'message'
    )
    assert_match(/Only QoS level 0, 1 or -1 is supported/, @cmd_result[0])
  end
end