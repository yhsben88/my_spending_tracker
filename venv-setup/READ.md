# How to Set Up Virtual Environment in Python with Installations

This guide explains how to create and use a **Python virtual environment** for this project.  
A virtual environment keeps dependencies isolated so they don’t interfere with other Python projects on your system.

---

## 1. Open the Project in VSCode

1. Open **VSCode**.
2. Go to **File → Open Folder**.
3. Select the folder where your Python files (e.g., `load.py`) are located.

---

## 2. Create a Virtual Environment

Open the terminal inside VSCode and run:

```bash
# Create a virtual environment named venv
python3 -m venv venv
```

This will create a folder called venv/ inside your project directory.

## 3. Activate the Virtual Environment

Activate the environment so Python and pip use this project’s interpreter.

macOS/Linux:

```bash
# Copy code
source venv/bin/activate
```

Windows (PowerShell):

```bash
# Copy code
venv\Scripts\Activate.ps1
```

When activated, your terminal prompt will look like:

```ruby
# Copy code
(venv) yourname@computer:~/project-folder$
```

## 4. Install Required Packages

With the virtual environment active, install dependencies locally:

```bash
# Copy code
pip install psycopg2-binary
```

(You can add more packages here if your project needs them.)

## 5. Save Dependencies (Optional but Recommended)

To export your installed packages into a requirements.txt file:

```bash
# Copy code
pip freeze > requirements.txt
```

Later, anyone can recreate the same environment with:

```bash
# Copy code
pip install -r requirements.txt
```

## 6. Select Interpreter in VSCode

Press Ctrl+Shift+P (or Cmd+Shift+P on Mac).

Type and select Python: Select Interpreter.

Choose the interpreter inside your project’s venv folder.

Now VSCode will run Python using this isolated environment.

✅ You are now ready to run your project inside a clean, project-specific Python environment.
