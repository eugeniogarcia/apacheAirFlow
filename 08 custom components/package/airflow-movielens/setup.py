#!/usr/bin/env python

import setuptools

# modulos que se precisan para instalar nuestro modulo
requirements = ["apache-airflow", "requests"]

# modulos que se precisan solo para desarrollo
extra_requirements = {"dev": ["pytest"]}

# configuracion de nuestro modulo
setuptools.setup(
    name="airflow_movielens", # nombre, versión, descripcion, autores
    version="0.1.0",
    description="Hooks, sensors and operators for the Movielens API.",
    author="Anonymous",
    author_email="anonymous@example.com",
    install_requires=requirements, # modulos que se requieren
    extras_require=extra_requirements,
    packages=setuptools.find_packages("src"), # donde esta el fuente de nuestro modulo
    package_dir={"": "src"},
    url="https://github.com/example-repo/airflow_movielens",
    license="MIT license",
)
