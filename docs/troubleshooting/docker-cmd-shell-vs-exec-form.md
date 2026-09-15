# Docker CMD Was Parsed As Shell Form Instead Of Exec Form

## Problem

While moving Phoenix from the Flask development server to Gunicorn, the Dockerfile was changed to run Gunicorn directly.

The intended command was an exec-form JSON CMD:

    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

However, the Docker build produced this warning:

    JSONArgsRecommended: JSON arguments recommended for CMD to prevent unintended behavior related to OS signals

At first glance, the Dockerfile already appeared to use JSON form.

## Investigation

The built image was inspected with:

    docker image inspect phoenix-app:gunicorn-test \
      --format 'CMD={{json .Config.Cmd}} ENTRYPOINT={{json .Config.Entrypoint}}'

The result showed:

    CMD=["/bin/sh","-c","[\"gunicorn\", ..."]

This proved that Docker had not parsed the CMD as JSON exec form.

Instead, Docker stored it as a shell command executed through:

    /bin/sh -c

The Dockerfile line was then inspected directly:

    sed -n '14p' Dockerfile | cat -A

A Python JSON parser was also used to validate the CMD payload.

The parser returned:

    INVALID JSON: Expecting ',' delimiter

The final closing bracket was missing from the CMD instruction.

## Root Cause

The Dockerfile contained an incomplete JSON array.

The command ended with:

    "app:app"

instead of:

    "app:app"]

Because the JSON was invalid, Docker treated the instruction as shell form.

This caused the image to execute through:

    /bin/sh -c

instead of starting Gunicorn directly.

## Why This Matters

For long-running container processes, exec form is preferred because the application process receives Unix signals directly.

With shell form:

    Docker
      ->
    /bin/sh
      ->
    Gunicorn

With exec form:

    Docker
      ->
    Gunicorn

This is especially important for signals such as:

    SIGTERM

which Docker sends during:

    docker stop

If Gunicorn is PID 1 and receives the signal directly, it can gracefully stop its workers before exiting.

## Solution

The Dockerfile CMD was corrected to valid JSON:

    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

The image was rebuilt.

The resulting image configuration was verified again:

    docker image inspect phoenix-app:gunicorn-test \
      --format 'CMD={{json .Config.Cmd}} ENTRYPOINT={{json .Config.Entrypoint}}'

The result became:

    CMD=["gunicorn","--bind","0.0.0.0:5000","--workers","1","--threads","4","--timeout","30","--access-logfile","-","--error-logfile","-","app:app"]

There was no:

    /bin/sh -c

in the command path.

## Verification

A Gunicorn container was started from the corrected image.

Its startup logs showed:

    Starting gunicorn 26.2.0
    Listening at: http://0.0.0.0:5000
    Using worker: gthread
    Booting worker

The container was then stopped using:

    docker stop -t 10 phoenix-gunicorn-test

Gunicorn logged:

    Handling signal: term
    Worker exiting
    Shutting down: Master

This confirmed that Gunicorn received the termination signal and performed a graceful shutdown.

## Lesson Learned

A Dockerfile instruction can look like JSON while still being invalid JSON.

Do not rely only on visual inspection.

When Docker reports a JSON-form warning, inspect the built image itself:

    docker image inspect

and verify whether the command starts directly or through:

    /bin/sh -c

For production container processes, valid exec-form CMD improves signal handling and graceful shutdown behavior.
