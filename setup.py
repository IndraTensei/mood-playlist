from setuptools import setup, find_packages

setup(
    name="mood-playlist",
    version="1.0.0",
    description="🎵 Generate curated Spotify playlists based on your mood",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="IndraTensei",
    url="https://github.com/IndraTensei/mood-playlist",
    py_modules=["mood-playlist"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "mood-playlist=mood-playlist:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
