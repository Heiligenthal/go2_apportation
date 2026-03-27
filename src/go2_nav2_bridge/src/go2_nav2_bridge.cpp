#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <string>

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/vector3.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "std_msgs/msg/string.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2_ros/transform_broadcaster.h"
#include "go2_interfaces/msg/sport_mode_state.hpp"

#include "go2_nav2_bridge/ros2_sport_client.h"

using namespace std::chrono_literals;

namespace go2_nav2_bridge
{

enum class GaitMode
{
  kNoChange,
  kStaticWalk,
  kTrotRun,
  kEconomicGait,
  kFreeWalk,
  kClassicWalk,
};

enum class ControlMode
{
  kVelocityMove,
  kBalanceStand,
};

class Go2Nav2Bridge : public rclcpp::Node
{
public:
  Go2Nav2Bridge()
  : Node("go2_nav2_bridge"), sport_client_(this)
  {
    cmd_vel_topic_ = declare_parameter<std::string>("cmd_vel_topic", "/cmd_vel_nav2");
    sport_state_topic_ = declare_parameter<std::string>("sport_state_topic", "lf/sportmodestate");
    control_mode_topic_ = declare_parameter<std::string>("control_mode_topic", "/control_mode_cmd");
    look_yaw_delta_topic_ = declare_parameter<std::string>("look_yaw_delta_topic", "/look_yaw_delta");
    balance_rpy_topic_ = declare_parameter<std::string>("balance_rpy_topic", "/balance_rpy_cmd");
    real_base_frame_ = declare_parameter<std::string>("real_base_frame", "base_link");
    nav2_base_frame_ = declare_parameter<std::string>("nav2_base_frame", "base_link_nav2");
    legacy_nav2_odom_topic_ = declare_parameter<std::string>("legacy_nav2_odom_topic", "/odom_nav2");
    legacy_nav2_odom_frame_ = declare_parameter<std::string>("legacy_nav2_odom_frame", "odom_nav2");
    publish_legacy_nav2_odom_ = declare_parameter<bool>("publish_legacy_nav2_odom", false);
    publish_virtual_base_tf_ = declare_parameter<bool>("publish_virtual_base_tf", true);

    watchdog_timeout_sec_ = declare_parameter<double>("watchdog_timeout_sec", 0.30);
    sport_state_timeout_sec_ = declare_parameter<double>("sport_state_timeout_sec", 0.50);
    startup_state_warn_delay_sec_ = declare_parameter<double>("startup_state_warn_delay_sec", 2.0);
    diagnostics_period_sec_ = declare_parameter<double>("diagnostics_period_sec", 1.0);
    command_publish_rate_hz_ = declare_parameter<double>("command_publish_rate_hz", 20.0);
    max_vx_ = declare_parameter<double>("max_vx", 0.40);
    max_vy_ = declare_parameter<double>("max_vy", 0.25);
    max_wz_ = declare_parameter<double>("max_wz", 0.60);
    look_yaw_kp_ = declare_parameter<double>("look_yaw_kp", 1.5);
    nav2_linear_y_enabled_ = declare_parameter<bool>("nav2_linear_y_enabled", false);
    require_standup_on_start_ = declare_parameter<bool>("require_standup_on_start", false);
    enable_joystick_override_ = declare_parameter<bool>("enable_joystick_override", false);
    gait_mode_ = gaitFromString(declare_parameter<std::string>("gait_mode", "no_change"));

    auto qos = rclcpp::QoS(rclcpp::KeepLast(20));

    cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      cmd_vel_topic_, qos,
      std::bind(&Go2Nav2Bridge::cmdVelCallback, this, std::placeholders::_1));

    sport_state_sub_ = create_subscription<go2_interfaces::msg::SportModeState>(
      sport_state_topic_, qos,
      std::bind(&Go2Nav2Bridge::sportStateCallback, this, std::placeholders::_1));

    control_mode_sub_ = create_subscription<std_msgs::msg::String>(
      control_mode_topic_, qos,
      std::bind(&Go2Nav2Bridge::controlModeCallback, this, std::placeholders::_1));

    look_yaw_delta_sub_ = create_subscription<std_msgs::msg::Float32>(
      look_yaw_delta_topic_, qos,
      std::bind(&Go2Nav2Bridge::lookYawDeltaCallback, this, std::placeholders::_1));

    balance_rpy_sub_ = create_subscription<geometry_msgs::msg::Vector3>(
      balance_rpy_topic_, qos,
      std::bind(&Go2Nav2Bridge::balanceRpyCallback, this, std::placeholders::_1));

    if (publish_legacy_nav2_odom_) {
      legacy_nav2_odom_pub_ = create_publisher<nav_msgs::msg::Odometry>(legacy_nav2_odom_topic_, qos);
    }
    if (publish_virtual_base_tf_) {
      tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    }

    const auto period = std::chrono::duration<double>(1.0 / std::max(1.0, command_publish_rate_hz_));
    control_timer_ = create_wall_timer(
      std::chrono::duration_cast<std::chrono::milliseconds>(period),
      std::bind(&Go2Nav2Bridge::controlLoop, this));

    const auto diagnostics_period = std::chrono::duration<double>(std::max(0.2, diagnostics_period_sec_));
    diagnostics_timer_ = create_wall_timer(
      std::chrono::duration_cast<std::chrono::milliseconds>(diagnostics_period),
      std::bind(&Go2Nav2Bridge::diagnosticsLoop, this));

    last_control_time_ = now();
    last_cmd_time_ = now();
    start_time_ = now();

    if (require_standup_on_start_) {
      sport_client_.StandUp(req_);
    }
    if (enable_joystick_override_) {
      sport_client_.SwitchJoystick(req_, true);
    }
    applyConfiguredGait();

    RCLCPP_INFO(get_logger(), "go2_nav2_bridge ready");
    RCLCPP_INFO(
      get_logger(),
      "cmd_vel=%s sport_state=%s control_mode=%s look_topic=%s balance_topic=%s",
      cmd_vel_topic_.c_str(), sport_state_topic_.c_str(), control_mode_topic_.c_str(),
      look_yaw_delta_topic_.c_str(), balance_rpy_topic_.c_str());
    RCLCPP_INFO(
      get_logger(),
      "real_base_frame=%s nav2_base_frame=%s publish_virtual_base_tf=%s publish_legacy_nav2_odom=%s",
      real_base_frame_.c_str(), nav2_base_frame_.c_str(),
      publish_virtual_base_tf_ ? "true" : "false", publish_legacy_nav2_odom_ ? "true" : "false");
    RCLCPP_INFO(
      get_logger(),
      "limits: max_vx=%.3f max_vy=%.3f max_wz=%.3f watchdog=%.2fs look_yaw_kp=%.3f",
      max_vx_, max_vy_, max_wz_, watchdog_timeout_sec_, look_yaw_kp_);
    RCLCPP_INFO(
      get_logger(),
      "runtime hardening: sport_state_timeout=%.2fs startup_state_warn_delay=%.2fs diagnostics_period=%.2fs",
      sport_state_timeout_sec_, startup_state_warn_delay_sec_, diagnostics_period_sec_);
    RCLCPP_INFO(
      get_logger(),
      "Nav2 semantics: angular.z integrates virtual yaw; translation stays consistent in map; real yaw follows look control.");
    if (publish_legacy_nav2_odom_) {
      RCLCPP_WARN(
        get_logger(),
        "Legacy nav2 odom output is enabled on %s (%s -> %s). Productive default is TF-only base_link -> base_link_nav2.",
        legacy_nav2_odom_topic_.c_str(), legacy_nav2_odom_frame_.c_str(), nav2_base_frame_.c_str());
    }
    RCLCPP_WARN(
      get_logger(),
      "If control_mode switches to balance_stand while Nav2 is active, Nav2 task cancel ownership remains outside this bridge.");
  }

private:
  static double clamp(double value, double lo, double hi)
  {
    return std::max(lo, std::min(value, hi));
  }

  static double normalizeAngle(double angle)
  {
    while (angle > M_PI) {
      angle -= 2.0 * M_PI;
    }
    while (angle < -M_PI) {
      angle += 2.0 * M_PI;
    }
    return angle;
  }

  static GaitMode gaitFromString(const std::string & value)
  {
    if (value == "static_walk") return GaitMode::kStaticWalk;
    if (value == "trot_run") return GaitMode::kTrotRun;
    if (value == "economic_gait") return GaitMode::kEconomicGait;
    if (value == "free_walk") return GaitMode::kFreeWalk;
    if (value == "classic_walk") return GaitMode::kClassicWalk;
    return GaitMode::kNoChange;
  }

  void applyConfiguredGait()
  {
    switch (gait_mode_) {
      case GaitMode::kStaticWalk:
        sport_client_.StaticWalk(req_);
        break;
      case GaitMode::kTrotRun:
        sport_client_.TrotRun(req_);
        break;
      case GaitMode::kEconomicGait:
        sport_client_.EconomicGait(req_);
        break;
      case GaitMode::kFreeWalk:
        sport_client_.FreeWalk(req_);
        break;
      case GaitMode::kClassicWalk:
        sport_client_.ClassicWalk(req_, true);
        break;
      case GaitMode::kNoChange:
      default:
        break;
    }
  }

  void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    latest_nav_cmd_ = *msg;
    last_cmd_time_ = now();
    nav_cmd_received_ = true;

    if (!state_received_ && !warned_cmd_before_state_) {
      RCLCPP_WARN(
        get_logger(),
        "Received /cmd_vel_nav2 before any sport mode state arrived. Bridge will not command motion until lf/sportmodestate is available.");
      warned_cmd_before_state_ = true;
    }
  }

  void sportStateCallback(const go2_interfaces::msg::SportModeState::SharedPtr msg)
  {
    last_state_ = *msg;
    state_received_ = true;
    last_state_time_ = now();

    real_x_ = msg->position[0];
    real_y_ = msg->position[1];
    real_z_ = msg->position[2];
    real_vx_world_ = msg->velocity[0];
    real_vy_world_ = msg->velocity[1];
    real_vz_world_ = msg->velocity[2];
    real_yaw_ = msg->imu_state.rpy[2];

    if (!yaw_initialized_) {
      fake_yaw_ = real_yaw_;
      look_yaw_target_world_ = real_yaw_;
      yaw_initialized_ = true;
      RCLCPP_INFO(get_logger(), "Initialized virtual yaw from real yaw %.3f rad", real_yaw_);
    }

    if (!sport_state_fresh_logged_) {
      RCLCPP_INFO(get_logger(), "lf/sportmodestate is now available and fresh");
      sport_state_fresh_logged_ = true;
    }
    sport_state_timeout_logged_ = false;

    publishBridgeOutputs(now());
  }

  void controlModeCallback(const std_msgs::msg::String::SharedPtr msg)
  {
    const std::string & value = msg->data;
    if (value == "velocity_move") {
      if (control_mode_ != ControlMode::kVelocityMove) {
        control_mode_ = ControlMode::kVelocityMove;
        mode_just_changed_ = true;
        look_yaw_target_world_ = real_yaw_;
        stop_command_sent_ = false;
        warned_balance_cmd_in_velocity_mode_ = false;
        warned_look_in_balance_mode_ = false;
        RCLCPP_INFO(get_logger(), "Switched to velocity_move");
      }
      return;
    }

    if (value == "balance_stand") {
      if (control_mode_ != ControlMode::kBalanceStand) {
        control_mode_ = ControlMode::kBalanceStand;
        mode_just_changed_ = true;
        balance_yaw_ = real_yaw_;
        stop_command_sent_ = false;
        warned_balance_cmd_in_velocity_mode_ = false;
        warned_look_in_balance_mode_ = false;
        RCLCPP_INFO(get_logger(), "Switched to balance_stand");
      }
      return;
    }

    RCLCPP_WARN(get_logger(), "Unknown control mode '%s'", value.c_str());
  }

  void lookYawDeltaCallback(const std_msgs::msg::Float32::SharedPtr msg)
  {
    if (!yaw_initialized_) {
      RCLCPP_WARN(get_logger(), "Ignoring look_yaw_delta before first state message");
      return;
    }
    if (control_mode_ == ControlMode::kBalanceStand && !warned_look_in_balance_mode_) {
      RCLCPP_WARN(
        get_logger(),
        "Received /look_yaw_delta while in balance_stand. Virtual path is unaffected; balance yaw is driven by /balance_rpy_cmd.");
      warned_look_in_balance_mode_ = true;
    }
    look_yaw_target_world_ = normalizeAngle(look_yaw_target_world_ + static_cast<double>(msg->data));
  }

  void balanceRpyCallback(const geometry_msgs::msg::Vector3::SharedPtr msg)
  {
    if (control_mode_ == ControlMode::kVelocityMove && !warned_balance_cmd_in_velocity_mode_) {
      RCLCPP_WARN(
        get_logger(),
        "Received /balance_rpy_cmd while still in velocity_move. Values are stored but only applied in balance_stand.");
      warned_balance_cmd_in_velocity_mode_ = true;
    }
    balance_roll_ = msg->x;
    balance_pitch_ = msg->y;
    balance_yaw_ = msg->z;
  }

  void controlLoop()
  {
    const auto now_time = now();
    const double dt = std::max(0.0, (now_time - last_control_time_).seconds());
    last_control_time_ = now_time;

    if (!state_received_ || !yaw_initialized_) {
      return;
    }

    if (!isSportStateFresh(now_time)) {
      if (!sport_state_timeout_logged_) {
        RCLCPP_WARN(
          get_logger(),
          "lf/sportmodestate has timed out (age=%.3fs > %.3fs). Sending StopMove and freezing bridge outputs until state recovers.",
          (now_time - last_state_time_).seconds(), sport_state_timeout_sec_);
        sport_state_timeout_logged_ = true;
      }
      sendStopOnce();
      publishBridgeOutputs(now_time);
      return;
    }

    if (control_mode_ == ControlMode::kVelocityMove) {
      runVelocityMove(now_time, dt);
    } else {
      runBalanceStand();
    }

    publishBridgeOutputs(now_time);
  }

  void diagnosticsLoop()
  {
    const auto now_time = now();

    if (!state_received_) {
      if ((now_time - start_time_).seconds() >= startup_state_warn_delay_sec_ && !startup_state_warned_) {
        RCLCPP_WARN(
          get_logger(),
          "No lf/sportmodestate received %.2fs after startup. Bridge cannot command motion or publish a meaningful virtual base without real robot state.",
          (now_time - start_time_).seconds());
        startup_state_warned_ = true;
      }
      return;
    }

    if (isSportStateFresh(now_time)) {
      if (sport_state_timeout_logged_) {
        RCLCPP_INFO(get_logger(), "lf/sportmodestate recovered; bridge outputs are live again");
        sport_state_timeout_logged_ = false;
      }
      return;
    }
  }

  void runVelocityMove(const rclcpp::Time & now_time, double dt)
  {
    if (mode_just_changed_) {
      sendStopOnce();
      mode_just_changed_ = false;
    }

    const double age = (now_time - last_cmd_time_).seconds();
    const bool command_fresh = age <= watchdog_timeout_sec_;
    if (command_fresh != last_command_fresh_) {
      if (command_fresh) {
        RCLCPP_INFO(get_logger(), "cmd_vel_nav2 stream is fresh again");
      } else {
        RCLCPP_WARN(
          get_logger(),
          "cmd_vel_nav2 watchdog expired after %.3fs; stopping motion commands",
          age);
      }
      last_command_fresh_ = command_fresh;
    }

    if (!command_fresh) {
      sendStopOnce();
      return;
    }

    const double nav_vx = clamp(latest_nav_cmd_.linear.x, -max_vx_, max_vx_);
    const double nav_vy = nav2_linear_y_enabled_
      ? clamp(latest_nav_cmd_.linear.y, -max_vy_, max_vy_)
      : 0.0;
    const double nav_wz = clamp(latest_nav_cmd_.angular.z, -max_wz_, max_wz_);

    if (!nav2_linear_y_enabled_ && std::abs(latest_nav_cmd_.linear.y) > 1e-4 && !warned_linear_y_ignored_) {
      RCLCPP_WARN(
        get_logger(),
        "Received non-zero linear.y on /cmd_vel_nav2 while nav2_linear_y_enabled=false. Ignoring lateral velocity to enforce non-holonomic runtime behavior.");
      warned_linear_y_ignored_ = true;
    } else if (std::abs(latest_nav_cmd_.linear.y) <= 1e-4) {
      warned_linear_y_ignored_ = false;
    }

    fake_yaw_ = normalizeAngle(fake_yaw_ + nav_wz * dt);

    const double world_vx = std::cos(fake_yaw_) * nav_vx - std::sin(fake_yaw_) * nav_vy;
    const double world_vy = std::sin(fake_yaw_) * nav_vx + std::cos(fake_yaw_) * nav_vy;

    const double body_vx = std::cos(real_yaw_) * world_vx + std::sin(real_yaw_) * world_vy;
    const double body_vy = -std::sin(real_yaw_) * world_vx + std::cos(real_yaw_) * world_vy;

    const double yaw_error = normalizeAngle(look_yaw_target_world_ - real_yaw_);
    const double body_wz = clamp(look_yaw_kp_ * yaw_error, -max_wz_, max_wz_);

    const double final_body_vx = clamp(body_vx, -max_vx_, max_vx_);
    const double final_body_vy = clamp(body_vy, -max_vy_, max_vy_);

    const bool effectively_stopped =
      std::abs(final_body_vx) < 1e-6 &&
      std::abs(final_body_vy) < 1e-6 &&
      std::abs(body_wz) < 1e-6;

    if (effectively_stopped) {
      sendStopOnce();
      return;
    }

    sport_client_.Move(
      req_, static_cast<float>(final_body_vx), static_cast<float>(final_body_vy),
      static_cast<float>(body_wz));
    stop_command_sent_ = false;
  }

  void runBalanceStand()
  {
    if (mode_just_changed_) {
      sendStopOnce();
      sport_client_.BalanceStand(req_);
      mode_just_changed_ = false;
    }

    sport_client_.Euler(
      req_, static_cast<float>(balance_roll_), static_cast<float>(balance_pitch_),
      static_cast<float>(balance_yaw_));
    stop_command_sent_ = false;
  }

  void sendStopOnce()
  {
    if (stop_command_sent_) {
      return;
    }
    sport_client_.StopMove(req_);
    stop_command_sent_ = true;
  }

  void publishBridgeOutputs(const rclcpp::Time & stamp)
  {
    publishVirtualBaseTf(stamp);
    publishLegacyNav2Odometry(stamp);
  }

  bool isSportStateFresh(const rclcpp::Time & now_time) const
  {
    if (!state_received_) {
      return false;
    }
    return (now_time - last_state_time_).seconds() <= sport_state_timeout_sec_;
  }

  void publishVirtualBaseTf(const rclcpp::Time & stamp)
  {
    if (!publish_virtual_base_tf_ || !tf_broadcaster_) {
      return;
    }

    geometry_msgs::msg::TransformStamped tf_msg;
    tf_msg.header.stamp = stamp;
    tf_msg.header.frame_id = real_base_frame_;
    tf_msg.child_frame_id = nav2_base_frame_;
    tf_msg.transform.translation.x = 0.0;
    tf_msg.transform.translation.y = 0.0;
    tf_msg.transform.translation.z = 0.0;

    tf2::Quaternion q;
    q.setRPY(0.0, 0.0, normalizeAngle(fake_yaw_ - real_yaw_));
    tf_msg.transform.rotation.x = q.x();
    tf_msg.transform.rotation.y = q.y();
    tf_msg.transform.rotation.z = q.z();
    tf_msg.transform.rotation.w = q.w();

    tf_broadcaster_->sendTransform(tf_msg);
  }

  void publishLegacyNav2Odometry(const rclcpp::Time & stamp)
  {
    if (!publish_legacy_nav2_odom_ || !legacy_nav2_odom_pub_) {
      return;
    }

    nav_msgs::msg::Odometry odom;
    odom.header.stamp = stamp;
    odom.header.frame_id = legacy_nav2_odom_frame_;
    odom.child_frame_id = nav2_base_frame_;

    odom.pose.pose.position.x = real_x_;
    odom.pose.pose.position.y = real_y_;
    odom.pose.pose.position.z = real_z_;

    tf2::Quaternion q;
    q.setRPY(0.0, 0.0, fake_yaw_);
    odom.pose.pose.orientation.x = q.x();
    odom.pose.pose.orientation.y = q.y();
    odom.pose.pose.orientation.z = q.z();
    odom.pose.pose.orientation.w = q.w();

    odom.twist.twist.linear.x =
      std::cos(fake_yaw_) * real_vx_world_ + std::sin(fake_yaw_) * real_vy_world_;
    odom.twist.twist.linear.y =
      -std::sin(fake_yaw_) * real_vx_world_ + std::cos(fake_yaw_) * real_vy_world_;
    odom.twist.twist.linear.z = real_vz_world_;
    const double nav_cmd_age = (stamp - last_cmd_time_).seconds();
    odom.twist.twist.angular.z = nav_cmd_age <= watchdog_timeout_sec_ ? latest_nav_cmd_.angular.z : 0.0;

    legacy_nav2_odom_pub_->publish(odom);
  }

  SportClient sport_client_;
  go2_interfaces::msg::WebRtcReq req_{};
  go2_interfaces::msg::SportModeState last_state_{};
  geometry_msgs::msg::Twist latest_nav_cmd_{};
  bool state_received_{false};
  bool yaw_initialized_{false};
  bool mode_just_changed_{false};
  bool stop_command_sent_{false};
  bool last_command_fresh_{false};
  bool nav_cmd_received_{false};
  bool warned_cmd_before_state_{false};
  bool warned_linear_y_ignored_{false};
  bool warned_look_in_balance_mode_{false};
  bool warned_balance_cmd_in_velocity_mode_{false};
  bool startup_state_warned_{false};
  bool sport_state_timeout_logged_{false};
  bool sport_state_fresh_logged_{false};

  std::string cmd_vel_topic_;
  std::string sport_state_topic_;
  std::string control_mode_topic_;
  std::string look_yaw_delta_topic_;
  std::string balance_rpy_topic_;
  std::string real_base_frame_;
  std::string nav2_base_frame_;
  std::string legacy_nav2_odom_topic_;
  std::string legacy_nav2_odom_frame_;
  bool publish_legacy_nav2_odom_{false};
  bool publish_virtual_base_tf_{true};
  double watchdog_timeout_sec_{0.30};
  double sport_state_timeout_sec_{0.50};
  double startup_state_warn_delay_sec_{2.0};
  double diagnostics_period_sec_{1.0};
  double command_publish_rate_hz_{20.0};
  double max_vx_{0.40};
  double max_vy_{0.25};
  double max_wz_{0.60};
  double look_yaw_kp_{1.5};
  bool nav2_linear_y_enabled_{false};
  bool require_standup_on_start_{false};
  bool enable_joystick_override_{false};
  GaitMode gait_mode_{GaitMode::kNoChange};
  ControlMode control_mode_{ControlMode::kVelocityMove};

  double real_x_{0.0};
  double real_y_{0.0};
  double real_z_{0.0};
  double real_vx_world_{0.0};
  double real_vy_world_{0.0};
  double real_vz_world_{0.0};
  double real_yaw_{0.0};
  double fake_yaw_{0.0};
  double look_yaw_target_world_{0.0};
  double balance_roll_{0.0};
  double balance_pitch_{0.0};
  double balance_yaw_{0.0};

  rclcpp::Time last_cmd_time_;
  rclcpp::Time last_control_time_;
  rclcpp::Time last_state_time_;
  rclcpp::Time start_time_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::Subscription<go2_interfaces::msg::SportModeState>::SharedPtr sport_state_sub_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr control_mode_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr look_yaw_delta_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr balance_rpy_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr legacy_nav2_odom_pub_;
  rclcpp::TimerBase::SharedPtr control_timer_;
  rclcpp::TimerBase::SharedPtr diagnostics_timer_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};

}  // namespace go2_nav2_bridge

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<go2_nav2_bridge::Go2Nav2Bridge>());
  rclcpp::shutdown();
  return 0;
}
