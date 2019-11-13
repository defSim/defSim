from setuptools import setup

setup(name='defSim',
      version='0.1',
      description='The Discrete Event Framework for Social Influence Models',
      url='https://github.com/marijnkeijzer/defSim',
      author='Laukemper & Keijzer',
      author_email='m.a.keijzer@rug.nl',
      license='MIT',
      packages=['defSim',
                'defSim/agents_init',
                'defSim/network_evolution_sim',
                'defSim/focal_agent_sim',
                'defSim/influence_sim',
                'defSim/neighbor_selector_sim',
                'defSim/network_init',
                'defSim/tools',
                'defSim/dissimilarity_component'],
      install_requires=[
            'networkx' >= 2.4,
            'numpy', 'pandas'
      ],
      include_package_data=True,
      test_suite="pytest-runner",
      tests_require=['pytest'],
      zip_safe=False)
