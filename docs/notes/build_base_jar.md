# Notes on progress with building PyEvolve

## Dependencies

- Jython3: installed successfully
- ComBy: Docker image installs it for itself
- Wala.ml: problems!!!

### Wala

It seems that the version which PyEvolve uses is not the same as in the master branch of wala.ml.

The problem with that is: we don't know which version to use.

Also, some tests didn't run successfully when building wala. I don't know it it's a local build issue with some inconsistent
dependencies, or just a bug. An issue mentioned testing inconsistencies while it works in production.
