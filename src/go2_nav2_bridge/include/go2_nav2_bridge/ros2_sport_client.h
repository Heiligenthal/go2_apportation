/**********************************************************************
 Adapted from the official Unitree unitree_ros2 example:
   example/src/include/common/ros2_sport_client.h
 Only the declarations and constants needed for Go2 sport-mode motion are kept.
***********************************************************************/
#ifndef GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_
#define GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_

#include <nlohmann/json.hpp>
#include <rclcpp/rclcpp.hpp>

#include "unitree_api/msg/request.hpp"
#include "unitree_api/msg/response.hpp"

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

class SportClient
{
public:
  explicit SportClient(rclcpp::Node * node)
  {
    req_puber_ = node->create_publisher<unitree_api::msg::Request>("/api/sport/request", 10);
  }

  void BalanceStand(unitree_api::msg::Request & req);
  void StopMove(unitree_api::msg::Request & req);
  void StandUp(unitree_api::msg::Request & req);
  void Euler(unitree_api::msg::Request & req, float roll, float pitch, float yaw);
  void Move(unitree_api::msg::Request & req, float vx, float vy, float vyaw);
  void SwitchJoystick(unitree_api::msg::Request & req, bool flag);
  void StaticWalk(unitree_api::msg::Request & req);
  void TrotRun(unitree_api::msg::Request & req);
  void EconomicGait(unitree_api::msg::Request & req);
  void FreeWalk(unitree_api::msg::Request & req);
  void ClassicWalk(unitree_api::msg::Request & req, bool flag);

private:
  rclcpp::Publisher<unitree_api::msg::Request>::SharedPtr req_puber_;
};

}  // namespace go2_nav2_bridge

#endif  // GO2_NAV2_BRIDGE__ROS2_SPORT_CLIENT_H_
