#!/bin/bash

# Define color codes
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"


install_docker() {
    echo ""
    echo -e "${YELLOW}Installing Docker...${RESET}"
    
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

if ! command -v docker &> /dev/null; then
    echo ""
    echo -e "${RED}Docker is NOT installed. Installing now...${RESET}"
    install_docker
else
    echo ""
    echo -e "${GREEN}Docker is already installed.${RESET}"

    if ! sudo systemctl is-active --quiet docker; then
        echo -e "${YELLOW}Docker is installed but not running. Starting Docker...${RESET}"
        sudo systemctl start docker
    fi

    echo -e "${CYAN}Docker is running.${RESET}"
    docker ps -a
fi

# Function to install pip if not installed
install_pip() {
    echo -e "${RED}pip is NOT installed. Installing now...${RESET}"
    
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
}

if ! command -v pip &> /dev/null; then
    install_pip
else
    echo -e "${GREEN}pip is already installed.${RESET}"
    echo ""
fi

echo -e "${CYAN}Running Docker Compose Build...${RESET}"
sudo docker compose build
