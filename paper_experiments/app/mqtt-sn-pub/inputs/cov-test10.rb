$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_debug
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          ['-d',
          '-t', 'topic',
          '-m', 'test_publish_qos_0_debug',
          '-p', fs.port,
          '-h', fs.address]
        )
      end
    end

    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG Debug level is: 1/, @cmd_result)
    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG Sending CONNECT packet/, @cmd_result)
    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG waiting for packet/, @cmd_result)
    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG CONNACK return code: 0x00/, @cmd_result)
    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG Sending PUBLISH packet/, @cmd_result)
    assert_includes_match(/[\d\-]+ [\d\:]+ DEBUG Sending DISCONNECT packet/, @cmd_result)
  end
end