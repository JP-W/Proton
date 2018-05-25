from setuptools import setup

setup(
	name="Proton IoT",
	version="1.0",
	scripts=['proton'],
	include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)
