$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_from_binary_file
    ## Test for a file that contains null bytes
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub',
          ['-t', 'topic',
          '-f', 'test.bin',
          '-p', fs.port,
          '-h', fs.address]
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal(1, @packet.topic_id)
    assert_equal(:normal, @packet.topic_id_type)
    assert_equal(12, @packet.data.length)
    assert_equal("\x01\x02\x03\x04\x05\x00Hello\x00", @packet.data)
    assert_equal(0, @packet.qos)
  end
end