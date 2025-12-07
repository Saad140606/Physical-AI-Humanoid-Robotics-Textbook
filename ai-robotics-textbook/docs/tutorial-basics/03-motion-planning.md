---
sidebar_position: 4
---

# Motion Planning and Control

## Path Planning Overview

Path planning is the process of determining a sequence of configurations to move a robot from start to goal while avoiding obstacles.

## Configuration Space

- **C-space (Configuration Space)**: Space of all possible robot configurations
- **C-free**: Configuration space without collisions
- **C-obstacle**: Configurations causing collisions

## Classic Path Planning Algorithms

### Rapidly-exploring Random Trees (RRT)

RRT is a probabilistically complete algorithm that explores configuration space:

```python
def rrt_planning(start, goal, obstacles, max_iterations):
    tree = [start]
    
    for i in range(max_iterations):
        # Sample random configuration
        q_rand = random_config()
        
        # Find nearest node in tree
        q_nearest = nearest_node(tree, q_rand)
        
        # Extend tree toward random config
        q_new = extend(q_nearest, q_rand)
        
        # Check collision
        if not collision_free(q_nearest, q_new, obstacles):
            continue
            
        tree.append(q_new)
        
        # Check if goal reached
        if distance(q_new, goal) < threshold:
            return reconstruct_path(tree)
    
    return None  # No path found
```

### Probabilistic Roadmap (PRM)

Creates a graph of collision-free configurations:
1. Sample random configurations
2. Connect nearby configurations if collision-free
3. Use graph search to find path

## Optimization-Based Planning

### TRAC-IK (Trajectory Rajectory and Arm Kinematics Inverse Kinematics)
Solves inverse kinematics with constraints:
- Joint limits
- Singularity avoidance
- Collision constraints

## Trajectory Generation

### Minimum-Time Trajectory

Generates smooth trajectories respecting:
- Joint velocity limits
- Joint acceleration limits
- Jerk constraints (derivative of acceleration)

### Bezier Curves

Smooth interpolation between waypoints:

```python
def bezier_curve(p0, p1, p2, p3, t):
    # Cubic Bezier interpolation
    mt = 1 - t
    return (mt**3 * p0 + 3*mt**2*t * p1 + 
            3*mt*t**2 * p2 + t**3 * p3)
```

## Control Systems

### PID Control

Fundamental feedback control law:

```
u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt
```

Where:
- **e(t)**: Error (desired - actual)
- **Kp**: Proportional gain
- **Ki**: Integral gain
- **Kd**: Derivative gain

### Model Predictive Control (MPC)

Predicts future states and optimizes over a horizon:
- Handles constraints naturally
- Provides optimal control sequences
- Computationally intensive

## Joint Space vs Task Space Control

### Joint Space Control
- Control individual joint angles
- Simple and direct
- Singularities in task space

### Task Space Control (Cartesian Control)
- Control end-effector position/orientation
- More intuitive for applications
- Requires inverse kinematics
- Better constraint handling

## Impedance Control

Makes robot compliant to external forces:
- Virtual stiffness and damping
- Safe human-robot interaction
- Force feedback control

## ROS Control

Robot Operating System provides control infrastructure:

```xml
<!-- URDF robot model definition -->
<robot name="robot">
  <link name="base"/>
  <joint name="joint1" type="revolute">
    <parent link="base"/>
    <child link="link1"/>
  </joint>
</robot>
```

## Real-Time Execution

Motion control requires hard real-time guarantees:
- Deterministic computation times
- PREEMPT-RT kernel on Linux
- Real-time operating systems
- Cycle times: 1-10 ms typical

## Collision Avoidance

### Dynamic Obstacle Avoidance
- Predict obstacle motion
- Modify trajectory in real-time
- Vector Field Histogram (VFH) algorithm
- Social force models for human prediction

### Safety Monitoring
- Speed limiting zones
- Safe stopping functions
- Emergency stops
- Dual-channel monitoring
