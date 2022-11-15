$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_no_arguments
    @cmd_result = run_cmd_func('mqtt-sn-pub')
    assert_match(/^Usage: mqtt-sn-pub/, @cmd_result[0])
  end
end