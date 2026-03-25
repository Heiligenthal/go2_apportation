/**********************************************************************
 Adapted from the official Unitree unitree_ros2 example:
   example/src/src/common/ros2_sport_client.cpp
 Only the methods needed by the bridge are kept.
***********************************************************************/
#include "go2_nav2_bridge/ros2_sport_client.h"

namespace go2_nav2_bridge
{

void SportClient::BalanceStand(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_BALANCESTAND;
  req_puber_->publish(req);
}

void SportClient::StopMove(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_STOPMOVE;
  req_puber_->publish(req);
}

void SportClient::StandUp(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_STANDUP;
  req_puber_->publish(req);
}

void SportClient::Euler(unitree_api::msg::Request & req, float roll, float pitch, float yaw)
{
  nlohmann::json js;
  js["x"] = roll;
  js["y"] = pitch;
  js["z"] = yaw;
  req.parameter = js.dump();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_EULER;
  req_puber_->publish(req);
}

void SportClient::Move(unitree_api::msg::Request & req, float vx, float vy, float vyaw)
{
  nlohmann::json js;
  js["x"] = vx;
  js["y"] = vy;
  js["z"] = vyaw;
  req.parameter = js.dump();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_MOVE;
  req_puber_->publish(req);
}

void SportClient::SwitchJoystick(unitree_api::msg::Request & req, bool flag)
{
  nlohmann::json js;
  js["data"] = flag;
  req.parameter = js.dump();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_SWITCHJOYSTICK;
  req_puber_->publish(req);
}

void SportClient::StaticWalk(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_STATICWALK;
  req_puber_->publish(req);
}

void SportClient::TrotRun(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_TROTRUN;
  req_puber_->publish(req);
}

void SportClient::EconomicGait(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_ECONOMICGAIT;
  req_puber_->publish(req);
}

void SportClient::FreeWalk(unitree_api::msg::Request & req)
{
  req.parameter.clear();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_FREEWALK;
  req_puber_->publish(req);
}

void SportClient::ClassicWalk(unitree_api::msg::Request & req, bool flag)
{
  nlohmann::json js;
  js["data"] = flag;
  req.parameter = js.dump();
  req.header.identity.api_id = ROBOT_SPORT_API_ID_CLASSICWALK;
  req_puber_->publish(req);
}

}  // namespace go2_nav2_bridge
