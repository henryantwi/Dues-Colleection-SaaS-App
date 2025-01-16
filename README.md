# DUESFLOW

A comprehensive Django-based SaaS application for managing dues collection.


## Key Features

- Admin authentication and authorization
- Payment processing
- Administrative dashboards
- Student management
- Responsive design


## Getting Started

1. Clone this repository:
    ```sh
    git clone https://github.com/henryantwi/Dues-Colleection-SaaS-App.git
    ```
2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
3. Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
    ```sh
    pip install -r src/requirements.txt
    ```
5. Run migrations:
    ```sh
    python src/manage.py migrate
    ```
6. Start the development server:
    ```sh
    python src/manage.py runserver
    ```

## Project Structure

```
dues_collection_saas_app/
├── src/
│   ├── a_home/
│   ├── administrators/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── payments/
│   ├── students/
│   ├── templates/
│   ├── static/
│   ├── media/
│   ├── manage.py
│   └── requirements.txt
├── .gitignore
├── .vscode/
├── LICENSE
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/henryantwi/Dues-Colleection-SaaS-App/blob/main/LICENSE) file for details.
