from setuptools import find_packages, setup

package_name = "go2_manipulation_runtime"

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
    description="Minimal runtime helpers for D1-550-backed pick/release mapping.",
    license="TODO",
    tests_require=["pytest"],
)
