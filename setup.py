from setuptools import setup

setup(name='defSim',
      version='0.1.0',  # update this version number together with number in __init__.py
      description='The Discrete Event Framework for Social Influence Models',
      url='https://github.com/defSim/defSim',
      author='Laukemper, Keijzer, Bakker',
      author_email='m.a.keijzer@rug.nl',
      license='GNU GPLv3',
      packages=['defSim',
                'defSim/agents_init',
                'defSim/extensions',
                'defSim/network_evolution_sim',
                'defSim/focal_agent_sim',
                'defSim/influence_sim',
                'defSim/neighbor_selector_sim',
                'defSim/network_init',
                'defSim/tools',
                'defSim/dissimilarity_component'],
      install_requires=[
            'networkx>=2.4',
            'numpy>=1.17',
            'pandas',
            'scipy>=1.1.0'
      ],
      include_package_data=True,
      test_suite="pytest-runner",
      tests_require=['pytest'],
      zip_safe=False)
