from setuptools import find_packages, setup

package_name = "go2_person_perception"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/person_surface.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="Minimal person-perception runtime surface for frozen person topics.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "person_surface_node = go2_person_perception.person_surface_node:main",
        ],
    },
)
