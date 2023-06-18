from mysite.celery import app


@app.task
def messages_to_db():
    return 2+2
