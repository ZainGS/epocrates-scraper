# Epocrates Scraper

## Overview

**Epocrates Scraper** is a web scraper that extracts the latest medical news articles from [Epocrates](https://www.epocrates.com) using **Selenium**. The scraper runs in a headless **Chrome** browser inside an **Azure Container App** and retrieves article titles, descriptions, and URLs, returning the data in JSON format.

## Features

- 🚀 **Automated news extraction** from Epocrates  
- 🌍 **Headless Chrome execution** for efficient scraping  
- 🔍 **Extracts article titles, descriptions, and URLs**  
- 📦 **Returns JSON response** with up to 3 latest articles  
- 🛠 **Runs in an Azure Container App** for cloud-based execution  
- 🛑 **Error handling** with logging for debugging  

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- `pip` package manager
- Google Chrome & Chromedriver
- Docker (for local container testing)
- Azure CLI (for deployment)

### Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/zaings/epocrates-scraper.git
   cd epocrates-scraper
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run Locally**
   ```sh
   python scraper.py
   ```

## Usage

### API Endpoint

This scraper runs inside an **Azure Container App** and is triggered via an HTTP request.

Originally, I intended to deploy this application using **Azure Functions** for easy article retrieval. However, Azure Functions does **NOT** support **Selenium/Chromedriver** due to its restricted sandboxed environment, which prevents access to essential system-level tooling required for Selenium to operate. These limitations include:

- Chromedriver – A driver that allows Selenium to automate Chrome-based web interactions; the bridge between Selenium and Chrome.
- Full browser installation (e.g., Google Chrome).
- Headless mode rendering components (used to run a browser without a GUI).
- File system access (for downloads, cookies, etc.).
- Networking & process control (to manage browser instances).

The solution is to use an **Azure Container App (ACA)**, which provides a **more flexible, containerized environment with system-level access**. This allows Selenium and Chromedriver to function inside a **Docker container**, overcoming Azure Functions' limitations.

#### **Example Request**
```sh
curl -X GET https://your-container-app-url/api/ScrapeMedicalNews
```

#### **Example JSON Response**
```json
[
  {
    "title": "New Drug Approved for Hypertension",
    "description": "The FDA has approved a new treatment for high blood pressure...",
    "url": "https://www.epocrates.com/news/new-drug-hypertension"
  },
  {
    "title": "Updated Guidelines for Diabetes Treatment",
    "description": "Recent studies suggest a new approach to managing Type 2 diabetes...",
    "url": "https://www.epocrates.com/news/diabetes-guidelines"
  }
]
```

## Running with Docker Locally

1. **Build the Docker image**
   ```sh
   docker build -t epocrates-scraper .
   ```

2. **Run the container**
   ```sh
   docker run -p 8080:8080 epocrates-scraper
   ```

3. **Test the local API**
   ```sh
   curl -X GET http://localhost:8080/api/ScrapeMedicalNews
   ```

## Deploying to Azure Container Apps

1. **Login to Azure**
   ```sh
   az login
   ```

2. **Create a resource group**
   ```sh
   az group create --name epocrates-rg --location eastus
   ```

3. **Create the Azure Container App**
   ```sh
   az containerapp create --name epocrates-scraper --resource-group epocrates-rg --image yourdockerhubusername/epocrates-scraper:latest --target-port 8080 --ingress external
   ```

4. **Find your deployed API URL**
   ```sh
   az containerapp show --name epocrates-scraper --resource-group epocrates-rg --query properties.configuration.ingress.fqdn -o tsv
   ```

5. **Test the deployed API**
   ```sh
   curl -X GET https://your-container-app-url/api/ScrapeMedicalNews
   ```

## Logs & Debugging

View logs for the container:

```sh
az containerapp logs show --name epocrates-scraper --resource-group epocrates-rg
```

## Disclaimer

This project is for **educational and research purposes only**. Scraping content from Epocrates may violate its **terms of service**. Ensure you have permission before using this tool.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or contributions, feel free to open an **Issue** or submit a **Pull Request**.
