from setuptools import setup, find_packages
setup(
    name="LoadBalancer",
    version="0.1",
    packages=find_packages(),
    install_requires=['pyzmq>=18.1.0']
)
