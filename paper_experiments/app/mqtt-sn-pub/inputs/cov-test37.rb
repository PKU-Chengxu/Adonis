$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_disconnect_after_publish
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Disconnect) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          '-T' => 10,
          '-m' => 'message',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_kind_of(MQTT::SN::Packet::Disconnect, @packet)
    assert_nil(@packet.duration)
  end
end