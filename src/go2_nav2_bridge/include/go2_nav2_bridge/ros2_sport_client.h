/**********************************************************************
 Adapted from the official Unitree unitree_ros2 example:
   example/src/include/common/ros2_sport_client.h
 Only the declarations and constants needed for Go2 sport-mode motion are kept.
***********************************************************************/
#ifndef GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_
#define GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_

#include <nlohmann/json.hpp>
#include <rclcpp/rclcpp.hpp>

#include "go2_interfaces/msg/web_rtc_req.hpp"

namespace go2_nav2_bridge
{

constexpr int32_t ROBOT_SPORT_API_ID_BALANCESTAND = 1002;
constexpr int32_t ROBOT_SPORT_API_ID_STOPMOVE = 1003;
constexpr int32_t ROBOT_SPORT_API_ID_STANDUP = 1004;
constexpr int32_t ROBOT_SPORT_API_ID_EULER = 1007;
constexpr int32_t ROBOT_SPORT_API_ID_MOVE = 1008;
constexpr int32_t ROBOT_SPORT_API_ID_SWITCHJOYSTICK = 1027;
constexpr int32_t ROBOT_SPORT_API_ID_STATICWALK = 1061;
constexpr int32_t ROBOT_SPORT_API_ID_TROTRUN = 1062;
constexpr int32_t ROBOT_SPORT_API_ID_ECONOMICGAIT = 1063;
constexpr int32_t ROBOT_SPORT_API_ID_FREEWALK = 2045;
constexpr int32_t ROBOT_SPORT_API_ID_CLASSICWALK = 2049;

constexpr char ROBOT_SPORT_REQUEST_TOPIC[] = "rt/api/sport/request";

class SportClient
{
public:
  explicit SportClient(rclcpp::Node * node)
  {
    req_puber_ = node->create_publisher<go2_interfaces::msg::WebRtcReq>("/webrtc_req", 10);
  }

  void BalanceStand(go2_interfaces::msg::WebRtcReq & req);
  void StopMove(go2_interfaces::msg::WebRtcReq & req);
  void StandUp(go2_interfaces::msg::WebRtcReq & req);
  void Euler(go2_interfaces::msg::WebRtcReq & req, float roll, float pitch, float yaw);
  void Move(go2_interfaces::msg::WebRtcReq & req, float vx, float vy, float vyaw);
  void SwitchJoystick(go2_interfaces::msg::WebRtcReq & req, bool flag);
  void StaticWalk(go2_interfaces::msg::WebRtcReq & req);
  void TrotRun(go2_interfaces::msg::WebRtcReq & req);
  void EconomicGait(go2_interfaces::msg::WebRtcReq & req);
  void FreeWalk(go2_interfaces::msg::WebRtcReq & req);
  void ClassicWalk(go2_interfaces::msg::WebRtcReq & req, bool flag);

private:
  rclcpp::Publisher<go2_interfaces::msg::WebRtcReq>::SharedPtr req_puber_;
};

}  // namespace go2_nav2_bridge

#endif  // GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_
