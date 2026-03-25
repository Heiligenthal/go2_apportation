from glob import glob
from setuptools import find_packages, setup

package_name = "go2_object_tracking"

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
    description="Object tracking skeleton without motion output.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "object_tracker_node = go2_object_tracking.object_tracker_node:main",
        ],
    },
)
