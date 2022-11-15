$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_both_topic_name_and_id
    @cmd_result = run_cmd(
      'mqtt-sn-pub',
      '-t' => 'topic_name',
      '-T' => 10,
      '-m' => 'message'
    )
    assert_match(/Please provide either a topic id or a topic name, not both/, @cmd_result[0])
  end
end