$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_disconnect_duration_warning
    fake_server do |fs|
      def fs.handle_disconnect(packet)
        MQTT::SN::Packet::Disconnect.new(
          :duration => 10
        )
      end

      @cmd_result = run_cmd_func(
        'mqtt-sn-pub',
        '-T' => 10,
        '-m' => 'message',
        '-p' => fs.port,
        '-h' => fs.address
      )
    end

    assert_match(/DISCONNECT warning. Gateway returned duration in disconnect packet/, @cmd_result[0])
  end
end