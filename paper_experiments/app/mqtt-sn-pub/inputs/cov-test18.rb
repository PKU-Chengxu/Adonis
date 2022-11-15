$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_multiline_from_stdin_no_newline
    server = fake_server do |fs|
      fs.wait_for_packet(MQTT::SN::Packet::Disconnect) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          ['-t', 'topic',
          '-l',
          '-p', fs.port,
          '-h', fs.address],
          "Message 1\nMessage 2"
        )
      end
    end

    publish_packets = server.packets_received.select do |packet|
      packet.is_a?(MQTT::SN::Packet::Publish)
    end

    assert_includes_match(/Failed to find newline when reading message/, @cmd_result)
    assert_equal(['Message 1'], publish_packets.map {|p| p.data})
    assert_equal([1], publish_packets.map {|p| p.topic_id})
    assert_equal([:normal], publish_packets.map {|p| p.topic_id_type})
    assert_equal([0], publish_packets.map {|p| p.qos})
  end
end