$:.unshift(File.dirname(__FILE__))

require 'test_helper'

class MqttSnPubTest < Minitest::Test

  def test_too_long_client_id
    fake_server do |fs|
      @cmd_result = run_cmd(
        'mqtt-sn-pub',
        '-i' => 'C' * 255,
        '-T' => 10,
        '-m' => 'message',
        '-p' => fs.port,
        '-h' => fs.address
      )
    end

    assert_match(/ERROR Client id is too long/, @cmd_result[0])
  end
end