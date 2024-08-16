from naoqi import ALProxy
import math

# 连接到Pepper机器人
motion = ALProxy("ALMotion", "PEPPER_IP", 9559)
sonar = ALProxy("ALSonar", "PEPPER_IP", 9559)

# 启用传感器
sonar.subscribe("SonarApp")

# 设置目标位置
goal_position = [2.0, 2.0]  # 目标点的坐标
zeta = 1.0  # 吸引力系数
eta = 0.5   # 排斥力系数
d0 = 1.0    # 排斥力作用的最大距离

def compute_attraction_force(current_position, goal_position):
    # 计算吸引力
    force_x = -zeta * (current_position[0] - goal_position[0])
    force_y = -zeta * (current_position[1] - goal_position[1])
    return [force_x, force_y]

def compute_repulsion_force(current_position, obstacle_position):
    # 计算排斥力
    dist_to_obstacle = math.sqrt((current_position[0] - obstacle_position[0])**2 + 
                                 (current_position[1] - obstacle_position[1])**2)
    if dist_to_obstacle <= d0:
        force_x = eta * (1/dist_to_obstacle - 1/d0) * (1/dist_to_obstacle**2) * \
                  (current_position[0] - obstacle_position[0]) / dist_to_obstacle
        force_y = eta * (1/dist_to_obstacle - 1/d0) * (1/dist_to_obstacle**2) * \
                  (current_position[1] - obstacle_position[1]) / dist_to_obstacle
        return [force_x, force_y]
    else:
        return [0, 0]

def detect_obstacle():
    # 获取传感器数据，返回障碍物的位置
    left_sensor = sonar.getSonarLeft()
    right_sensor = sonar.getSonarRight()
    
    if left_sensor < 1.0:
        return [0.5, left_sensor]  # 假设障碍物在左前方
    elif right_sensor < 1.0:
        return [0.5, right_sensor]  # 假设障碍物在右前方
    else:
        return None  # 没有检测到障碍物

def move_towards_goal():
    current_position = [0.0, 0.0]  # 初始位置

    while True:
        # 计算吸引力
        attraction = compute_attraction_force(current_position, goal_position)
        
        # 检测障碍物并计算排斥力
        obstacle_position = detect_obstacle()
        if obstacle_position:
            repulsion = compute_repulsion_force(current_position, obstacle_position)
        else:
            repulsion = [0, 0]
        
        # 计算合力
        total_force_x = attraction[0] + repulsion[0]
        total_force_y = attraction[1] + repulsion[1]
        
        # 更新机器人位置
        current_position[0] += total_force_x * 0.1  # 调整步长
        current_position[1] += total_force_y * 0.1
        
        # 控制Pepper机器人移动
        motion.moveTo(total_force_x * 0.1, total_force_y * 0.1, 0.0)
        
        # 检查是否到达目标点
        if math.sqrt((current_position[0] - goal_position[0])**2 + 
                     (current_position[1] - goal_position[1])**2) < 0.1:
            print("到达目标点")
            break

# 启动导航
move_towards_goal()

# 取消传感器订阅
sonar.unsubscribe("SonarApp")
