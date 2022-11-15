$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_default_client_id
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Connect) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub',
          '-T' => 10,
          '-m' => 'message',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_match(/^mqtt-sn-tools-(\d+)$/, @packet.client_id)
    assert_equal(10, @packet.keep_alive)
    assert_equal(true, @packet.clean_session)
  end
end