
# **Autonomous BDD Pipeline 🚀**  

## **Overview**  
The **Autonomous BDD Pipeline** is an automated workflow that ensures business logic validation and bug fixing using AI-generated tests. It continuously monitors code changes, evaluates compliance with business requirements, generates test scenarios, and fixes issues dynamically.  

This pipeline integrates **GitHub Actions** to streamline **test case generation, business logic validation, debugging, and automated PR creation**.  

---

## **🛠️ Key Features**  
✔ **AI-Powered Business Logic Validation** - Evaluates code compliance against business requirements  
✔ **Automatic Test Generation** - Generates BDD (Gherkin) test cases dynamically  
✔ **Self-Healing Debugging** - Fixes detected issues in a loop until tests pass  
✔ **GitHub Actions Integration** - Runs seamlessly on every code update  
✔ **Automated Pull Requests** - Uses `peter-evans/create-pull-request` to propose changes  

---

## **📂 Project Structure**  
```
.
├── .github/
│   ├── workflows/
│   │   ├── auto_bdd.yml # GitHub Actions workflow
├── debuggers/
│   ├── debugger_v2.py # script that runs generated tests and iteratively fix failed tests (if any)
├── requirements
│   ├── brd.md # Business Requirement Document (text-based)
├── scripts/
│   ├── generate_report/
│   │   ├── generate_report.py  # Generates business requirements compliance report
│   ├── generate_tests/
│   │   ├── test_orchestrator.py  # Generates test scenarios
├── src/implementation/
│   ├── [sample_code]  # sample code to be evaluated
├── test-config
│   ├── environment.py
├── README.md
└── requirements.txt
```

---

## **⚡ How It Works (GitHub Actions Workflow)**  
The pipeline runs when changes are pushed to `src/` or `requirements/`.  

### **1️⃣ Generate Requirements Compliance Report**
- Extracts business requirements  
- Analyzes the codebase for compliance  

```bash
python scripts/generate_report/generate_report.py
```

### **2️⃣ Generate Test Scenarios**
- Generates feature files and step definitions  
- Uses BDD (Gherkin) format for business logic validation  

```bash
python scripts/generate_tests/test_orchestrator.py --generate
```

### **3️⃣ Execute Business Validation & Debugging**
- Runs generated tests  
- Identifies and fixes business logic errors automatically  

```bash
python debuggers/debugger_v2.py
```

---

## **🛠️ Setup & Installation**
### **📌 Prerequisites**
- **Python 3.8+**  
- **GitHub Actions enabled**  
- **pip dependencies installed**  

```bash
pip install -r scripts/requirements.txt
```

### **🚀 Running Locally**
If you want to test locally:  
```bash
python scripts/generate_report/generate_report.py
python scripts/generate_tests/test_orchestrator.py --generate
python scripts/debuggers/debugger_v2.py
```

---

## **📌 Contribution Guidelines**
1. Fork the repository  
2. Create a feature branch (`feature-xyz`)  
3. Make changes and test locally  
4. Push changes and let the pipeline create a PR  

---

## **📜 License**
This project is licensed under **MIT License**.  
