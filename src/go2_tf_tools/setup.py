from setuptools import find_packages, setup

package_name = "go2_tf_tools"

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
    description="TF adapter utilities for Go2 runtime bringup.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "odom_to_tf_broadcaster = go2_tf_tools.odom_to_tf_broadcaster:main",
        ],
    },
)
