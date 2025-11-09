# 🚀 Enterprise Selenium Automation Framework

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-Latest-orange.svg)](https://pytest.org/)
[![Allure](https://img.shields.io/badge/Allure-Reports-yellow.svg)](https://docs.qameta.io/allure/)

> A robust, scalable, and enterprise-grade test automation framework built with Selenium WebDriver, Python, and Pytest. Designed for production-ready web application testing with advanced features including multi-browser support, database validation, API testing, and comprehensive reporting.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [⚙️ Installation](#️-installation)
- [🚀 Quick Start](#-quick-start)
- [🎯 Usage Examples](#-usage-examples)
- [📊 Test Reports](#-test-reports)
- [🔧 Configuration](#-configuration)
- [🌐 Multi-Browser Support](#-multi-browser-support)
- [🤝 Contributing](#-contributing)
- [📞 Contact](#-contact)

---

## ✨ Key Features

### 🎯 Core Capabilities
- **Multi-Browser Support**: Chrome, Firefox, Edge, Safari (Desktop & Mobile)
- **Page Object Model (POM)**: Maintainable and scalable test architecture
- **Dynamic Locator Management**: JSON-based locator repository for easy maintenance
- **Parallel Test Execution**: Run tests concurrently to reduce execution time
- **Cross-Environment Testing**: Support for multiple environments (Dev, QA, Prod)

### 🔧 Advanced Features
- **Database Integration**: Direct MySQL/PostgreSQL database validation
- **API Testing**: Built-in API helper for REST API validation
- **AWS Integration**: S3, Lambda, and other AWS services support
- **Email Automation**: Automated email testing and validation
- **WebEx Integration**: Meeting automation and validation
- **CSV Data Management**: Data-driven testing with CSV support

### 📊 Reporting & Monitoring
- **Allure Reports**: Beautiful, interactive test reports with screenshots
- **Custom HTML Reports**: Styled HTML reports with detailed test results
- **Screenshot on Failure**: Automatic screenshot capture for failed tests
- **Logging**: Comprehensive logging for debugging and audit trails
- **Test Metrics**: Detailed execution metrics and trends

### 🛡️ Quality & Best Practices
- **Pytest Framework**: Industry-standard testing framework
- **Modular Design**: Reusable components and utilities
- **Configuration Management**: Centralized configuration for easy customization
- **Error Handling**: Robust exception handling and recovery mechanisms
- **CI/CD Ready**: Easily integrable with Jenkins, GitLab CI, GitHub Actions

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Test Layer (test_prod/)                  │
│         - Test Cases                                         │
│         - Test Data (JSON/CSV)                              │
│         - Fixtures & Configurations                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Page Layer (pages_prod/)                  │
│         - Page Objects                                       │
│         - Page Actions & Validations                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Locator Layer (locators/)                  │
│         - JSON-based Locator Repository                      │
│         - Dynamic Locator Management                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Helper Layer (helper/)                    │
│  - Selenium Helper    - API Helper      - Database Helper   │
│  - Email Helper       - AWS Helper      - WebEx Helper       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Layer (core/)                       │
│         - Driver Manager (Multi-browser)                     │
│         - Page Factory                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.8+ |
| **Automation Tool** | Selenium WebDriver 4.x |
| **Testing Framework** | Pytest |
| **Reporting** | Allure Reports, Custom HTML |
| **Database** | MySQL, PostgreSQL |
| **API Testing** | Requests Library |
| **Cloud Services** | AWS (S3, Lambda) |
| **Communication** | WebEx APIs, SMTP Email |
| **Data Management** | Pandas, CSV, JSON |
| **Version Control** | Git & GitHub |

---

## 📁 Project Structure

```
selenium_automation_project/
│
├── 📁 config.json                    # Main configuration file
│
├── 📁 core/                          # Core framework components
│   ├── __init__.py
│   ├── driver_manager.py             # Multi-browser driver management
│   └── page_factory.py               # Page factory pattern implementation
│
├── 📁 helper/                        # Utility helpers
│   ├── api_helper.py                 # REST API testing utilities
│   ├── aws_helper.py                 # AWS integration
│   ├── csv_helper.py                 # CSV data management
│   ├── email_helper.py               # Email automation
│   ├── login_helper.py               # Authentication helpers
│   ├── selenium_helper.py            # Selenium utilities
│   ├── 📁 database/                  # Database integration
│   │   ├── config.json
│   │   ├── db_connection.py
│   │   ├── db_helper.py
│   │   └── utils.py
│   └── 📁 webex/                     # WebEx integration
│       ├── config.json
│       ├── webex_connector.py
│       └── webex_helper.py
│
├── 📁 locators/                      # JSON-based locator repository
│   ├── NewsubductPage.json
│   └── OrdersPage.json
│
├── 📁 pages_prod/                    # Page Object Models
│   ├── home_page.py
│   └── new_subduct_page.py
│
├── 📁 test_prod/                     # Test cases
│   ├── conftest.py                   # Pytest configurations & fixtures
│   ├── pytest.ini                    # Pytest settings
│   ├── test_active_group_dateTimeCheck.py
│   └── 📁 data/                      # Test data
│       └── active_group_dateTimeCheck.json
│
├── 📁 utility/                       # Common utilities
│   ├── frsutility.py
│   ├── utils_parser.py
│   ├── utils.py
│   └── 📁 data/
│       └── override_sitemodule.json
│
└── 📁 report/                        # Test reports
    ├── 📁 allure/                    # Allure reports
    ├── 📁 screenshot/                # Test screenshots
    └── 📁 assets/                    # Report styling
        └── style.css
```

---

## ⚙️ Installation

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- **Git** for version control
- **Chrome/Firefox/Edge** browser installed
- **WebDriver** executables in system PATH

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/selenium_automation_project.git
cd selenium_automation_project
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
```
selenium>=4.0.0
pytest>=7.0.0
pytest-xdist>=2.5.0
allure-pytest>=2.9.0
requests>=2.27.0
pandas>=1.4.0
mysql-connector-python>=8.0.0
boto3>=1.20.0
webexteamssdk>=1.6.0
python-interface>=1.6.0
msedge-selenium-tools>=3.141.4
```

### Step 4: Configure WebDrivers

Download and add to system PATH:
- [ChromeDriver](https://chromedriver.chromium.org/)
- [GeckoDriver (Firefox)](https://github.com/mozilla/geckodriver/releases)
- [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

---

## 🚀 Quick Start

### 1. Update Configuration

Edit `config.json` with your environment settings:

```json
{
    "build_url": "https://your-application-url.com",
    "countries": ["US", "GB", "AU"],
    "automation_email": {
        "email_id": "your-email@example.com",
        "email_app_password": "your-app-password"
    }
}
```

### 2. Run Your First Test

**Single Test Execution:**
```bash
pytest test_prod/test_active_group_dateTimeCheck.py -v
```

**Run with Specific Browser:**
```bash
pytest test_prod/ --browser_name=chrome -v
```

**Parallel Execution:**
```bash
pytest test_prod/ -n 4 -v
```

### 3. Generate Allure Report

```bash
# Run tests with Allure
pytest test_prod/ --alluredir=report/allure

# Generate and open report
allure serve report/allure
```

---

## 🎯 Usage Examples

### Example 1: Basic Test Execution

```python
import pytest
from pages_prod.home_page import HomePage

class TestHomePage:
    
    @pytest.fixture
    def setup(self):
        self.home_page = HomePage(pytest.driver)
    
    def test_page_title(self, setup):
        """Verify home page title"""
        assert self.home_page.get_page_title() == "Expected Title"
    
    def test_login_functionality(self, setup):
        """Test user login"""
        self.home_page.login("user@example.com", "password123")
        assert self.home_page.is_logged_in()
```

### Example 2: Data-Driven Testing

```python
import pytest
import json

# Load test data
with open('test_prod/data/test_data.json') as f:
    test_data = json.load(f)

@pytest.mark.parametrize("user_data", test_data['users'])
def test_multiple_users(user_data):
    """Test with multiple user datasets"""
    # Your test logic here
    pass
```

### Example 3: Database Validation

```python
from helper.database import db_helper

def test_user_data_in_database():
    """Validate data in database"""
    query = "SELECT * FROM users WHERE email = 'test@example.com'"
    result = db_helper.get_prod_data(query)
    assert len(result) > 0
```

### Example 4: API Testing

```python
from helper.api_helper import APIHelper

def test_api_endpoint():
    """Test REST API endpoint"""
    api = APIHelper()
    response = api.get("https://api.example.com/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

---

## 📊 Test Reports

### Allure Reports

Generate beautiful, interactive reports with Allure:

```bash
# Run tests with Allure
pytest --alluredir=report/allure

# View report
allure serve report/allure
```

**Features:**
- ✅ Test execution timeline
- ✅ Test categorization
- ✅ Screenshots on failure
- ✅ Historical trends
- ✅ Flaky test detection

### Custom HTML Reports

```bash
pytest --html=report/report.html --self-contained-html
```

### Screenshots

Failed tests automatically capture screenshots saved to `report/screenshot/`

---

## 🔧 Configuration

### Browser Configuration

Supported browsers can be specified via command line:

```bash
# Chrome (default)
pytest --browser_name=chrome

# Firefox
pytest --browser_name=firefox

# Edge
pytest --browser_name=edge

# Safari
pytest --browser_name=safari

# Mobile Chrome
pytest --browser_name=m_chrome

# Mobile Safari
pytest --browser_name=m_safari
```

### Environment Configuration

Modify `config.json` for different environments:

```json
{
    "product": "Website",
    "build_name": "master",
    "build_url": "http://your-app-url.com",
    "countries": ["IN", "US", "GB", "AU"],
    "superadmin": {
        "email": "admin@example.com",
        "password": "secure_password"
    }
}
```

### Database Configuration

Configure database connections in `helper/database/config.json`:

```json
{
    "host": "localhost",
    "user": "db_user",
    "password": "db_password",
    "database": "your_database"
}
```

---

## 🌐 Multi-Browser Support

The framework supports execution across multiple browsers:

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ❌ |
| Edge | ✅ | ❌ |
| Safari | ✅ | ✅ |

**Example:**
```bash
# Run tests on multiple browsers sequentially
pytest --browser_name=chrome
pytest --browser_name=firefox
pytest --browser_name=edge
```

---

## 🎓 Best Practices Implemented

1. **Page Object Model (POM)**: Separation of test logic from page structure
2. **DRY Principle**: Reusable components and utilities
3. **Data-Driven Testing**: External test data management
4. **Explicit Waits**: Robust synchronization mechanisms
5. **Exception Handling**: Graceful error management
6. **Logging**: Comprehensive logging for debugging
7. **Modular Design**: Independent, maintainable modules
8. **Version Control**: Git-based version management
9. **Configuration Management**: Centralized configuration
10. **Continuous Integration**: CI/CD ready architecture

---

## 📈 Test Execution Strategies

### Smoke Testing
```bash
pytest -m smoke -v
```

### Regression Testing
```bash
pytest test_prod/ -v
```

### Parallel Execution
```bash
pytest -n auto -v
```

### Specific Test Module
```bash
pytest test_prod/test_active_group_dateTimeCheck.py -v
```

### With Test Filters
```bash
pytest --test_filter="priority:high" -v
```

---

## 🔍 Debugging Tips

### Run Tests in Debug Mode
```bash
pytest -v -s test_prod/
```

### Run Single Test
```bash
pytest test_prod/test_file.py::TestClass::test_method -v
```

### View Full Traceback
```bash
pytest --tb=long
```

### Capture Screenshots
Screenshots are automatically captured on failure in `report/screenshot/`

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to classes and methods
- Write unit tests for new features
- Update documentation as needed

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author & Contact

**Your Name**
- 🌐 **GitHub**: [@yourusername](https://github.com/yourusername)
- 💼 **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)
- 📧 **Email**: your.email@example.com
- 🌐 **Portfolio**: [yourportfolio.com](https://yourportfolio.com)

---

## 🏆 Key Achievements

- ✅ **Enterprise-Grade Architecture**: Production-ready framework design
- ✅ **Multi-Browser Support**: Cross-browser compatibility
- ✅ **Database Integration**: Direct DB validation capabilities
- ✅ **API Testing**: Comprehensive REST API testing
- ✅ **Cloud Integration**: AWS services support
- ✅ **Advanced Reporting**: Allure & HTML reports
- ✅ **CI/CD Ready**: Easy integration with CI/CD pipelines

---

## 📚 Additional Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Allure Reports](https://docs.qameta.io/allure/)
- [Page Object Model Pattern](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

## 🙏 Acknowledgments

- Selenium WebDriver community
- Pytest framework contributors
- Allure reporting team
- Open source community

---

<div align="center">

### ⭐ If you find this project useful, please consider giving it a star! ⭐

**Made with ❤️ and ☕ by a passionate Test Automation Engineer**

</div>
