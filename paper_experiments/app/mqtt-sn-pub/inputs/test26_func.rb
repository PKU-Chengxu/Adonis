$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_ipv6
    unless have_ipv6?
      skip("IPv6 is not available on this system")
    end

    server = fake_server(nil, '::1') do |fs|
      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd_func(
          'mqtt-sn-pub',
          ['-d', '-d',
          '-t', 'topic',
          '-m', 'test',
          '-p', fs.port,
          '-h', fs.address]
        )
      end
    end

    assert_includes_match(/Received  3 bytes from ::1:#{server.port}/, @cmd_result)
    assert_equal('test', @packet.data)
  end
end