from setuptools import setup

setup(name='defSim',
      version='0.1.2',  # update this version number together with number in __init__.py
      description='The Discrete Event Framework for Social Influence Models',
      url='https://github.com/defSim/defSim',
      author='Laukemper, Keijzer, Bakker',
      author_email='marijn.keijzer@iast.fr',
      license='GNU GPLv3',
      packages=['defSim',
                'defSim/agents_init',
                'defSim/extensions',
                'defSim/extensions/influence_sim',
                'defSim/extensions/tools',
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
            'scipy>=1.1.0',
            'tqdm>=4.58.0',
            'matplotlib>=3.1.3',  # previously 3.3.4 required, crashes upon calling plot functions with error:
                                  # cannot import name '_png' from 'matplotlib'    (matplotlib error, not ours)
            'seaborn>=0.11.1'
      ],
      include_package_data=True,
      test_suite="pytest-runner",
      tests_require=['pytest'],
      zip_safe=False)
