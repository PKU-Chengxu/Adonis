$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_23char_client_id
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Connect) do
        @cmd_result = run_cmd_func(
          'mqtt-sn-pub',
          '-i' => 'ABCDEFGHIJKLMNOPQRSTUVW',
          '-T' => 10,
          '-m' => 'message',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal('ABCDEFGHIJKLMNOPQRSTUVW', @packet.client_id)
    assert_equal(10, @packet.keep_alive)
    assert_equal(true, @packet.clean_session)
  end
end