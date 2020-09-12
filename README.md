# Artbiogs - Artist CV Parser

> A web application that uses AI/ML to extract all Artist's Exhibition details from a CV.

![](screenshot.gif)

Watch a demo or view how the final parsed cv.

# Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# Development

You require `python3`, `google-chrome` and `wkhtmltopdf` installed. First clone the repository and change directory to the project folder. Then create a virtual environment:

```bash
python3 -m virtualenv .venv
source .venv/bin/activate
```

Now, run the following:

```bash
python setup.py develop
```

This installs all the necessary dependencies to run the python project. Now, lets launch the web application by running:

```bash
python web/app.py
```

You can now view the application at [http://localhost:5000](localhost:5000)

# Technologies

Web Stack:

- **Python** - Stack core
- **Flask + SocketIO** - Web Server
- **Bulma** - CSS Framework
- **Selenium** - Remote Webpage to PDF conversion
- **wkhtmltopdf** - HTML to PDF generation.

AI/ML Cloud Technologies used:

- **AWS S3** - File Storage
- **AWS Textract** - Text extraction
- **AWS Comprehend** - Exhibition Title
