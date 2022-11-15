$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_payload_too_big
    fake_server do |fs|
      @cmd_result = run_cmd(
        'mqtt-sn-pub',
        ['-t', 'topic',
        '-m', 'm' * 255,
        '-p', fs.port,
        '-h', fs.address]
      )
    end
    assert_match(/Payload is too big/, @cmd_result[0])
  end
end