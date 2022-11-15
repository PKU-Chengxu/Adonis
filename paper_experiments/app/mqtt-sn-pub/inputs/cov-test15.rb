$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_from_file_hyphen
    fake_server do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          ['-t', 'topic',
          '-f', '-',
          '-p', fs.port,
          '-h', fs.address],
          'Message from file -'
        )
      end
    end

    assert_empty(@cmd_result)
    assert_equal('Message from file -', @packet.data)
  end
end