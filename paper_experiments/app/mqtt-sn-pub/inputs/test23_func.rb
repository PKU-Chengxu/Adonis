$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_qos_0_empty
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd_func(
          'mqtt-sn-pub',
          ['-r', '-n',
          '-t', 'topic',
          '-p', fs.port,
          '-h', fs.address]
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(1, @packet.topic_id)
    assert_equal(:normal, @packet.topic_id_type)
    assert_equal('', @packet.data)
    assert_equal(0, @packet.qos)
    assert_equal(true, @packet.retain)
    assert_equal(0, @packet.id)
  end
end