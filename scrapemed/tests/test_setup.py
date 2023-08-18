import os
import subprocess
import shutil
import sys
import venv
import pkg_resources

def create_virtualenv(venv_dir):
    if os.path.exists(venv_dir):
        print(f"Virtual environment directory '{venv_dir}' already exists.")
        return

    venv.create(venv_dir, with_pip=True)
    print(f"Virtual environment created at '{venv_dir}'.")

def activate_virtualenv(venv_dir):
    activate_script = os.path.join(venv_dir, "Scripts" if sys.platform == "win32" else "bin", "activate")
    activate_cmd = f"source {activate_script}" if sys.platform != "win32" else f"{activate_script}"
    subprocess.run(activate_cmd, shell=True, executable="/bin/bash" if sys.platform != "win32" else None)

def deactivate_virtualenv():
    subprocess.run("deactivate", shell=True, executable="/bin/bash" if sys.platform != "win32" else None)


def delete_virtualenv(venv_dir):
    if os.path.exists(venv_dir):
        shutil.rmtree(venv_dir)
        print(f"Deleted virtual environment '{venv_dir}'.")
    else:
        print(f"Virtual environment directory '{venv_dir}' not found.")

def install_package(package_dir):
    setup_py = os.path.join(package_dir, "setup.py")
    subprocess.run(["python", setup_py, "install"])

def uninstall_package(package_name):
    try:
        pkg_resources.require(package_name)
    except pkg_resources.DistributionNotFound:
        print(f"Package '{package_name}' is not installed.")
        return

    distribution = pkg_resources.get_distribution(package_name)
    distribution.activate()
    dist_location = distribution.location

    subprocess.run(["pip", "uninstall", "-y", package_name])
    print(f"Uninstalled package '{package_name}'.")

    # Clean up any leftover files
    shutil.rmtree(dist_location, ignore_errors=True)
    print(f"Cleaned up '{dist_location}'.")

def test_setup():
    venv_dir = "test_setup_scrapemed"
    package_name = "scrapemed"  #

    # Create and activate a fresh virtual environment
    create_virtualenv(venv_dir)
    activate_virtualenv(venv_dir)

    # Run tests
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.abspath(os.path.join(current_dir, ".."))
    install_package(package_dir)
    uninstall_package(package_name)

    # Deactivate and delete the virtual environment
    deactivate_virtualenv()
    delete_virtualenv(venv_dir)

    return None