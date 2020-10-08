# Create builder step
# pull official base image and use it as builder
FROM r-base:4.0.2 AS builder

WORKDIR /src

# install required debian packages to make R packages work
COPY setup ./setup
COPY requirements_debian.txt .
RUN cat requirements_debian.txt | xargs ./setup/install_debian_packages.sh

# install required R packages for the worker.
# these are sectioned as seen here so we can cache compiled code
# NOTE: add new packages to the END of this list. this makes sure
# previously installed packages don't get recompiled for no reason.
RUN Rscript setup/install_or_die.r devtools
RUN Rscript setup/install_or_die.r github rexyai/RestRserve
RUN Rscript setup/install_or_die.r languageserver

# ---------------------------------------------------
# PRODUCTION BUILD
# ---------------------------------------------------
FROM builder AS prod

# add app
COPY src ./

# start app
CMD ["Rscript", "work.r"]

# ---------------------------------------------------
# DEVELOPMENT BUILD
# ---------------------------------------------------
FROM builder AS dev

# install Radian for interactive R shell
# also install watchdog to automatically restart
# when source files change
RUN pip install -U jedi radian PyYAML watchdog[watchmedo]

WORKDIR /r
CMD watchmedo auto-restart --directory=./src/ --pattern=* --recursive -- Rscript src/work.r