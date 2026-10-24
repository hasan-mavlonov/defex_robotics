from pathlib import Path

import mujoco
import mujoco.viewer

# Find the XML file relative to this Python script
BASE_DIR = Path(__file__).resolve().parent
XML_PATH = BASE_DIR / "connector.xml"

model = mujoco.MjModel.from_xml_path(str(XML_PATH))
data = mujoco.MjData(model)

print("Defex Robotics | MuJoCo simulation started")
print("Close the viewer window to exit.")

mujoco.viewer.launch(model, data)