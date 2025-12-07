# CS Automation Capstone (TU Ilmenau)

This project is a compact, runnable capstone aligned with the doctoral programme areas: Artificial Intelligence & Machine Learning, Robotics & Autonomous Systems, Computer Vision & Image Processing, Software Engineering, and Cybersecurity & Privacy.

It lives inside the `capstone/` subfolder to avoid interfering with your existing workspace.

## Structure
- **AI/ML**: `capstone/cs_capstone/ml/q_learning.py` (includes multi-agent Q-learning)
- **Robotics**: `capstone/cs_capstone/robotics/astar.py`, `capstone/cs_capstone/robotics/grid_world.py`
- **Computer Vision**: `capstone/cs_capstone/vision/color_detect.py`
- **Security**: `capstone/cs_capstone/security/crypto_utils.py`
- **Demos CLI**: `capstone/cs_capstone/app.py`
- **Tests**: `capstone/tests/`

## Setup (Windows, PowerShell)
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r capstone\requirements.txt
```

## Run Demos
Run from the `capstone/` directory:
```powershell
# A* path planning
python -m cs_capstone.app plan

# Q-learning navigation
python -m cs_capstone.app qlearn

# Multi-agent Q-learning (agentic workflow)
python -m cs_capstone.app multi_qlearn

# Computer vision color detection demo (outputs image)
python -m cs_capstone.app vision

# Security demo (encryption + hashing)
python -m cs_capstone.app crypto
```
Outputs are written to `capstone/cs_capstone/artifacts/`.

## Run Tests
```powershell
cd capstone
python -m pytest -q
```

## Notes
- Minimal deps to keep it lightweight and reproducible.
- The demos are deterministic (seeded) and fast (< a few seconds).
