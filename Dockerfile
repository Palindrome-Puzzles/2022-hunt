FROM gcr.io/google-appengine/python

# Create a virtualenv for dependencies. This isolates these packages from
# system-level packages.
#
# Note: some of the hunt website depends on Python 3.9, but none of the backend
# server does. (It's mostly for iterating puzzle data files.) If this becomes a
# problem, then we can customize the docker image further.
RUN virtualenv /env -p python3.7

# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copy the application's requirements and run pip to install all
# dependencies into the virtualenv. requirements.txt will load some child
# requirements files, so make sure they're accessible.
ADD requirements /app/requirements
RUN pip install -r /app/requirements/release_gcloud.txt

# Add the application source code. No need for static files, so let's reduce our
# Docker image size.
ADD hunt /app/hunt
ADD spoilr /app/spoilr

# Run an ASGI server to serve the application. daphne must be declared as
# a dependency in requirements.txt.
CMD daphne -b 0.0.0.0 -p $PORT hunt.deploy.asgi:application
