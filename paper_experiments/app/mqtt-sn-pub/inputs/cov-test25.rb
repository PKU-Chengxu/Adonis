$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_publish_qos_1_puback_timeout
    fake_server do |fs|
      def fs.handle_publish(packet)
        nil
      end

      @packet = fs.wait_for_packet(MQTT::SN::Packet::Publish) do
        @cmd_result = run_cmd(
          'mqtt-sn-pub-cov',
          '-q' => 1,
          '-d' => '',
          '-k' => 2,
          '-t' => 'topic',
          '-m' => 'test_publish_qos_1',
          '-p' => fs.port,
          '-h' => fs.address
        )
      end
    end

    assert_includes_match(/Timed out while waiting for a PUBACK from gateway/, @cmd_result)
  end
end