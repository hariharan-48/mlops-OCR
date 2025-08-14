# MLOps OCR + RAG Workshop - Prerequisites

This guide will help you set up your development environment before the workshop. Please complete all required installations before attending.

## 🎯 **What You'll Need**

### **Required Tools (Must Have)**
- Google Cloud SDK
- Docker Desktop
- Python 3.8+
- Git
- Terminal/Command Prompt

### **Good to Have**
- VS Code or similar code editor
- Postman or similar API testing tool
- Basic knowledge of command line

---

## 🖥️ **Operating System Setup**

### **macOS Setup**

#### **1. Install Homebrew (Package Manager)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (if needed)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

#### **2. Install Required Tools**
```bash
# Install Python 3.11
brew install python@3.11

# Install Git
brew install git

# Install Docker Desktop
brew install --cask docker

# Install Google Cloud SDK
brew install --cask google-cloud-sdk
```

#### **3. Verify Installations**
```bash
# Check Python version
python3 --version  # Should be 3.8 or higher

# Check Git version
git --version

# Check Docker version
docker --version

# Check Google Cloud SDK
gcloud --version
```

### **Windows Setup**

#### **Option 1: Manual Installation (Recommended)**

##### **1. Install Python 3.11**
1. **Download Python**: Go to [python.org/downloads](https://www.python.org/downloads/)
2. **Download Python 3.11.x** (latest 3.11 version)
3. **Run installer**: Check "Add Python to PATH" and "Install for all users"
4. **Verify installation**:
   ```cmd
   python --version
   pip --version
   ```

##### **2. Install Git**
1. **Download Git**: Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. **Download Windows version** (64-bit)
3. **Run installer**: Use default settings
4. **Verify installation**:
   ```cmd
   git --version
   ```

##### **3. Install Docker Desktop**
1. **Download Docker Desktop**: Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Download Windows version**
3. **Run installer**: Follow installation wizard
4. **Restart computer** when prompted
5. **Start Docker Desktop** from Start Menu
6. **Verify installation**:
   ```cmd
   docker --version
   docker run hello-world
   ```

##### **4. Install Google Cloud SDK**
1. **Download SDK**: Go to [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
2. **Download Windows installer** (Google Cloud CLI)
3. **Run installer**: Follow installation wizard
4. **Open new Command Prompt** and verify:
   ```cmd
   gcloud --version
   ```

#### **Option 2: Using Chocolatey (Alternative)**

If Chocolatey works on your system:

##### **1. Install Chocolatey**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

##### **2. Install Required Tools**
```powershell
# Install Python 3.11
choco install python311

# Install Git
choco install git

# Install Docker Desktop
choco install docker-desktop

# Install Google Cloud SDK
choco install gcloudsdk
```

#### **3. Verify All Installations**
```cmd
# Check Python version
python --version  # Should be 3.8 or higher

# Check Git version
git --version

# Check Docker version
docker --version

# Check Google Cloud SDK
gcloud --version
```

### **Linux Setup (Ubuntu/Debian)**

#### **1. Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

#### **2. Install Required Tools**
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Install Git
sudo apt install git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Google Cloud SDK
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update && sudo apt install google-cloud-sdk
```

#### **3. Verify Installations**
```bash
# Check Python version
python3 --version  # Should be 3.8 or higher

# Check Git version
git --version

# Check Docker version
docker --version

# Check Google Cloud SDK
gcloud --version
```

---

## 🔧 **Tool-Specific Setup**

### **1. Google Cloud SDK Setup**

#### **Initialize Google Cloud SDK**
```bash
# Initialize gcloud
gcloud init

# Set default project (you'll get this from the organizer)
gcloud config set project YOUR_PROJECT_ID

# Set default region
gcloud config set compute/region us-central1
```

#### **Install Additional Components**
```bash
# Install Docker credential helper
gcloud components install docker-credential-gcr

# Install additional components
gcloud components install kubectl
gcloud components install cloud-build-local
```

### **2. Docker Desktop Setup**

#### **Start Docker Desktop**
- **macOS**: Open Docker Desktop from Applications
- **Windows**: Start Docker Desktop from Start Menu
- **Linux**: Run `sudo systemctl start docker`

#### **Verify Docker is Running**
```bash
# Test Docker
docker run hello-world

# Check Docker version
docker --version
```


### **4. Git Setup**

#### **Configure Git**
```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main
```

---

## 📁 **Workshop Preparation**

### **1. Create Workshop Directory**
```bash
# Create directory for workshop
mkdir ~/mlops-ocr-workshop
cd ~/mlops-ocr-workshop
```

### **2. Get Repository Access**
```bash
# Clone the workshop repository (you'll get the URL from the organizer)
git clone <WORKSHOP_REPOSITORY_URL>
cd Mlops-Trainig-OCR

# Verify you have the workshop files
ls -la
# You should see: PARTICIPANT_GUIDE.md, PREREQUISITES.md, app/, rag-service/, etc.
```

### **3. Download Workshop Materials**
- Download your service account key file (`.keys/ocr-sa-<yourname>.json`) from the organizer
- Place it in the `.keys/` directory (create if it doesn't exist)
- Verify sample images are in the `sample/` directory

```