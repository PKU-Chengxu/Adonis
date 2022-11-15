$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_connect_fail
    skip("Unable to get this test to run reliably")
#     @cmd_result = run_cmd(
#       'mqtt-sn-pub-cov',
#       ['-t', 'topic',
#       '-m', 'message',
#       '-h', '0.0.0.1',
#       '-p', '29567']
#     ) do |cmd|
#       wait_for_output_then_kill(cmd)
#     end
# 
#     assert_match(/ERROR Could not connect to remote host/, @cmd_result[0])
  end
end