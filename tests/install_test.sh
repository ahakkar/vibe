#!/bin/bash

# Define color codes
RED="\e[31m"
GREEN="\e[32m"
RESET="\e[0m"

REQ_FILE_TEST="tests/requirements.txt"
MISSING_PACKAGES=()

# Check if requirements file exists
if [[ -f "$REQ_FILE_TEST" ]]; then
    echo -e "${CYAN}Checking required Python packages from $REQ_FILE_TEST...${RESET}"

    while IFS= read -r package || [[ -n "$package" ]]; do
        if [[ -n "$package" && ! "$package" =~ ^# ]]; then
            PACKAGE_NAME=$(echo $package | cut -d'=' -f1)  
            if ! pip show "$PACKAGE_NAME" &> /dev/null; then
                MISSING_PACKAGES+=("$package")
            fi
        fi
    done < "$REQ_FILE_TEST"

    if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Some packages are missing. Installing required packages...${RESET}"
        pip install -r "$REQ_FILE_TEST"
    else
        echo -e "${GREEN}All required packages are already installed. Skipping installation.${RESET}"
        echo ""
    fi
else
    echo -e "${RED}Error: Requirements file '$REQ_FILE_TEST' not found!${RESET}"
    echo ""
    exit 1
fi

package_name="portaudio19-dev"
if [ "$(dpkg-query -s "$package_name" 2>/dev/null)" ]; then
    echo -e "${GREEN}The package $package_name is installed.${RESET}"
else
    echo -e "${RED}The package $package_name is not installed. Installing now...${RESET}"
    if command -v apt &> /dev/null; then
        sudo apt install -y portaudio19-dev
    elif command -v yum &> /dev/null; then
        sudo yum install -y portaudio19-dev
    elif command -v pacman &> /dev/null; then
        sudo pacman -S portaudio19-dev --noconfirm
    else
        echo -e "${RED}Unsupported package manager. Please install $package_name manually.${RESET}"
        exit 1
    fi

    echo -e "${GREEN}$package_name installation completed.${RESET}"
fi