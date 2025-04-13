from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "mazy_ai_logo.icns",
    "plist": {
        "CFBundleName": "MAZY AI",
        "CFBundleDisplayName": "MAZY AI",
        "CFBundleVersion": "1.0.0",
        "CFBundleIdentifier": "app.vercel.dineshpandikona.brainymaze",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
