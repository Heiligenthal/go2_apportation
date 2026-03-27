/**********************************************************************
 Adapted from the official Unitree unitree_ros2 example:
   example/src/src/common/ros2_sport_client.cpp
 Only the methods needed by the bridge are kept.
***********************************************************************/
#include "go2_nav2_bridge/ros2_sport_client.h"

namespace go2_nav2_bridge
{

namespace
{

void prepareSportRequest(go2_interfaces::msg::WebRtcReq & req, int32_t api_id)
{
  req.id = 0;
  req.topic = ROBOT_SPORT_REQUEST_TOPIC;
  req.api_id = api_id;
  req.priority = 0;
}

}  // namespace

void SportClient::BalanceStand(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_BALANCESTAND);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::StopMove(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_STOPMOVE);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::StandUp(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_STANDUP);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::Euler(go2_interfaces::msg::WebRtcReq & req, float roll, float pitch, float yaw)
{
  nlohmann::json js;
  js["x"] = roll;
  js["y"] = pitch;
  js["z"] = yaw;
  prepareSportRequest(req, ROBOT_SPORT_API_ID_EULER);
  req.parameter = js.dump();
  req_puber_->publish(req);
}

void SportClient::Move(go2_interfaces::msg::WebRtcReq & req, float vx, float vy, float vyaw)
{
  nlohmann::json js;
  js["x"] = vx;
  js["y"] = vy;
  js["z"] = vyaw;
  prepareSportRequest(req, ROBOT_SPORT_API_ID_MOVE);
  req.parameter = js.dump();
  req_puber_->publish(req);
}

void SportClient::SwitchJoystick(go2_interfaces::msg::WebRtcReq & req, bool flag)
{
  nlohmann::json js;
  js["data"] = flag;
  prepareSportRequest(req, ROBOT_SPORT_API_ID_SWITCHJOYSTICK);
  req.parameter = js.dump();
  req_puber_->publish(req);
}

void SportClient::StaticWalk(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_STATICWALK);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::TrotRun(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_TROTRUN);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::EconomicGait(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_ECONOMICGAIT);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::FreeWalk(go2_interfaces::msg::WebRtcReq & req)
{
  prepareSportRequest(req, ROBOT_SPORT_API_ID_FREEWALK);
  req.parameter.clear();
  req_puber_->publish(req);
}

void SportClient::ClassicWalk(go2_interfaces::msg::WebRtcReq & req, bool flag)
{
  nlohmann::json js;
  js["data"] = flag;
  prepareSportRequest(req, ROBOT_SPORT_API_ID_CLASSICWALK);
  req.parameter = js.dump();
  req_puber_->publish(req);
}

}  // namespace go2_nav2_bridge
