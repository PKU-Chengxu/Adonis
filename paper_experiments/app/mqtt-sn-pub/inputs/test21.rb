$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_qos_0_predefined
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub',
          '-q' => 0,
          '-T' => 127,
          '-m' => 'test_publish_qos_0_predefined',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(127, @packet.topic_id)
    assert_equal(:predefined, @packet.topic_id_type)
    assert_equal('test_publish_qos_0_predefined', @packet.data)
    assert_equal(0, @packet.qos)
    assert_equal(false, @packet.retain)
    assert_equal(0, @packet.id)
  end
end