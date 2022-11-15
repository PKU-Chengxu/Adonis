$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_both_qos_n1_topic_name
    @cmd_result = run_cmd(
      'mqtt-sn-pub-cov',
      '-q' => -1,
      '-t' => 'topic_name',
      '-m' => 'message'
    )
    assert_match(/Either a pre-defined topic id or a short topic name must be given for QoS -1/, @cmd_result[0])
  end
end