#!/bin/bash

# Exit immediately if a command fails
set -e

echo "======================================"
echo " ArchLinux OS System Maintenance Script"
echo "======================================"

# Require root
if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

echo "Updating package databases and upgrading system..."
pacman -Syu --noconfirm

echo "Removing orphaned packages..."
orphans=$(pacman -Qtdq || true)
if [[ -n "$orphans" ]]; then
  pacman -Rns --noconfirm $orphans
else
  echo "No orphaned packages found."
fi

echo "Cleaning package cache..."
pacman -Sc --noconfirm

echo "System maintenance completed successfully!"
