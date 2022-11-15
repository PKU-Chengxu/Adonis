$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_qos_1
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd_func(
          'mqtt-sn-pub',
          '-q' => 1,
          '-t' => 'topic',
          '-m' => 'test_publish_qos_1',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(1, @packet.topic_id)
    assert_equal(:normal, @packet.topic_id_type)
    assert_equal('test_publish_qos_1', @packet.data)
    assert_equal(1, @packet.qos)
    assert_equal(false, @packet.retain)
    assert_equal(2, @packet.id) # REGISTER for topic ID has id 1
  end
end