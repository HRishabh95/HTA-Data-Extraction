import yaml

# Load the environment.yml file
with open('environment.yaml') as file:
    env = yaml.safe_load(file)

# Extract dependencies
dependencies = env['dependencies']

# Write dependencies to requirements.txt
with open('requirements.txt', 'w') as file:
    for dep in dependencies:
        if isinstance(dep, str):  # Direct package specification
            file.write(dep + '\n')
        elif isinstance(dep, dict) and 'pip' in dep:  # Pip dependencies
            for pip_dep in dep['pip']:
                file.write(pip_dep + '\n')
