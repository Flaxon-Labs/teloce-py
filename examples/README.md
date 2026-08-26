# Teloce examples

Every example is intended to be copied into a new project. From the repository root, install the example's requirements, run its build command, and start the corresponding Python server.

| Example | Demonstrates | Start |
| --- | --- | --- |
| `basic` | Flask task board, imported `.vel` component | `python app.py` |
| `flask` | Flask host and health API | `python app.py` |
| `flask-chat` | Flask JSON chat API and reactive UI | `python app.py` |
| `fastapi-cms` | FastAPI page CRUD API | `python app.py` |
| `django-scanner` | Django defensive scanner UI | `python build.py`, then `python manage.py runserver` |
| `flaxon` | Flaxon + Jinax + `.vel` | `python build.py`, then `python -m flaxon run app:app --reload` |
| `flaxon-network` | Flaxon JSON and WebSocket routes | `python build.py`, then `python -m flaxon run app:app --reload` |

Run commands from the example directory. The examples use local in-memory data where appropriate; replace that storage with your production database and security controls before deployment.
