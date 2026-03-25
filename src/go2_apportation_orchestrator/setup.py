from setuptools import find_packages, setup

package_name = "go2_apportation_orchestrator"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/behavior_trees", ["behavior_trees/mission_flow_stub.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="Runtime skeleton orchestrator for the Go2 apportation project.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "orchestrator_stub = go2_apportation_orchestrator.orchestrator_node:main",
            "orchestrator_runtime = go2_apportation_orchestrator.orchestrator_runtime_node:main",
        ],
    },
)
