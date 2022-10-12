from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="McBrokenLostRevenue",
    version="1.0.0",
    description="Compute revenue loss of McDonald's in the USA due to broken "
                "ice-cream machines at the specific date",
    author="Ilya Valynets",
    author_email="ilyavolynets19@gmail.com",

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8, <4",

    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },

    entry_points={
       "console_scripts": [
          "mcbroken=mcbroken.compute_loss:compute_net_loss",
       ],
    },
)
