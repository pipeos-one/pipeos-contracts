# Pipeline Smart Contracts

Not production ready.

## Development

Clone this repo:

```
git clone https://github.com/pipeos-one/pipeos-contracts.git
cd pipeos-contracts
```

Use a virtual environment:

```
virtualenv -p python3 env
. env/bin/activate
```

Install development dependencies:

```
make
```

### Linting

```
make lint
```

### Testing

```
pytest
pytest pipeos_contracts/tests/test_proxy.py
```
