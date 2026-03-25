#include <chrono>
#include <cstring>
#include <iostream>
#include <string>
#include <thread>

#include <unitree/robot/channel/channel_factory.hpp>
#include <unitree/robot/go2/sport/sport_client.hpp>

namespace {

constexpr float kForwardSlowVx = 0.05f;
constexpr float kForwardSlowDurationSec = 0.25f;

void PrintUsage(const char* argv0) {
  std::cout
      << "Usage: " << argv0 << " <networkInterface> (--stop | --forward-slow)\n"
      << "\n"
      << "Options:\n"
      << "  --stop           Call SportClient::StopMove() once.\n"
      << "  --forward-slow   Call SportClient::Move(vx, 0, 0) briefly, then StopMove().\n";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    PrintUsage(argv[0]);
    return 2;
  }

  const std::string network_interface = argv[1];
  const std::string mode = argv[2];

  const bool do_stop = (mode == "--stop");
  const bool do_forward_slow = (mode == "--forward-slow");
  if (!do_stop && !do_forward_slow) {
    PrintUsage(argv[0]);
    return 2;
  }

  unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

  unitree::robot::go2::SportClient sport_client;
  sport_client.SetTimeout(10.0f);
  sport_client.Init();

  if (do_stop) {
    const int32_t ret = sport_client.StopMove();
    std::cout << "StopMove ret=" << ret << std::endl;
    return (ret == 0) ? 0 : 1;
  }

  std::cout << "Forward-slow test: vx=" << kForwardSlowVx
            << " m/s for " << kForwardSlowDurationSec << " s" << std::endl;
  int32_t ret = sport_client.Move(kForwardSlowVx, 0.0f, 0.0f);
  std::cout << "Move ret=" << ret << std::endl;
  if (ret != 0) {
    return 1;
  }

  std::this_thread::sleep_for(
      std::chrono::duration<float>(kForwardSlowDurationSec));

  ret = sport_client.StopMove();
  std::cout << "StopMove ret=" << ret << std::endl;
  return (ret == 0) ? 0 : 1;
}
