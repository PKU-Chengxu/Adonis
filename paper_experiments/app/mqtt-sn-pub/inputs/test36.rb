$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_hostname_lookup_fail
    @cmd_result = run_cmd(
      'mqtt-sn-pub',
      ['-t', 'topic',
      '-m', 'message',
      '-p', '29567',
      '-h', '!(invalid)']
    ) do |cmd|
      wait_for_output_then_kill(cmd)
    end

    assert_match(/nodename nor servname provided, or not known|Name or service not known/, @cmd_result[0])
  end
end