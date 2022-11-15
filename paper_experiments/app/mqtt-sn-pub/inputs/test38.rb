$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_disconnect_after_publish_with_sleep
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Disconnect) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub',
          '-e' => 3600,
          '-T' => 10,
          '-m' => 'message',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(MQTT::SN::Packet::Disconnect, @packet.class)
    assert_equal(3600, @packet.duration)
  end
end