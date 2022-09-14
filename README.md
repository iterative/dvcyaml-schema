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

If you have installed YAML extension, it'll automatically fetch the latest dvcyaml-schema, and
should work out of the box.

But you can specify explicitly as well by adding following contents to your settings:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/iterative/dvcyaml-schema/master/schema.json":
        "dvc.yaml"
  }
}
```

You can also specify custom URL or path instead for debugging/testing purposes.

#### JetBrain IDEs (PyCharm, Intellij IDEA, et al.)

Follow [this](https://www.jetbrains.com/help/ruby/yaml.html#remote_json) instruction.

### Important Files:

1. **[schema.json](schema.json)**
2. [gen.py](gen.py)
3. [examples](examples)
4. [tests.py](tests.py)

### Contributing

1. Setup a virtual environment, and install required dependencies from [`requirements.txt`](requirements.txt).

    ```console
    $ python -m venv venv
    $ source venv/bin/activate
    $ python -m pip install -U wheel pip
    $ python -m pip install -r requirements.txt
    ```
    Also make sure that `dvc` is installed.
2. Open [gen.py](gen.py) and make some adjustments, and generate schema using:

    ```console
    $ python gen.py > schema.json
    ```
3. (Optional) Add [valid](examples/valid) and [invalid](examples/invalid) yaml examples.

4. Run tests to validate compatibility.
    ```console
    $ python -m pytest
    ```

5. Send us a pull request. 🤗
