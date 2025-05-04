#!/bin/bash

# Define color codes
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"

REQ_FILE_TEST="test/requirements.txt"
MISSING_PACKAGES=()
PACKAGE_NAME="portaudio19-dev"

install_docker() {
    echo -e "\n${YELLOW}Installing Docker...${RESET}"
    
    sudo apt update -y || sudo yum update -y
    
    if command -v apt &> /dev/null; then
        sudo apt install -y docker.io
    elif command -v yum &> /dev/null; then
        sudo yum install -y docker
    else
        echo -e "${RED}Unsupported package manager. Please install Docker manually.${RESET}"
        exit 1
    fi

    sudo systemctl enable docker
    sudo systemctl start docker

    echo -e "${GREEN}Docker installation completed successfully!${RESET}"
}

install_pip() {
    if ! command -v pip &> /dev/null; then
        echo -e "\n${YELLOW}Installing pip...${RESET}"
        
        if command -v apt &> /dev/null; then
            sudo apt update -y && sudo apt install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy python-pip --noconfirm
        else
            echo -e "${RED}Unsupported package manager. Please install pip manually.${RESET}"
            exit 1
        fi

        echo -e "${GREEN}pip installation completed.${RESET}"
    fi
}

install_requirements() {
    if [[ -f "$REQ_FILE_TEST" ]]; then
        while IFS= read -r package || [[ -n "$package" ]]; do
            if [[ -n "$package" && ! "$package" =~ ^# ]]; then
                PACKAGE_NAME=$(echo $package | cut -d'=' -f1)
                if ! pip show "$PACKAGE_NAME" &> /dev/null; then
                    MISSING_PACKAGES+=("$package")
                fi
            fi
        done < "$REQ_FILE_TEST"

        if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
            echo -e "${YELLOW}Installing missing Python packages...${RESET}"
            pip install -r "$REQ_FILE_TEST"
        fi
    else
        echo -e "${RED}Error: Requirements file '$REQ_FILE_TEST' not found!${RESET}"
        exit 1
    fi
}

install_portaudio() {
    if ! dpkg-query -s "$PACKAGE_NAME" &> /dev/null; then
        echo -e "${YELLOW}Installing $PACKAGE_NAME...${RESET}"
        
        if command -v apt &> /dev/null; then
            sudo apt install -y "$PACKAGE_NAME"
        elif command -v yum &> /dev/null; then
            sudo yum install -y "$PACKAGE_NAME"
        elif command -v pacman &> /dev/null; then
            sudo pacman -S "$PACKAGE_NAME" --noconfirm
        else
            echo -e "${RED}Unsupported package manager. Please install $PACKAGE_NAME manually.${RESET}"
            exit 1
        fi

        echo -e "${GREEN}$PACKAGE_NAME installation completed.${RESET}"
    fi
}

run_application() {
    echo -e "${CYAN}Building and running the application using Docker Compose...${RESET}"
    docker compose build && docker compose run --rm --service-ports app
}

while true; do
    echo -e "\n${CYAN}Select an option:${RESET}"
    echo -e "1) Install Docker"
    echo -e "2) Install Requirements for testing"
    echo -e "3) Download models"
    echo -e "4) Run application"
    echo -e "5) Exit"

    read -p "Enter your choice (1-5): " choice

    case $choice in
        1)
            if ! command -v docker &> /dev/null; then
                echo -e "\n${RED}Docker is NOT installed. Installing now...${RESET}"
                install_docker
            else
                echo -e "${GREEN}Docker is already installed.${RESET}"
            fi
            ;;
        2) install_pip && install_requirements && install_portaudio ;;
        3) python download_models.py ;;
        4) run_application ;;
        5) 
            echo -e "${GREEN}Exiting...${RESET}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice! Please enter a valid number (1-4).${RESET}"
            sleep 1
            ;;
    esac
done
