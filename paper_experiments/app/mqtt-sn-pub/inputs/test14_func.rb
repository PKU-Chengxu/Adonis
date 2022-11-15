$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_from_file_too_big
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd_func(
          'mqtt-sn-pub',
          ['-t', 'topic',
          '-f', 'test_big.txt',
          '-p', fs.port,
          '-h', fs.address]
        )
      end
    end

    assert_match(/WARN  Input file is longer than the maximum message size/, @cmd_result[0])

    assert_equal(1, @packet.topic_id)
    assert_equal(:normal, @packet.topic_id_type)
    assert_equal(248, @packet.data.length)
    assert_equal(0, @packet.qos)
  end
end