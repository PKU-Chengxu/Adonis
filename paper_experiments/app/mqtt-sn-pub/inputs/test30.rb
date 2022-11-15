$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_both_message_and_file
    @cmd_result = run_cmd(
      'mqtt-sn-pub',
      '-t' => 'topic_name',
      '-m' => 'message',
      '-f' => '/dev/zero'
    )
    assert_match(/Please provide either message data or a message file, not both/, @cmd_result[0])
  end
end