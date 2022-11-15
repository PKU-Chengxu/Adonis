$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_register_invalid_topic_name
    fake_server do |fs|
      def fs.handle_register(packet)
        MQTT::SN::Packet::Regack.new(
          :id => packet.id,
          :return_code => 2
        )
      end

      @cmd_result = run_cmd(
        'mqtt-sn-pub-cov',
        ['-t', '/!invalid%topic"name',
        '-m', 'message',
        '-p', fs.port,
        '-h', fs.address]
      ) do |cmd|
        wait_for_output_then_kill(cmd)
      end
    end

    assert_match(/ERROR REGISTER failed: Rejected: invalid topic ID/, @cmd_result[0])
  end
end