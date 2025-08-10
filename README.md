# 3D Environment Viewer

This project provides a 3D environment viewer for basic wireframe models and includes functionality for simulating inverse kinematics (IK) motion.

## Project Structure

```
3d_env_viewer
├── src
│   ├── viewer.py          # Main entry point for the 3D viewer
│   ├── ik_simulation.py   # Implementation of IK simulation
│   └── models
│       └── wireframe.py   # Definitions for wireframe models
├── requirements.txt       # List of dependencies
└── README.md              # Project documentation
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd 3d_env_viewer
pip install -r requirements.txt
```

## Usage

To run the 3D environment viewer, execute the following command:

```bash
python src/viewer.py
```

This will open a window displaying the 3D wireframe models. You can interact with the viewer using your mouse and keyboard.

## Components

- **Viewer**: The `viewer.py` file initializes the 3D rendering context and handles user interactions.
- **IK Simulation**: The `ik_simulation.py` file contains the logic for simulating inverse kinematics, allowing for dynamic motion of models.
- **Wireframe Models**: The `wireframe.py` file defines the structures and methods for creating and manipulating wireframe geometries.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.