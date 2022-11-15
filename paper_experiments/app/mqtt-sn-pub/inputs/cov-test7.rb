$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_no_connack
    fake_server do |fs|
      def fs.handle_connect(packet)
        MQTT::SN::Packet::Disconnect.new
      end

      fs.wait_for_packet(MQTT::SN::Packet::Connect) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          '-T' => 10,
          '-m' => 'message',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_match(/ERROR Was expecting CONNACK packet but received: DISCONNECT/, @cmd_result[0])
  end
end