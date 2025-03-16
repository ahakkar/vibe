#!/bin/bash

# Build and run Docker Compose if everything is installed properly
echo -e "${CYAN}Running Docker Compose Build...${RESET}"
sudo docker compose build

echo -e "${CYAN}Running Docker Compose App...${RESET}"
sudo docker compose run --rm --service-ports app