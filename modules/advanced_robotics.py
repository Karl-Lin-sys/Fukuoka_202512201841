"""
Advanced Robotics and Cognitive Computing Module
Demonstrates robotic simulations, path planning, and cognitive architectures
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
import heapq
from collections import deque
import random
import math


class RobotType(Enum):
    """Different types of robots with varying capabilities"""
    DIFFERENTIAL_DRIVE = "differential_drive"
    OMNIDIRECTIONAL = "omnidirectional"
    ARTICULATED_ARM = "articulated_arm"
    HUMANOID = "humanoid"


@dataclass
class RobotState:
    """Represents the state of a robot"""
    x: float
    y: float
    theta: float  # Orientation angle
    velocity: float
    angular_velocity: float
    timestamp: float


@dataclass
class EnvironmentObject:
    """Represents an object in the environment"""
    x: float
    y: float
    width: float
    height: float
    object_type: str  # 'obstacle', 'target', 'hazard'


class CognitiveArchitecture:
    """Simple cognitive architecture for decision making"""
    
    def __init__(self):
        self.perception_layer = PerceptionLayer()
        self.decision_layer = DecisionLayer()
        self.action_layer = ActionLayer()
        self.memory = MemorySystem()
        
    def process_sensory_input(self, robot_state: RobotState, environment: 'Environment') -> Dict:
        """Process sensory input and generate actions"""
        # Perception
        perceived_data = self.perception_layer.perceive(robot_state, environment)
        
        # Store in memory
        self.memory.store(perceived_data)
        
        # Decision making
        decision = self.decision_layer.decide(perceived_data, self.memory)
        
        # Action execution
        action = self.action_layer.execute(decision, robot_state)
        
        return {
            "perception": perceived_data,
            "decision": decision,
            "action": action
        }


class PerceptionLayer:
    """Perception layer for processing sensory data"""
    
    def perceive(self, robot_state: RobotState, environment: 'Environment') -> Dict:
        """Perceive the environment"""
        # Simulate sensor readings
        obstacles = self._detect_obstacles(robot_state, environment)
        targets = self._detect_targets(robot_state, environment)
        hazards = self._detect_hazards(robot_state, environment)
        
        return {
            "robot_position": (robot_state.x, robot_state.y),
            "robot_orientation": robot_state.theta,
            "detected_obstacles": obstacles,
            "detected_targets": targets,
            "detected_hazards": hazards,
            "timestamp": robot_state.timestamp
        }
    
    def _detect_obstacles(self, robot_state: RobotState, environment: 'Environment') -> List[Dict]:
        """Detect obstacles within sensor range"""
        detected = []
        sensor_range = 5.0  # meters
        
        for obj in environment.objects:
            if obj.object_type == "obstacle":
                distance = math.sqrt((obj.x - robot_state.x)**2 + (obj.y - robot_state.y)**2)
                if distance <= sensor_range:
                    detected.append({
                        "position": (obj.x, obj.y),
                        "distance": distance,
                        "size": (obj.width, obj.height)
                    })
        
        return detected
    
    def _detect_targets(self, robot_state: RobotState, environment: 'Environment') -> List[Dict]:
        """Detect targets within sensor range"""
        detected = []
        sensor_range = 10.0  # meters
        
        for obj in environment.objects:
            if obj.object_type == "target":
                distance = math.sqrt((obj.x - robot_state.x)**2 + (obj.y - robot_state.y)**2)
                if distance <= sensor_range:
                    detected.append({
                        "position": (obj.x, obj.y),
                        "distance": distance
                    })
        
        return detected
    
    def _detect_hazards(self, robot_state: RobotState, environment: 'Environment') -> List[Dict]:
        """Detect hazards within sensor range"""
        detected = []
        sensor_range = 3.0  # meters
        
        for obj in environment.objects:
            if obj.object_type == "hazard":
                distance = math.sqrt((obj.x - robot_state.x)**2 + (obj.y - robot_state.y)**2)
                if distance <= sensor_range:
                    detected.append({
                        "position": (obj.x, obj.y),
                        "distance": distance,
                        "severity": "high" if distance < 1.5 else "medium"
                    })
        
        return detected


class DecisionLayer:
    """Decision layer for cognitive processing"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[Dict]:
        """Initialize decision rules"""
        return [
            {"condition": "hazard_near", "action": "avoid", "priority": 1},
            {"condition": "obstacle_ahead", "action": "navigate_around", "priority": 2},
            {"condition": "target_detected", "action": "approach", "priority": 3},
            {"condition": "path_clear", "action": "explore", "priority": 4}
        ]
    
    def decide(self, perception: Dict, memory: 'MemorySystem') -> Dict:
        """Make decision based on perception and memory"""
        # Evaluate conditions
        active_conditions = []
        
        if perception["detected_hazards"]:
            active_conditions.append("hazard_near")
        
        if perception["detected_obstacles"]:
            active_conditions.append("obstacle_ahead")
        
        if perception["detected_targets"]:
            active_conditions.append("target_detected")
        
        if not active_conditions:
            active_conditions.append("path_clear")
        
        # Find highest priority rule
        applicable_rules = [rule for rule in self.rules if rule["condition"] in active_conditions]
        if applicable_rules:
            decision = min(applicable_rules, key=lambda x: x["priority"])
        else:
            decision = {"condition": "default", "action": "wait", "priority": 5}
        
        return {
            "decision": decision["action"],
            "condition": decision["condition"],
            "confidence": 0.8,
            "reasoning": f"Rule triggered: {decision['condition']}"
        }


class ActionLayer:
    """Action layer for executing decisions"""
    
    def execute(self, decision: Dict, robot_state: RobotState) -> Dict:
        """Execute action based on decision"""
        action = decision["decision"]
        
        if action == "avoid":
            # Emergency avoidance maneuver
            new_velocity = 0.0
            new_angular_velocity = random.choice([-1.0, 1.0])  # Turn quickly
        elif action == "navigate_around":
            # Navigate around obstacle
            new_velocity = 0.5
            new_angular_velocity = 0.5
        elif action == "approach":
            # Move toward target
            new_velocity = 1.0
            new_angular_velocity = 0.0
        elif action == "explore":
            # Random exploration
            new_velocity = 0.8
            new_angular_velocity = random.uniform(-0.5, 0.5)
        else:  # wait
            new_velocity = 0.0
            new_angular_velocity = 0.0
        
        return {
            "action_type": action,
            "linear_velocity": new_velocity,
            "angular_velocity": new_angular_velocity,
            "duration": 0.1  # seconds
        }


class MemorySystem:
    """Simple memory system for storing and retrieving information"""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.short_term_memory = deque(maxlen=100)
        self.long_term_memory = []
        self.spatial_map = {}
    
    def store(self, data: Dict):
        """Store data in memory"""
        self.short_term_memory.append(data)
        
        # Important data goes to long-term memory
        if data.get("detected_hazards") or data.get("detected_targets"):
            self.long_term_memory.append(data)
        
        # Update spatial map
        position = data.get("robot_position")
        if position:
            self.spatial_map[data["timestamp"]] = position
    
    def recall_recent(self, n: int = 10) -> List[Dict]:
        """Recall recent memories"""
        return list(self.short_term_memory)[-n:]
    
    def get_trajectory(self) -> List[Tuple[float, float]]:
        """Get robot trajectory from spatial map"""
        return [pos for pos in self.spatial_map.values()]


class Environment:
    """Robot environment simulation"""
    
    def __init__(self, width: float = 20.0, height: float = 20.0):
        self.width = width
        self.height = height
        self.objects: List[EnvironmentObject] = []
        self.time = 0.0
    
    def add_object(self, obj: EnvironmentObject):
        """Add an object to the environment"""
        self.objects.append(obj)
    
    def generate_random_environment(self, n_obstacles: int = 10, n_targets: int = 3, n_hazards: int = 2):
        """Generate random environment with objects"""
        self.objects.clear()
        
        # Add obstacles
        for _ in range(n_obstacles):
            obj = EnvironmentObject(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                width=random.uniform(0.5, 2.0),
                height=random.uniform(0.5, 2.0),
                object_type="obstacle"
            )
            self.add_object(obj)
        
        # Add targets
        for _ in range(n_targets):
            obj = EnvironmentObject(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                width=0.5,
                height=0.5,
                object_type="target"
            )
            self.add_object(obj)
        
        # Add hazards
        for _ in range(n_hazards):
            obj = EnvironmentObject(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                width=1.0,
                height=1.0,
                object_type="hazard"
            )
            self.add_object(obj)
    
    def check_collision(self, x: float, y: float, radius: float = 0.3) -> bool:
        """Check if position collides with obstacles"""
        for obj in self.objects:
            if obj.object_type == "obstacle":
                # Simple rectangular collision
                if (obj.x - obj.width/2 <= x <= obj.x + obj.width/2 and
                    obj.y - obj.height/2 <= y <= obj.y + obj.height/2):
                    return True
        return False
    
    def update(self, dt: float):
        """Update environment state"""
        self.time += dt


class AdvancedRobot:
    """Advanced robot with cognitive capabilities"""
    
    def __init__(self, robot_type: RobotType, initial_x: float = 0.0, initial_y: float = 0.0):
        self.robot_type = robot_type
        self.state = RobotState(
            x=initial_x,
            y=initial_y,
            theta=0.0,
            velocity=0.0,
            angular_velocity=0.0,
            timestamp=0.0
        )
        self.cognitive_arch = CognitiveArchitecture()
        self.trajectory = [(initial_x, initial_y)]
        self.max_velocity = 2.0  # m/s
        self.max_angular_velocity = 1.0  # rad/s
    
    def update(self, environment: Environment, dt: float):
        """Update robot state using cognitive architecture"""
        # Process sensory input and generate action
        result = self.cognitive_arch.process_sensory_input(self.state, environment)
        
        # Apply action to robot state
        action = result["action"]
        self.state.velocity = np.clip(action["linear_velocity"], -self.max_velocity, self.max_velocity)
        self.state.angular_velocity = np.clip(action["angular_velocity"], -self.max_angular_velocity, self.max_angular_velocity)
        
        # Update position (simple kinematics)
        self.state.x += self.state.velocity * math.cos(self.state.theta) * dt
        self.state.y += self.state.velocity * math.sin(self.state.theta) * dt
        self.state.theta += self.state.angular_velocity * dt
        
        # Keep theta in [-pi, pi]
        self.state.theta = math.atan2(math.sin(self.state.theta), math.cos(self.state.theta))
        
        # Check boundaries
        self.state.x = np.clip(self.state.x, 0, environment.width)
        self.state.y = np.clip(self.state.y, 0, environment.height)
        
        # Update timestamp
        self.state.timestamp += dt
        
        # Store trajectory
        self.trajectory.append((self.state.x, self.state.y))
        
        return result


class SwarmRobotics:
    """Swarm robotics simulation"""
    
    def __init__(self, n_robots: int = 5, environment: Environment = None):
        self.n_robots = n_robots
        self.robots = []
        self.environment = environment or Environment()
        
        # Initialize robots with random positions
        for i in range(n_robots):
            robot = AdvancedRobot(
                RobotType.DIFFERENTIAL_DRIVE,
                random.uniform(1, self.environment.width - 1),
                random.uniform(1, self.environment.height - 1)
            )
            self.robots.append(robot)
    
    def simulate_step(self, dt: float = 0.1):
        """Simulate one time step"""
        results = []
        
        for robot in self.robots:
            result = robot.update(self.environment, dt)
            results.append(result)
        
        self.environment.update(dt)
        return results
    
    def get_swarm_metrics(self) -> Dict:
        """Calculate swarm performance metrics"""
        positions = [(robot.state.x, robot.state.y) for robot in self.robots]
        
        # Calculate centroid
        centroid_x = np.mean([pos[0] for pos in positions])
        centroid_y = np.mean([pos[1] for pos in positions])
        
        # Calculate dispersion (average distance from centroid)
        dispersion = np.mean([
            math.sqrt((pos[0] - centroid_x)**2 + (pos[1] - centroid_y)**2)
            for pos in positions
        ])
        
        # Calculate cohesion (inverse of dispersion)
        cohesion = 1.0 / (1.0 + dispersion)
        
        return {
            "swarm_size": self.n_robots,
            "centroid": (centroid_x, centroid_y),
            "dispersion": dispersion,
            "cohesion": cohesion,
            "coverage": self._calculate_coverage()
        }
    
    def _calculate_coverage(self) -> float:
        """Calculate area coverage by swarm"""
        positions = [(robot.state.x, robot.state.y) for robot in self.robots]
        
        if len(positions) < 3:
            return 0.0
        
        # Simple convex hull area calculation
        hull = self._convex_hull(positions)
        area = self._polygon_area(hull)
        
        return area / (self.environment.width * self.environment.height)
    
    def _convex_hull(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Calculate convex hull of points"""
        if len(points) < 3:
            return points
        
        # Sort points by x-coordinate
        points = sorted(points)
        
        # Build lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and self._cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # Build upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and self._cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        return lower[:-1] + upper[:-1]
    
    def _cross_product(self, o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Calculate cross product of OA and OB vectors"""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    def _polygon_area(self, vertices: List[Tuple[float, float]]) -> float:
        """Calculate area of polygon using shoelace formula"""
        if len(vertices) < 3:
            return 0.0
        
        area = 0.0
        n = len(vertices)
        
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        
        return abs(area) / 2.0


def create_robotics_demo() -> Dict:
    """Create a comprehensive robotics demonstration"""
    # Create environment
    env = Environment(width=20.0, height=20.0)
    env.generate_random_environment(n_obstacles=8, n_targets=3, n_hazards=2)
    
    # Create advanced robot
    robot = AdvancedRobot(RobotType.DIFFERENTIAL_DRIVE, initial_x=1.0, initial_y=1.0)
    
    # Create swarm
    swarm = SwarmRobotics(n_robots=5, environment=env)
    
    # Simulate for some time
    simulation_results = []
    for step in range(100):
        results = swarm.simulate_step(dt=0.1)
        metrics = swarm.get_swarm_metrics()
        simulation_results.append({
            "step": step,
            "time": step * 0.1,
            "robot_states": [
                {
                    "x": robot.state.x,
                    "y": robot.state.y,
                    "theta": robot.state.theta,
                    "velocity": robot.state.velocity
                } for robot in swarm.robots
            ],
            "swarm_metrics": metrics
        })
    
    return {
        "environment": {
            "width": env.width,
            "height": env.height,
            "objects": [
                {
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                    "type": obj.object_type
                } for obj in env.objects
            ]
        },
        "simulation_results": simulation_results,
        "final_metrics": swarm.get_swarm_metrics(),
        "robot_trajectories": [
            robot.trajectory for robot in swarm.robots
        ]
    }
