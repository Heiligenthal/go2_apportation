from setuptools import find_packages, setup

package_name = "go2_apportation_mocks"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="ROS2 mock servers for orchestrator development.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "mock_nav2_server = go2_apportation_mocks.mock_nav2_server:main",
            "mock_manipulation_server = go2_apportation_mocks.mock_manipulation_server:main",
        ],
    },
)
