$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test
  def test_usage
    @cmd_result = run_cmd('mqtt-sn-pub-cov', '-?')
    assert_match(/^Usage: mqtt-sn-pub/, @cmd_result[0])
  end
end