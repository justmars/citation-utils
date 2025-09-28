set dotenv-load

# create .env file from example
dumpenv:
  op inject -i env.example -o .env

# upload to pypi
publish:
  uv build && \
  uv publish --token $PYPI_TOKEN
