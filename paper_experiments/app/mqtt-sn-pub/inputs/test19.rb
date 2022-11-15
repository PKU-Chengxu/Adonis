$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_qos_0
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub',
          '-q' => 0,
          '-t' => 'topic',
          '-m' => 'test_publish_qos_0',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(1, @packet.topic_id)
    assert_equal(:normal, @packet.topic_id_type)
    assert_equal('test_publish_qos_0', @packet.data)
    assert_equal(0, @packet.qos)
    assert_equal(false, @packet.retain)
    assert_equal(0, @packet.id)
  end
end