from glob import glob
from setuptools import find_packages, setup

package_name = "go2_cube_perception"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="Cube perception skeleton with FAST/PRECISE stubs.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "object_detector_trt_node = go2_cube_perception.object_detector_trt_node:main",
            "object_position_fast_node = go2_cube_perception.object_position_fast_node:main",
            "object_pose_precise_node = go2_cube_perception.object_pose_precise_node:main",
        ],
    },
)
