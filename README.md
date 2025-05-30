# PDF Generator

A Python application to generate multiple PDF files with custom text, watermarks, and size control.

## Features

- Generate multiple PDF files in bulk
- Customize number of pages per PDF
- Add custom text to each page
- Insert watermark images (PNG/JPG)
- Control text placement (default or custom coordinates)
- Choose between color or black & white watermarks
- Set desired PDF file size (in KB)
- Progress bar to track generation
- Single instance enforcement (prevents multiple runs)


## Screenshots

![App GUI](https://www.managexindia.com/GUI.png)


## System Requirements

- Python 3.6 or higher
- Windows, macOS, or Linux

## Installation

### 1. Create and Activate Virtual Environment

#### Windows:
```cmd
python -m venv pdf
pdf\Scripts\activate
```

#### macOS/Linux:
```cmd
python3 -m venv pdf
source pdf/bin/activate
```

### 2. Install Dependencies
```cmd
pip install -r requirements.txt
```
### 3. Run the application:
```cmd
python PDF_Generator_v2.1.py
```

### 4. Fill in the fields:
- Select output folder

- Enter number of pages per PDF

- Enter number of PDFs to generate

- Add custom text (optional)

- Select watermark image (optional)

- Choose text alignment (default or custom coordinates) (optional)

- Select watermark type (color or black & white) (optional)

- Set desired PDF size in KB (optional)

###### Click "Generate PDFs" button

### Notes

- Maximum allowed pages/PDFs: 100,000

- Application requires admin privileges on Windows

- Only one instance can run at a time

- Default text position is Center of the PDF coordinates

- Watermark transparency is set to 20%

### Version
Current version: 2.1
