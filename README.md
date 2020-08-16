# dvcyaml-schema

[JSON Schema](https://json-schema.org/) for [`dvc.yaml`](https://dvc.org/doc/user-guide/dvc-files-and-directories#dvcyaml-file) file format.

It can provide better autocompletion, validation, and linting for `dvc.yaml` files.

## Usage

### JSON Schema

Use the following URL to obtain the latest JSON schema for `dvc.yaml`:

```
https://raw.githubusercontent.com/iterative/dvcyaml-schema/master/schema.json
```

#### Visual Studio Code (with [YAML Extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)):

Add the following to your settings:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/iterative/dvcyaml-schema/master/schema.json":
        "dvc.yaml"
  }
}
```

#### JetBrain IDEs (PyCharm, Intellij IDEA, et al.)

Follow [this](https://www.jetbrains.com/help/ruby/yaml.html#remote_json) instruction.

### Important Files:

1. **[schema.json](schema.json)**
2. [gen.py](gen.py)
3. [examples](examples)
4. [tests.py](tests.py)

### Contributing

1. Open [gen.py](gen.py) and make some adjustments.
2. Generate schema and run tests:
    ```console
    $ dvc repro
    ```
3. Send us a pull request. 🤗

> Make sure to create a virtual environment before, and `dvc` is installed.
