# README for Image Processing API

## Overview
This project provides a Flask-based web service for processing images. It includes endpoints for processing images, checking the service's status, and displaying usage instructions. The service computes a normalized histogram vector and a perceptual hash (pHash) for each image. It also keeps track of various metrics like processing time and the last successful or failed request.

## Docker
You can easily run this service using Docker. The image is available on Docker Hub. Pull the image using the following command:

```bash
docker pull origiladi/de-dup_images:v0.1